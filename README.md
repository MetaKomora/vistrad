# vistrad

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Video streamer and audio downloader

Search and open Youtube videos, Twitch streams on MPV and download audio to .opus format

## Dependencies
- **python v3.11+** - To execute this script
- **yad** - To show graphical dialogs
- **mpv** - To stream videos
- **yt-dlp** - To open links on MPV, configure resolution, hardware acceleration and to download audio
- **ffmpeg** - To convert downloaded audio to .opus format
- **xdg-user-dirs** - To save downloaded audio to XDG music directory (optional)
- **xdg-utils** - To open the default markdown editor for history file
- **blackBox (flatpak)** - To open history file

## Installation
```sh
git clone https://github.com/MetaKomora/vistrad
mkdir -p ~/.local/bin/
mv vistrad/vistrad.py ~/.local/bin
```

## Usage
```sh
vistrad.py
```
