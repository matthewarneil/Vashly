import sqlite3
import discord
from discord.ext import commands
from datetime import datetime, timedelta
from dateutil.parser import parse

class PlantCondition(commands.Cog):
    def __init__(self, bot, database):
        self.bot = bot
        self.database = database

    @commands.hybrid_command()
    async def plantcondition(self, ctx):
        """View your plant condition!"""
        user_id = ctx.message.author.id
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute("SELECT * FROM farm WHERE user_id=?", (user_id,))
        if user := c.fetchone():
            if user[7] <= 0:
                embed = discord.Embed(title="Plant Condition", description="`You don't have any seeds planted.`", color=0x2a2d31)
                embed.set_footer(text="View documentation for all commands.")
            else:
                last_cared = parse(user[10])
                care_diff = datetime.now() - last_cared
                if care_diff.days >= 5:
                    seed_type = user[7]
                    water_level = user[8]
                    fertilizer_level = user[9]
                    base_growth_rate = 10  # Base growth rate per day
                    growth_rate = base_growth_rate + water_level * 5 + fertilizer_level * 10
                    growth_factor = 1.0 + growth_rate / 100.0
                    growth_days = care_diff.days
                    max_profits = [10000, 12000, 13000, 14000, 15000, 16000, 17000, 18000, 19000]
                    ROI = min(int((seed_type * 1000) * growth_factor ** growth_days), max_profits[seed_type - 1])  # Advanced ROI calculation based on growth factor and days, capped at the maximum profit for the seed type
                    new_balance = user[1] + ROI
                    new_plant_count = user[6] + 1
                    c.execute("UPDATE farm SET coins = ?, plants = ?, seed_type = 0, water_level = 0, fertilizer_level = 0, last_cared = NULL WHERE user_id=?", (new_balance, new_plant_count, user_id))
                    conn.commit()
                    embed = discord.Embed(title="Plant Condition", description=f"`Your type {seed_type} plant grew successfully! You earned {ROI} coins.`", color=0x2a2d31)
                    embed.set_footer(text="View documentation for all commands.")
                    embed.set_image(url="https://vashly.com/wp-content/uploads/2023/06/grown.png")
                else:
                    embed = discord.Embed(title="Plant Condition", description=f"Seed Type: `{user[7]}`\nWater Level: `{user[8]}`\nFertilizer Level: `{user[9]}`", color=0x2a2d31)
                    embed.set_image(url="https://vashly.com/wp-content/uploads/2023/06/Seeds.png")
                    embed.set_footer(text="View documentation for all commands.")
        else:
            embed = discord.Embed(title="Plant Condition", description="`User not found. Contact Support.`", color=0x2a2d31)
            embed.set_footer(text="View documentation for all commands.")
        await ctx.send(embed=embed)

async def setup(bot):
    database = "farm.db"  
    await bot.add_cog(PlantCondition(bot, database))
