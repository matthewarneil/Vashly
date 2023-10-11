import discord
import json
import random
import requests
from discord.ext import commands

class Joke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def joke(self, ctx):
        """Tells a random joke."""
        url = 'https://official-joke-api.appspot.com/random_joke'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            setup = data['setup']
            punchline = data['punchline']
            embed = discord.Embed(title="Joke", description=f"{setup}\n\n||{punchline}||", color=0x2a2d31)
            embed.set_footer(text="View documentation for all commands.")
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("`Failed to get a joke :(`")

async def setup(bot):
    await bot.add_cog(Joke(bot))
