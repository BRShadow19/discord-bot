
FROM ubuntu:latest

RUN apt-get update -y && apt-get upgrade -y && apt install python3 -y && apt install python3-pip -y && yes | pip3 install --upgrade pip
RUN apt install ffmpeg -y
RUN apt install git -y

RUN yes | pip3 install -U discord.py && yes | pip3 install asyncio && yes | pip3 install pafy && yes | pip3 install -U yt_dlp[default] && yes | pip3 install git+https://github.com/ytdl-org/youtube-dl.git@master#egg=youtube_dl && yes | pip3 install spotipy && yes | pip3 install pynacl && yes | pip3 install python-dotenv && yes | pip3 install pytz && yes | pip3 install youtube-search

# Discord bot token
ENV TOKEN=******************************
# YouTube API key
ENV KEY=*************************
# Weather API key
ENV WEA=***************
# Spotify API key
ENV SPOTIFY_ID=**************
# Spotify API secret
ENV SPOTIFY_SECRET=**********
# OSU APIv2 secret
ENV OSU=****************
# OSU APIv2 ID
ENV OSU_ID=******

COPY bot-code /
RUN chmod +x __init__.py

CMD ["python3", "./__init__.py"]
