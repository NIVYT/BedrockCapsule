# 📦 BedrockCapsule — Release Notes

## ⚡ BedrockCapsule v2.2 — High-Speed Serverless & Zero-Lag Sync

Starting with version **2.2**, the Discord notification gateway has been completely overhauled:

### 🚀 Key Highlights & Improvements:
- **Serverless Discord Gateway**: Migrated the notification gateway from Render containers to Vercel Serverless Edge architecture, eliminating the 50-second idle cold-start delay for good.
- **Instant Background Dispatch**: Backup notifications to Discord are now fired asynchronously in a dedicated daemon thread. Your local world backups finish and save with zero UI lag.
- **Unified 2.2 Rebranding**: Discord embed messages, bot identity, and dashboard footers now seamlessly reflect the BedrockCapsule v2.2 release.

---

## 📦 BedrockCapsule v2.1 — Release Notes

Starting with version **2.1**, **NIVYT Backup Copilot** has officially been rebranded to **BedrockCapsule**.

### 🔍 Why the Rebrand?
- **From Prototype to Open Source**: What started as a personal backup script is now a full-fledged, community-driven desktop ecosystem for Minecraft Bedrock on Windows.
- **Capsule Concept**: The new name reflects the core architecture — bundling worlds into secure, timestamped, and encrypted "capsules" with instant rollback capabilities.
- **Unified Experience**: All desktop executables, setup installers, system tray menus, and Discord notifications are now unified under the **BedrockCapsule** identity.

---

### ⚡ What Changes for You?
- **Seamless Upgrade**: Your existing world backups in `%APPDATA%\BedrockCapsule` remain completely safe and intact.
- **New Installer & Binary**: The app is now packaged as `BedrockCapsule_2.1.exe` and `BedrockCapsule_Setup_v2.1.exe`.
- **Improved Performance**: Completely modernized frontend rendering, zero startup errors, and enhanced background stability.
