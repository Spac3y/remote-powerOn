# remote-powerOn

Remotely power on a PC (or any device with a momentary power-button header)
from Discord, using a Raspberry Pi and a small custom PCB.

Send `?on` in a private Discord channel and a Raspberry Pi pulses a GPIO pin,
which drives a transistor-switched relay/output on the custom board to
simulate a momentary press of the target device's power-button header. The
bot connects outbound-only via Discord's Gateway API, so there's no port
forwarding or public IP exposure of the Pi.

## Structure

- **`code/`** — the Discord bot (Python, `discord.py` + `gpiozero`) that
  runs on the Pi and drives the GPIO pin. See `code/README.md` for setup,
  Discord bot configuration, and systemd install instructions.
- **`kicad/`** — KiCad schematic/PCB design for the driver board that sits
  between the Pi's GPIO pin and the target device's power-button header. See
  `kicad/changes.md` for the design change log.
