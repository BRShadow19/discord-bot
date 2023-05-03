import discord
from discord.ext import commands
import requests

class league(commands.Cog):

    def __init__(self, bot, gameAPI_url):
        self.bot = bot
        self.gameAPI_url = gameAPI_url+"/league"
     
        
    def sort_by_mastery(self, x):
        return x[1][1]
       
        
    @commands.command("lolmastery")
    async def mastery(self, ctx, *, summoner_name=""):
        if len(summoner_name) > 0:
            # Spaces must be "%20" in a URL
            input = summoner_name.split("$")
            summoner = input[0].replace(" ", "%20") 
            count = input[1]
            url = self.gameAPI_url + "/mastery/" + summoner+"/"+count
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                name = input[0]
                embed = discord.Embed(title=":fire: Highest Champion Mastery :fire:", description=name,
                                      color=discord.Color.gold())
                data = dict(sorted(data.items(), key=self.sort_by_mastery, reverse=True))
                for champion in data:
                    level = str(data[champion][0])
                    points = str(data[champion][1])
                    embed.add_field(name=champion, value="M"+level+"     "+points+" pts", inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send("Looks like you sent a summoner name that doesn't exist... or there is a server issue")
        else: 
            await ctx.send("To use this command, enter a summoner name and the number of champions, with a '$' before the number. Ex: ShadowShark19 $5")


async def setup(bot, url):
    """Adds this cog to the bot, meaning that the commands in the League class can be used by the bot/users

        Args:
            bot (discord.Bot): The bot object to have the cog added to
    """    
    await bot.add_cog(league(bot, gameAPI_url=url))
    print("League is online!")
        