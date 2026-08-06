# NIVYT Backup Copilot

**Automatic Minecraft Bedrock world backups for Windows — zero setup, one-click recovery.**

NIVYT Backup Copilot runs quietly in the background, detects the moment Minecraft Bedrock closes, and saves a timestamped backup of your world automatically. If a world ever gets corrupted, deleted, or messed up by a bad update, you can restore it in one click — no manual file copying, no digging through AppData folders.

## Features

- **Automatic detection** — backs up the instant Minecraft Bedrock closes, no commands or buttons needed
- **Timestamped backups** — every backup is saved with a clear date/time so you can find the version you want
- **One-click restore** — roll back to any previous backup instantly
- **Discord backup logs** — optional Discord bot integration posts a log every time a backup runs, so you always know it's working
- **Lightweight** — runs silently in the background with minimal resource use

## Installation

1. Download the latest installer: [`NIVYT_Backup_Copilot_Setup_v2.0.exe`](./NIVYT_Backup_Copilot_Setup_v2.0.exe)
2. Run the installer and follow the prompts
3. Launch NIVYT Backup Copilot — it will run in the background automatically
4. (Optional) Add your Discord webhook URL in settings to get backup notifications

## How it works

NIVYT Backup Copilot watches for the Minecraft Bedrock process. When it detects the game has closed, it copies your active world save to a local backup folder, tagged with the date and time. Old backups can be configured to rotate automatically so you don't run out of disk space.

## FAQ

**Does this work with Minecraft Java Edition?**
No — this tool is built specifically for Minecraft Bedrock on Windows.

**Where are backups stored?**
Locally on your machine, in a configurable backup folder (default location shown in Settings).

**Is this safe to run?**
[Add details here: what the exe does, what permissions it needs, whether it's code-signed, and a link to source code if/when available.]

## License