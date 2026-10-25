# PS4 App Manager

A native homebrew application for jailbroken PlayStation 4 consoles running **GoldHEN** (Firmware 13.52 and compatible).

## Features
- **Application Browser**: Scan and list installed games, homebrew, and system applications.
- **Hide/Show Application Management**: Logically toggle home screen visibility per app without deleting game files or modifying system database records.
- **Custom Icon Manager**: Assign custom icons to titles.
- **Backup & Restore**: Safeguard application configurations and preferences to persistent local storage (`/data/ps4_app_backups`).
- **Persistent Preferences**: Settings and visibility flags persist across reboot (`/data/ps4_app_manager_prefs.cfg`).

## Package Metadata
- **Title ID**: `PS4APP000`
- **Content ID**: `IV0000-PS4APP000_00-PS4APPMANAGER000`
- **Output Artifact**: `PS4-App-Manager.pkg`

## Local Building

### Prerequisites
- Docker (for extracting the `openorbisofficial/toolchain:latest` toolchain environment)
- Python 3.x
- Clang / Make

### Building Steps
```bash
# 1. Extract toolchain
python3 scripts/setup_toolchain.py

# 2. Compile ELF, generate eboot.bin, param.sfo, and package PKG
make

# 3. Validate generated package
make test
```

## GitHub Actions Automated CI/CD
The repository includes a complete GitHub Actions workflow at `.github/workflows/build.yml`.
- **Triggers**: On push to `main`, pull requests, version tags (`v*`), and manual `workflow_dispatch`.
- **Artifacts**: Automatically uploads `PS4-App-Manager.pkg` as downloadable GitHub Actions artifact.
- **Releases**: Attaches `PS4-App-Manager.pkg` to GitHub Releases on tagged versions (e.g. `v1.0.0`).

## Installation on PS4
1. Copy `PS4-App-Manager.pkg` to the root of a FAT32/exFAT formatted USB drive.
2. Plug the USB drive into your PS4 running GoldHEN.
3. On the PS4, go to **Settings -> GoldHEN -> Package Installer**.
4. Select `PS4-App-Manager.pkg` and install.
