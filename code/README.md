# Discord Remote Power-On Bot

A lightweight Discord bot for a Raspberry Pi that listens for a
command in a private channel and pulses GPIO to remotely power on a
device (e.g. simulating a momentary press of a PC's power-button header).

Connects via Discord's Gateway API — an **outbound-only** connection, same
as running the Discord desktop app. No port forwarding, no public IP, no
inbound exposure of the Pi to the internet.

## Commands

- `?on` — pulses GPIO14 high for 0.5s then low. Subject to a 30s cooldown;
  spamming it just gets you a "still on cooldown" reply, no re-trigger.
- `?help` — explains the bot and lists commands. Not subject to cooldown.

Both the command prefix (`?`) and all the numbers above are configurable in
`config.py`.

## Discord Developer Portal setup

1. Go to https://discord.com/developers/applications → **New Application**.
2. **Bot** tab → Add Bot → click **Reset Token** → copy it. This goes into
   `config.py` as `DISCORD_TOKEN`.
3. Still on the **Bot** tab, enable **Message Content Intent** (a
   privileged intent — required for the bot to read message text at all).
4. **OAuth2 → URL Generator**:
   - Scopes: `bot`
   - Bot permissions: `Send Messages`, `Read Message History`, `View Channel`
   - Open the generated URL and invite the bot to your server.
5. In Discord: **Settings → Advanced → Developer Mode** (enable it), then
   right-click your private channel → **Copy Channel ID**. This goes into
   `config.py` as `ALLOWED_CHANNEL_ID`.

## Pi-side setup

```bash
sudo apt update
sudo apt install -y python3-venv python3-lgpio

cd /home/raspi/remote-powerOn   # wherever you deploy this project
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install -r requirements.txt
```

`--system-site-packages` lets the venv see the apt-installed `python3-lgpio`
(a prebuilt package — more reliable on a Pi 3 than letting pip try to
compile `lgpio` from source).

Create `config.py` in the project root (see the template already in this
repo) and fill in your real `DISCORD_TOKEN` and `ALLOWED_CHANNEL_ID`.

## Manual test run

```bash
source venv/bin/activate
python3 main.py
```

You should see `Logged in as <YourBotName> (id=...)` printed — this
confirms the token, intents, and Gateway connection all work. Leave it
running and test `?help`/`?on` from Discord (see Verification below)
before installing it as a service.

## Install as a systemd service

The included `discord-gpio-bot.service` assumes the project lives at
`/home/pi/remote-powerOn` and runs as user `pi`. **Edit `User=`,
`WorkingDirectory=`, and `ExecStart=` first if your username or deploy path
differs.**

```bash
sudo cp discord-gpio-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now discord-gpio-bot.service
sudo systemctl status discord-gpio-bot
journalctl -u discord-gpio-bot -f
```

No extra group setup should be needed — the default `pi` user is already
in the `gpio` group on stock Raspberry Pi OS (verify with `groups pi`). If
running as a different user, add it: `sudo usermod -aG gpio <user>` and
log out/in (or reboot).