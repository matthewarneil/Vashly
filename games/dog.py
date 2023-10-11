import discord
from discord.ext import commands
import requests

class Dog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def dog(self, ctx):
        """Random dog."""
        response = requests.get("https://dog.ceo/api/breeds/image/random")
        if response.status_code == 200:
            data = response.json()
            image_url = data["message"]
            
            embed = discord.Embed(title="Random Dog", color=0x2a2d31)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            embed.set_footer(text="View documentation for all commands.")
            embed.set_image(url=image_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Failed to fetch a random dog image.")

async def setup(bot):
    await bot.add_cog(Dog(bot))
