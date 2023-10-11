import discord
import random
from discord.ext import commands

class Dice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def droll(self, ctx, sides: int = 6, rolls: int = 1):
        """Roll one or more dice with a specified number of sides.
        Parameters
        -----------
        sides: sides
            How many sides you want your dice to have.

        Parameters
        -----------
        rolls: rolls
            How many times you want your dice to roll.
        """
        if sides < 2:
            embed = discord.Embed(description="`The number of sides must be at least 2.`", color=0x2a2d31)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            embed.set_footer(text="View documentation for all commands.")
            await ctx.send(embed=embed)
            return
        if rolls < 1:
            embed = discord.Embed(description="`You must roll the dice at least once.`", color=0x2a2d31)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            embed.set_footer(text="View documentation for all commands.")
            await ctx.send(embed=embed)
            return
        if rolls > 10:
            embed = discord.Embed(description="`You can only roll the dice up to 10 times.`", color=0x2a2d31)
            await ctx.send(embed=embed)
            return

        results = [random.randint(1, sides) for _ in range(rolls)]
        embed = discord.Embed(description=f"You rolled **{', '.join(str(result) for result in results)}**!", color=0x2a2d31)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_footer(text="View documentation for all commands.")
        await ctx.send(embed=embed)

async def setup(bot):
   await bot.add_cog(Dice(bot))
