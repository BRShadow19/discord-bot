
FROM rockylinux:9

RUN dnf update -y && \
dnf install python3.12 python3.12-devel -y && \
dnf install python3.12-pip -y
RUN yes | python3.12 -m pip install --upgrade pip
RUN dnf -y install --nogpgcheck https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-9.noarch.rpm && \
dnf  config-manager --set-enabled crb
RUN dnf install ffmpeg libffi-devel -y
RUN dnf install git unzip -y


RUN yes | python3.12 -m pip install asyncio && \
 yes | python3.12 -m pip install pafy && yes | python3.12 -m pip install -U yt_dlp[default] && \
 yes | python3.12 -m pip install youtube_dl && \
 yes | python3.12 -m pip install spotipy && yes | python3.12 -m pip install pynacl && yes | python3.12 -m pip install python-dotenv && \
 yes | python3.12 -m pip install pytz && \
 yes | python3.12 -m pip install youtube-search && \
 yes | python3.12 -m pip install "discord.py[voice] @ git+https://github.com/rapptz/discord.py"

RUN curl -fsSL https://deno.land/install.sh | sh

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

CMD ["python3.12", "/bot-code/__init__.py"]