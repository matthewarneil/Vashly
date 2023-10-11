import discord
import random
from discord.ext import commands

class Coinflip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def coinflip(self, ctx):
        """Flip a coin and get heads or tails"""
        options = ["Heads", "Tails"]
        result = random.choice(options)
        embed = discord.Embed(title="Coinflip", description=f"The coin landed on **{result}**!", color=0x2a2d31)
        embed.set_footer(text="View documentation for all commands.")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Coinflip(bot))
