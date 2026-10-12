<div align="center">
  <img src="logo.ico" alt="BedrockCapsule Logo" width="100" />
  <h1>BedrockCapsule v2.3</h1>
  <p>Automated world backup, encryption & rollback for Minecraft Bedrock on Windows.</p>

  <p>
    <a href="RELEASE_NOTES.md"><img src="https://img.shields.io/badge/Release_Notes-v2.3-orange?style=for-the-badge" alt="Release Notes" /></a>
    <a href="https://github.com/NIVYT/BedrockCapsule/releases"><img src="https://img.shields.io/badge/Version-v2.3-0ba071?style=for-the-badge&logo=github" alt="Version 2.3" /></a>
    <a href="https://discord.com"><img src="https://img.shields.io/badge/Discord-Integration-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord Integration" /></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License: MIT" /></a>
  </p>
</div>

---

BedrockCapsule monitors your Minecraft sessions in the background and automatically captures timestamped backups the moment you close the game. Supports rollback, `.mcworld` export, optional encryption, Discord notifications, and a system tray daemon.

---

## Getting Started

**Requirements:** Windows 10/11 · Minecraft Bedrock (UWP) · Python 3.10+ *(source only)* · Edge WebView2 Runtime

**Install:** Download `BedrockCapsule_Setup_v2.3.exe` from [Releases](https://github.com/NIVYT/BedrockCapsule/releases) and run the setup wizard.

**Run from source:**
```bash
git clone https://github.com/NIVYT/BedrockCapsule.git
cd BedrockCapsule
pip install -r requirements.txt
python main.py
```

**Build:**
```cmd
.\build.bat
```
Output: `dist/BedrockCapsule_2.3.exe` · `Output/BedrockCapsule_Setup_v2.3.exe`

---

## Configuration

Settings stored at `%APPDATA%\BedrockCapsule\config.json`

| Setting | Default | Description |
| :--- | :--- | :--- |
| `max_backups` | `5` | Snapshots kept per world before auto-pruning |
| `theme` | `"dark"` | UI theme (`"dark"` or `"light"`) |
| `encryption_key` | `""` | Optional XOR passkey for capsule encryption |
| `custom_world_dir` | `""` | Custom world folder path (overrides UWP default) |

---

## License

MIT — see `LICENSE` for details.

<div align="center">
  <p>Crafted by <strong>NIVYT</strong> for the Minecraft Bedrock Community.</p>
</div>
