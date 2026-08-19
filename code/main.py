import asyncio
import time

import discord
from gpiozero import DigitalOutputDevice

import config

# --- GPIO -------------------------------------------------------------
pin = DigitalOutputDevice(config.GPIO_PIN, initial_value=False)

# --- Debounce state -----------------------------------------------------
# time.monotonic() (not wall-clock) so an NTP jump can't shorten/lengthen
# the cooldown. Set *before* the pulse sleep, and the lock held across it,
# so an overlapping ?on can't double-trigger or see a stale timestamp.
_last_trigger = 0.0
_trigger_lock = asyncio.Lock()

HELP_TEXT = (
    "**Remote Power-On Bot**\n"
    f"`{config.COMMAND_PREFIX}on` — pulses GPIO{config.GPIO_PIN} high for "
    f"{config.PULSE_SECONDS}s to simulate a momentary power-button press "
    f"(cooldown: {config.DEBOUNCE_SECONDS}s between triggers).\n"
    f"`{config.COMMAND_PREFIX}help` — shows this message."
)

# --- Discord client: narrow intents, no member/message cache ------------
intents = discord.Intents.none()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True

client = discord.Client(
    intents=intents,
    chunk_guilds_at_startup=False,
    max_messages=None,
)


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (id={client.user.id})")


@client.event
async def on_message(message: discord.Message):
    global _last_trigger

    if message.author.bot:
        return
    if message.channel.id != config.ALLOWED_CHANNEL_ID:
        return
    if config.ALLOWED_USER_ID is not None and message.author.id != config.ALLOWED_USER_ID:
        return

    content = message.content.strip()

    if content == f"{config.COMMAND_PREFIX}help":
        await message.channel.send(HELP_TEXT)
        return

    if content == f"{config.COMMAND_PREFIX}on":
        async with _trigger_lock:
            now = time.monotonic()
            elapsed = now - _last_trigger
            if elapsed < config.DEBOUNCE_SECONDS:
                remaining = config.DEBOUNCE_SECONDS - elapsed
                await message.channel.send(
                    f"On cooldown — try again in {remaining:.0f}s."
                )
                return
            _last_trigger = now
            pin.on()
            await asyncio.sleep(config.PULSE_SECONDS)
            pin.off()
        await message.channel.send(
            f"Pulsed GPIO{config.GPIO_PIN} for {config.PULSE_SECONDS}s."
        )


client.run(config.DISCORD_TOKEN)
