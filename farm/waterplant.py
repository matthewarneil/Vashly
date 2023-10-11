import sqlite3
import discord
from discord.ext import commands
from datetime import datetime, timedelta
from dateutil.parser import parse

class WaterPlant(commands.Cog):
    def __init__(self, bot, database):
        self.bot = bot
        self.database = database

    @commands.hybrid_command()
    async def waterplant(self, ctx):
        """Water your plant!"""
        user_id = ctx.message.author.id
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute("SELECT * FROM farm WHERE user_id=?", (user_id,))
        if user := c.fetchone():
            if user[7] <= 0:
                embed = discord.Embed(title="Action Failed", description="`You don't have any seeds planted.`", color=0x2a2d31)
                embed.set_footer(text="View documentation for all commands.")
                await ctx.send(embed=embed)
                return
            last_cared = parse(user[10])
            if datetime.now() - last_cared >= timedelta(hours=24):
                new_water_level = user[8] + 1  # Increment the water level by 1
                c.execute("UPDATE farm SET water_level = ?, last_cared = ? WHERE user_id=?", (new_water_level, datetime.now(), user_id))
                conn.commit()
                embed = discord.Embed(
                    title="Action Successful",
                    description="`You've watered your plant.`",
                    color=0x2A2D31,
                )
                embed.set_footer(text="View documentation for all commands.")
                embed.set_image(url="https://vashly.com/wp-content/uploads/2023/06/Water.png")
            else:
                embed = discord.Embed(title="Action Failed", description="`You can only water your plant once every 24 hours.`", color=0x2a2d31)
                embed.set_footer(text="View documentation for all commands.")
        else:
            embed = discord.Embed(title="Action Failed", description="`User not found. Contact Support.`", color=0x2a2d31)
            embed.set_footer(text="View documentation for all commands.")
        await ctx.send(embed=embed)

async def setup(bot):
    database = "farm.db"  
    await bot.add_cog(WaterPlant(bot, database))
