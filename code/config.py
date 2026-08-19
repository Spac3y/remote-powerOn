# config.py — DO NOT COMMIT. Fill in your own values before running main.py.
# This file is listed in .gitignore.

# Bot token from the Discord Developer Portal (Bot tab -> Reset Token / Copy).
DISCORD_TOKEN = ""

# ID of the private channel the bot should listen in.
# (Discord: enable Developer Mode in Settings -> Advanced, then
#  right-click the channel -> Copy Channel ID.)
ALLOWED_CHANNEL_ID = 1234

# Optional: restrict to a single Discord user ID for extra safety.
# Set to None to disable this check (channel-ID gating alone is usually
# enough for a single-person private channel).
ALLOWED_USER_ID = None

# BCM pin number the relay/transistor is wired to.
# Default is GPIO14 (physical pin 8) — see README for the UART caution
# before wiring anything to it.
GPIO_PIN = 14

# How long (seconds) to hold the pin high — simulates a momentary button press.
PULSE_SECONDS = 0.5

# Minimum seconds required between two successful ?on triggers.
DEBOUNCE_SECONDS = 30

# Command prefix. Change to "/" or anything else if you like.
COMMAND_PREFIX = "/"
