import discord
import asyncio
import requests
import json
import os
import datetime
import string
from discord.ext import commands


class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def weather(self,ctx,city='',city_second_space='',city_third_space=''):
        """Sends a message to the discord channel containing weather information about a given location.
        Weather information includes high/low temperatures, the humidity, and current weather conditions (cloudy, rainy, etc.)

        Args:
            ctx (obj): Object containing all information about the context of the bot within a Discord server,
                such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
            city (str, optional): First word in the name of the city. Defaults to ''.
            city_second_space (str, optional): Second word in the name of the city. Defaults to ''.
            city_third_space (str, optional): Third word in the name of the city. Defaults to ''.

        Returns:
            None: If the user does not enter any characters for the city, the method will return None (otherwise the function runs to completion without returning)
        """        
        current_city = str(city) + " " + str(city_second_space) + " " + city_third_space
        current_city = string.capwords(current_city)
        if city == '' or city is None:
            await ctx.send(":person_facepalming: Nothing is a city? :person_facepalming:")
            return None
        complete_url = "http://api.openweathermap.org/data/2.5/weather?" + "appid=" + weather_key + "&q=" + current_city + "&units=imperial"
        response = requests.get(complete_url)
        data = response.json()  # Dictionary of weather data for the chosen city
        if data["cod"] != "404":
            opendata = data["main"]
            temp = opendata["temp"]
            temp_max = opendata["temp_max"]
            temp_min = opendata["temp_min"]
            humidity = opendata["humidity"]
            weather = data["weather"]
            desc = weather[0]["description"]
            # Create a Discord Embed object using the gathered info
            g = discord.Embed(title=":white_sun_cloud: _**{}**_:thunder_cloud_rain:".format(current_city), description="High: *{}°*, Low: *{}°*\nCurrent Temp: **{}°**\nHumidity: **{}%**\nDescription: {}".format(str(temp_max), str(temp_min), str(temp), str(humidity), string.capwords(str(desc))), color=discord.Color.dark_blue()).set_footer(text='For a forecast 5 days in advance -> m!forecast', icon_url='https://i.imgur.com/oWQeUDj.png')
            await ctx.send(embed=g)
        else:
            await ctx.send(":person_facepalming: That isn't a city :person_facepalming:")

    @commands.command()
    async def forecast(self,ctx,city='',city_second_space='',city_third_space=''):
        """_summary_

        Args:
            ctx (obj): Object containing all information about the context of the bot within a Discord server,
                such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
            city (str, optional): First word in the name of the city. Defaults to ''.
            city_second_space (str, optional): Second word in the name of the city. Defaults to ''.
            city_third_space (str, optional): Third word in the name of the city. Defaults to ''.

        Returns:
            None: If the user does not enter any characters for the city, the method will return None (otherwise the function runs to completion without returning)
        """        
        current_city = str(city) + " " + str(city_second_space) + " " + city_third_space   # Concatenate the city name
        current_city = string.capwords(current_city)    # Capitalize the city name
        if city == '' or city is None:
            await ctx.send(":person_facepalming: Nothing is a city? :person_facepalming:")
            return None
        lonLatCall = "http://api.openweathermap.org/geo/1.0/direct?" +"q=" + current_city + "&appid=" + weather_key
        response = requests.get(lonLatCall)
        # Get the longitude and latitude of the chosen city
        data_first_call = response.json()
        lon = data_first_call[0]["lon"]
        lat = data_first_call[0]["lat"]
        latt = str(lat)
        lonn = str(lon)
        # Use the longitude and latitude to obtain forecast data for the chosen city
        forecast_call = "http://api.openweathermap.org/data/2.5/forecast?" + "appid=" + weather_key + "&lat=" + latt + "&lon=" + lonn + "&units=imperial"
        forecast_response = requests.get(forecast_call)
        for_data = forecast_response.json()     # Dictionary of forecast data
        if for_data["cod"] != "404":
            forecast = for_data["list"]
            temp = ""
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            for x in range(6):
                temp += "**{}**\n:thermometer:High: {} - Low: {} - Avg: **{}**°\n sky: *{}*\n\n".format(tomorrow + datetime.timedelta(days=x), forecast[x]["main"]["temp_max"], forecast[x]["main"]["temp_min"], forecast[x]["main"]["temp"], string.capwords(forecast[x]["weather"][0]["description"]))
            # Create a Discord Embed object using the gathered info
            g = discord.Embed(title=":white_sun_cloud: _**{}**_'s Expected Weather (Next 6 days) :thunder_cloud_rain:".format(current_city), description=temp, color=discord.Color.dark_blue()).set_footer(text='Want the current temperature? use m!weather', icon_url='https://i.imgur.com/oWQeUDj.png').set_thumbnail(url='https://i.imgur.com/j7WQ7bx.png')
            await ctx.send(embed=g)
        else:
            await ctx.send(":person_facepalming: That isn't a city :person_facepalming:")

    @commands.command()
    async def time(self,ctx):
        """Sends a message telling the current time (based on where the bot host is located)

        Args:
            ctx (Obj): Object containing all information about the context of the bot within a Discord server,
                such as the channel, who sent the message, when a message was sent, etc. Necessary for all bot commands
        """        
        await ctx.send(":clock2: *{}*".format(datetime.datetime.now().strftime("%I:%M %p on %A, %b %d")))


weather_key = ''

async def setup(bot):
    """Adds this cog to the bot, meaning that the commands in the Weather class can be used by the bot/users

    Args:
        bot (discord.Bot): The bot object to have the cog added to
    """    
    global weather_key 
    weather_key = os.environ.get('WEA')
    await bot.add_cog(Weather(bot))
    print("Weather is online!")