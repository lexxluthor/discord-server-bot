# discord-server-bot

Simple discord server bot, with the following functionality:
## Modules

- Music module for local party (requires FFMPEG)
- Chat moderation module that allows to manage users
- Leveling system module for fun
- And a lot of different features that will make your server a bit better


## Used opensource projects

- [FFMPEG](https://github.com/FFmpeg/FFmpeg) - FFmpeg is a collection of libraries and tools to process multimedia content such as audio, video, subtitles and related metadata.
- [discord.py](https://github.com/Rapptz/discord.py) - A modern, easy to use, feature-rich, and async ready API wrapper for Discord written in Python.
- [youtube-dl](https://github.com/ytdl-org/youtube-dl) - youtube-dl - download videos from YouTube.com or other video platforms
- [PyNaCl](https://github.com/pyca/pynacl) - PyNaCl is a Python binding to libsodium, which is a fork of the Networking and Cryptography library. These libraries have a stated goal of improving usability, security and speed. It supports Python 3.6+ as well as PyPy 3.
- [discord_components](https://github.com/kiki7000/discord.py-components) - An unofficial third party library of discord.py for discord components.


## Installation on Linux

discord-server-bot requires [Python](https://www.python.org/) v3.8+ to run.

also, you need libffi7 package to run some discord-py functional, just install it from your Linux distribution repository

Cloning repository
```sh
git clone https://github.com/lexxluthor/discord-server-bot.git
cd discord-server-bot
```

Install the requirements for python.

```sh
pip install -r requirements.txt
```

create .env file and put into it your token like
```
TOKEN=yourToken123
```
also, you can specify prefix for your bot commands ('!' by default)
```
PREFIX=';;'
```

after that just run it
```sh
python bot.py
```