import discord
import asyncio
import requests
import json
import os
import datetime
from discord.ext import commands


class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def weather(self,ctx,city='',city_second_space='',city_third_space=''):
        current_city = str(city) + " " + str(city_second_space) + " " + city_third_space
        if city == '' or city is None:
            await ctx.send(":person_facepalming: Nothing is a city? :person_facepalming:")
            return None
        complete_url = "http://api.openweathermap.org/data/2.5/weather?" + "appid=" + weather_key + "&q=" + current_city + "&units=imperial"
        response = requests.get(complete_url)
        data = response.json()
        if data["cod"] != "404":
            opendata = data["main"]
            temp = opendata["temp"]
            temp_max = opendata["temp_max"]
            temp_min = opendata["temp_min"]
            humidity = opendata["humidity"]
            weather = data["weather"]
            desc = weather[0]["description"]
            g = discord.Embed(title=":white_sun_cloud: _**{}**_:thunder_cloud_rain:".format(current_city), description="High: *{}°*, low: *{}°*\nCurrent Temp: **{}°**\nHumidity: {}\nDescription: {}".format(str(temp_max), str(temp_min), str(temp), str(humidity), str(desc)), color=discord.Color.dark_blue()).set_footer(text='For a forecast 5 days in advance -> m!forecast', icon_url='https://i.imgur.com/oWQeUDj.png')
            await ctx.send(embed=g)
        else:
            await ctx.send(":person_facepalming: That isn't a city :person_facepalming:")

    @commands.command()
    async def forecast(self,ctx,city='',city_second_space='',city_third_space=''):
        current_city = str(city) + " " + str(city_second_space) + " " + city_third_space
        if city == '' or city is None:
            await ctx.send(":person_facepalming: Nothing is a city? :person_facepalming:")
            return None
        lonLatCall = "http://api.openweathermap.org/geo/1.0/direct?" +"q=" + current_city + "&appid=" + weather_key
        response = requests.get(lonLatCall)
        data_first_call = response.json()
        lon = data_first_call[0]["lon"]
        lat = data_first_call[0]["lat"]
        latt = str(lat)
        lonn = str(lon)
        forecast_call = "http://api.openweathermap.org/data/2.5/forecast?" + "appid=" + weather_key + "&lat=" + latt + "&lon=" + lonn + "&units=imperial"
        forecast_response = requests.get(forecast_call)
        for_data = forecast_response.json()
        if for_data["cod"] != "404":
            forecast = for_data["list"]
            temp = ""
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            for x in range(6):
                temp += "**{}**\n:thermometer:High: {} - Low: {} - Avg: **{}**°\n sky: *{}*\n\n".format(tomorrow + datetime.timedelta(days=x), forecast[x]["main"]["temp_max"], forecast[x]["main"]["temp_min"], forecast[x]["main"]["temp"], forecast[x]["weather"][0]["description"])
            g = discord.Embed(title=":white_sun_cloud: _**{}**_'s Expected Weather (Next 6 days) :thunder_cloud_rain:".format(current_city.capitalize()), description=temp, color=discord.Color.dark_blue()).set_footer(text='Want the current temperature? use m!weather', icon_url='https://i.imgur.com/oWQeUDj.png').set_thumbnail(url='https://i.imgur.com/j7WQ7bx.png')
            await ctx.send(embed=g)
        else:
            await ctx.send(":person_facepalming: That isn't a city :person_facepalming:")

    @commands.command()
    async def time(self,ctx):
        await ctx.send(":clock2: *{}*".format(datetime.datetime.now().strftime("%I:%M %p on %A, %b %d")))

weather_key = ''

def setup(bot):
    global weather_key 
    weather_key = os.environ.get('WEA')
    bot.add_cog(Weather(bot))
    print("Weather is online!")