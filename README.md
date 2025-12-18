# Python Podcast Downloader (with Auto-Opus Transcoding) 🎙️🐍

A feature-rich Command Line Interface (CLI) tool designed to fetch podcast feeds and batch-download episodes. It intelligently handles audio formats, prioritizing Opus for high-efficiency storage while offering automated transcoding for standard MP3 feeds.

## 🌟 Key Features

Automated Transcoding: If a podcast only offers MP3, the tool uses FFmpeg to convert it to a voice-optimized Opus file (64kbps) on the fly, saving up to 70% in storage space without losing perceived quality.

Smart Prioritization: Automatically detects and downloads native .opus or .ogg files if the RSS feed provides them.

Advanced Batch Selection: Support for range downloading (e.g., 1-20), recent episodes (f10), oldest episodes (l5), or the entire library (all).

Progress Tracking: Interactive progress bars using tqdm for both downloads and transcoding steps.

Sanitized Filenames: Automatic removal of illegal characters to ensure compatibility across Windows, macOS, and Linux.

## 🛠️ Prerequisites

1. Python

Ensure you have Python 3.8 or higher installed. You can check your version with:

python --version


2. FFmpeg (Required for Transcoding)

This tool requires FFmpeg to be installed on your system to convert MP3s to Opus.

macOS (Homebrew): brew install ffmpeg

Linux (Ubuntu/Debian): sudo apt update && sudo apt install ffmpeg

Windows: 1. Download the "essentials" build from gyan.dev.
2. Extract the folder and add the bin directory to your System PATH.
3. Verify by running ffmpeg -version in a new Command Prompt.

## 🚀 Installation & Setup

Clone the repository:

git clone [https://github.com/your-username/python-podcast-downloader.git](https://github.com/your-username/python-podcast-downloader.git)
cd python-podcast-downloader


Install Python dependencies:

pip install -r requirements.txt


## 📖 Usage

Run the script to start the interactive session:

python podcast_downloader.py


1. Enter the RSS Feed

The script will ask for a URL. You can paste any valid podcast RSS feed or press Enter to use the default test feed.

2. Select Episodes

Once the feed is loaded, use the following commands to choose what to download:

Command

Action

Example

Number

Download a single specific episode

5

Range

Download a inclusive range

10-25

First N

Download the $N$ newest episodes

f10

Last N

Download the $N$ oldest episodes

l5

All

Download every episode in the feed

all

Quit

Exit the application

q

## ⚙️ How it Works

Fetching: Uses feedparser to extract episode details and media enclosures.

Analysis: Checks the type attribute of the media file.

Download:

If native Opus/Ogg is found, it downloads directly.

If MP3 is found, it downloads to a temporary .tmp.mp3 file.

Transcoding: Calls ffmpeg via a subprocess to convert the MP3 to Opus at 64kbps.

Cleanup: Automatically deletes temporary files after successful conversion.

## 📦 Dependencies

requests: For handling file downloads.

feedparser: For parsing RSS XML feeds.

tqdm: For visual progress bars.

📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Fork the Project

Create your Feature Branch (git checkout -b feature/AmazingFeature)

Commit your Changes (git commit -m 'Add some AmazingFeature')

Push to the Branch (git push origin feature/AmazingFeature)

Open a Pull Request
