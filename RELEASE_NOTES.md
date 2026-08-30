# 📦 BedrockCapsule — Release Notes & Changelog

All notable changes, architectural updates, and version histories for **BedrockCapsule** are documented in this file.

---

## 🚀 Version 2.1 — The "BedrockCapsule" Milestone Release

### 📢 Major Rebranding: *NIVYT Backup Copilot* ➔ *BedrockCapsule*
With this release, the application has officially graduated from its original prototype name, **NIVYT Backup Copilot**, to **BedrockCapsule**.

#### Why the Rebrand?
- **Community Focus**: Transitioning from a personalized developer utility to a dedicated, open-source community tool.
- **Capsule Architecture**: The name reflects the project's core feature — encapsulating worlds with optional XOR passkey encryption, metadata tagging, and atomic rollback points.
- **Unified Identity**: All executables, installer scripts (`setup.iss`), window identifiers (`bedrockcapsule.app.2.1`), and Discord embeds are now aligned under the BedrockCapsule banner.

---

### 🌟 What's New in v2.1

#### 🎨 1. In-Memory WebView2 Rendering (Zero 404 Errors)
- **Eliminated Internal Bottle HTTP Server**: The UI is now injected directly into Microsoft Edge WebView2 via memory strings (`NavigateToString`), removing all dependency on localhost sockets/ports for frontend serving.
- **Base64 Asset Inlining**: Application logos and assets are automatically converted to Base64 data URIs on boot, guaranteeing zero file-path resolution issues.

#### 🛡️ 2. Bulletproof Restore & Rollback Recovery
- **Crash Recovery Guard**: If archive decompression or decryption fails during a world restoration, the engine automatically rolls back to the `_CRASH_RECOVERY` checkpoint so world folders are never corrupted or lost.
- **LevelDB Lock Awareness**: Improved game process exit detection to ensure Minecraft fully releases its file locks before attempting snapshot compression.

#### 📦 3. Universal `.mcworld` Export
- Directly export any historical capsule snapshot into an unencrypted `.mcworld` format compatible with Minecraft Bedrock on iOS, Android, Xbox, and Windows.

#### 🔒 4. Capsule Encryption Layer
- Built-in XOR encryption engine allowing users to protect sensitive survival saves and custom server worlds with a custom passkey.

#### ⚡ 5. Process & Background Daemon Stability
- **Single-Instance Lock Port**: Upgraded local socket locking mechanism to ensure only one instance of BedrockCapsule runs at a time.
- **System Tray Quick Actions**: Access backup folders, trigger manual syncs, and restore dashboard visibility directly from the Windows taskbar tray.
- **Window Visibility on Launch**: Fixed an issue where the dashboard remained hidden if launched manually without `--autostart`.

#### 🤖 6. Discord Gateway Microservice (v2.1)
- Updated the FastAPI Discord bot gateway with modern embeds displaying:
  - 🗺️ World Name
  - 💾 Backup Size (in MB)
  - ⚙️ Trigger Mode (Auto-Pilot vs. Manual)
  - 🕒 ISO-8601 Timestamp

---

### 🛠️ Bug Fixes & Refactoring in v2.1
- **JS Injection Fix**: Fixed unescaped Windows backslashes (`\`) in file paths crashing frontend UI status feeds by migrating to `json.dumps()` serialization.
- **HTML Special Character Escaping**: World names containing quotes, apostrophes, or angle brackets no longer break button click events.
- **PyInstaller Bundling**: Added explicit resource data bundling (`datas=[('index.html', '.'), ('logo.ico', '.')]`) to `BedrockCapsule_2.1.spec`.
- **Inno Setup Modernization**: Updated `setup.iss` to target `BedrockCapsule_2.1.exe` and generate clean uninstallation shortcuts.
- **Root Requirements File**: Added root `requirements.txt` to eliminate package discovery errors during automated builds.

---

### 📦 Upgrading from NIVYT Backup Copilot
If you have an older build installed:
1. Download **`BedrockCapsule_Setup_v2.1.exe`** from the Releases page.
2. Run the installer. It will automatically update your shortcuts and point to the new `BedrockCapsule_2.1.exe` binary.
3. Your existing backups in `%APPDATA%\BedrockCapsule` will be preserved automatically.

---

## 📜 Historical Versions

### v2.0.1 (Legacy - NIVYT Backup Copilot)
- Added initial PyWebView dark-themed desktop UI.
- Implemented `levelname.txt` automatic world detection.
- Introduced background auto-pilot monitoring with `psutil`.
- Added retention limit rotation (keeping last 5 snapshots).

### v1.0.0 (Initial Prototype)
- CLI-based Python script for backing up `com.mojang` worlds on game exit.
- Simple zip compression without encryption or GUI.
