<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->



<!-- PROJECT LOGO -->
<br />
<div align="center">

  <h2 align="center">Discord Bot</h2>

  <p align="center">
    An open-source, multipurpose Discord bot
    <br />
    <!-- <a href="https://github.com/othneildrew/Best-README-Template"><strong>Explore the docs »</strong></a> -->
    <a href="https://github.com/brshadow19/discord-bot/issues">Report Bug</a>
    ·
    <a href="https://github.com/brshadow19/discord-bot/issues">Request Feature</a>
    ·
    <a href="https://github.com/brshadow19/discord-bot/wiki/Commands">Bot Commands</a>
  </p>
</div>
<br />

[![Contributors][contributors-shield]][contributors-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield-brenden]][linkedin-url-brenden]
[![LinkedIn][linkedin-shield-devon]][linkedin-url-devon]
[![LinkedIn][linkedin-shield-gavin]][linkedin-url-gavin]


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#api-tokens">API Tokens</a></li>
        <li><a href="#running-as-a-python-application">Python Application</a></li>
        <li><a href="#docker">Docker</a></li>
      </ul>
    </li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

After dealing with various music bots being shut down on Discord, we decided to make our own as a fun side project. We began with the goal of making a bot that could play music from a YouTube link with some basic music player functionalities, such as play, pause, view the queue, etc. After a few months of working on the project in our free time, it has begun to evolve into something that we use for more than just listening to music in a call together. Our bot is capable of playing audio from both YouTube and Spotify links, answering your questions with an 8 ball, telling you the weather in a given location, and can even give you some stats from the rhythm game OSU! We plan to add more functionality in the future, specifically around integration with some of our favorite video games. 

This bot is coded completely in Python with a lot of help from the Discord API wrapper [Discord.py](https://discordpy.readthedocs.io/en/stable/index.html). The bot can be run as a Python script, or in a Docker container with the provided [Dockerfile](https://github.com/BRShadow19/discord-bot/blob/main/Dockerfile).

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

This bot can be run either as a set of Python scripts, or in a Docker container. Regardless of your choice, there are some API tokens that you will need in order for the bot to work. To start, clone this repository into a local directory on your machine.

### API Tokens
First, make a file called `token.env` within the main directory of the bot code. Now we will start to fill it with our API tokens. If you choose to use Docker, instead enter the API keys in the corresponding spots in `Dockerfile` (for the Dockerfile you should **not put the key values within quotes**, unlike how it is shown below).
* Discord bot token
  * Follow [these instructions](https://discordpy.readthedocs.io/en/stable/discord.html) to set up a bot account
  * Once your bot is created, grab the token and add it to your `token.env` file like so:
  ```sh
  # Discord bot token
  TOKEN='*********************'
  ```
* YouTube API key
  * Follow [these instructions](https://developers.google.com/youtube/registering_an_application) to create a YouTube application and obtain an API key. We will use this for the Pafy module which uses the YouTube API to gather information about playlists.
  * Copy the API token and add it to `token.env` like so:
  ```sh
  # YouTube API key
  KEY='*********************'
  ```
* Weather API key
  * Follow [these instructions](https://openweathermap.org/appid) to create an OpenWeather account and obtain an API key
  * Copy the API key and add it to `token.env` like so:
  ```sh
  # Weather API key
  WEATHER='*********************'
  ```
* Spotify API key and secret
  * Follow the first few directions on [Spotify's developer site](https://developer.spotify.com/documentation/web-api/quick-start/) up to "Register Your Application".
  * Once you create your application, copy the API key and client secret and place them in `token.env` like so:
  ```sh
  # Spotify API Key
  SPOTIFY_ID='*********************'
  # Spotify API secret
  SPOTIFY_SECRET='******************'
  ```
* osu! API key and client ID
  * Go to the [osu!api wiki](https://github.com/ppy/osu-api/wiki) and follow their links to request an API key.
  * From your developer page, copy the API key and client ID and place them in `token.env` like so:
  ```sh
  # OSU APIv2 secret
  OSU='****************'
  # OSU APIv2 ID
  OSU_ID='******'
  ```
<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Running as a Python application
**In order for audio to work, you will need to install [FFmpeg](https://ffmpeg.org/) on your machine!**

Below is a list of Python modules that you will need to install in order for the bot to work properly:
* [Discord.py](https://discordpy.readthedocs.io/en/stable/intro.html#installing) - Discord API wrapper
  * There are different instructions based on your OS, so it's best to follow what they recommend
* [Pafy](https://pypi.org/project/pafy/) - Retrieve YouTube content and metadata
* [youtube_dl](https://pypi.org/project/youtube_dl/) - YouTube video downloader (used for obtaining audio)
* [Spotipy](https://pypi.org/project/spotipy/) - Library for interacting with the Spotify API
* [PyNaCl](https://pypi.org/project/PyNaCl/) - Used by Discord.py
* [python-dotenv](https://pypi.org/project/python-dotenv/) - Read in environment variables from `token.env`
* [pytz](https://pypi.org/project/pytz/) - Get accurate time zone information

Now, you should have everything you need for the bot to work. Simply run `__init__.py` to start up the bot!
<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Docker
This guide will assume you already have Docker installed and working on your machine. If not, follow [this documentation](https://docs.docker.com/get-started/) to get started with Docker.
* Build the image
  ```sh
  # From inside the root of the bot directory
  docker build -t containername
  ```
* Run the application
  ```sh
  docker run -d -it --name=CONTAINER_NAME
  ```
And that's it! The bot should be up and running now. You can use
```sh
docker attach CONTAINER_NAME
```
to attach the container to your terminal and check for any errors. If you have the default keybinds for docker, you can detatch the container by using CTRL+P then CRTL+Q.
<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
<!-- ## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#readme-top">back to top</a>)</p> -->



<!-- ROADMAP -->
<!-- ## Roadmap

- [x] Add Changelog
- [x] Add back to top links
- [ ] Add Additional Templates w/ Examples
- [ ] Add "components" document to easily copy & paste sections of the readme
- [ ] Multi-language Support
    - [ ] Chinese
    - [ ] Spanish

See the [open issues](https://github.com/othneildrew/Best-README-Template/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>
 -->


<!-- CONTRIBUTING -->
<!-- ## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p> -->



<!-- LICENSE -->
## License

Distributed under the Apache License 2.0. See `LICENSE` for more information.
<br />
<br />
<!-- <p align="right">(<a href="#readme-top">back to top</a>)</p> -->


<!-- CONTACT -->
## Contact

Brenden Reim - brenden@breim.dev

Project Link: [https://github.com/brshadow19/discord-bot](https://github.com/brshadow19/discord-bot)

<!-- <p align="right">(<a href="#readme-top">back to top</a>)</p> -->
<br />
<br />


<!-- ACKNOWLEDGMENTS -->
## Acknowledgments


* [Discord.py](https://discordpy.readthedocs.io/en/stable/index.html)
* [FFmpeg](https://ffmpeg.org/)
* [OpenWeather](https://openweathermap.org/api)
* [osu!api](https://github.com/ppy/osu-api/wiki)
* [Choose an Open Source License](https://choosealicense.com)
* [Img Shields](https://shields.io)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/brshadow19/discord-bot?style=for-the-badge
[contributors-url]: https://github.com/BRShadow19/discord-bot/graphs/contributors
<!-- [forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge -->
<!--[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members -->
[stars-shield]: https://img.shields.io/github/stars/BRShadow19/discord-bot?style=for-the-badge
[stars-url]: https://github.com/BRShadow19/discord-bot/stargazers
[issues-shield]: https://img.shields.io/github/issues/BRShadow19/discord-bot?style=for-the-badge
[issues-url]: https://github.com/BRShadow19/discord-bot/issues
[license-shield]: https://img.shields.io/github/license/BRShadow19/discord-bot?style=for-the-badge
[license-url]: https://github.com/BRShadow19/discord-bot/blob/main/LICENSE
[linkedin-shield-brenden]: https://img.shields.io/badge/LINKEDIN-Brenden-blue?style=for-the-badge
[linkedin-url-brenden]: https://linkedin.com/in/brenden-reim
[linkedin-shield-devon]: https://img.shields.io/badge/LINKEDIN-Devon-blue?style=for-the-badge
[linkedin-url-devon]: https://www.linkedin.com/in/devon-tolbert-86a004141/
[linkedin-shield-gavin]: https://img.shields.io/badge/LINKEDIN-Gavin-blue?style=for-the-badge
[linkedin-url-gavin]: https://www.linkedin.com/in/gavin-bean-a52376241/
<!-- [product-screenshot]: images/screenshot.png -->
