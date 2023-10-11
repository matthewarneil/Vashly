import sqlite3
import asyncio
import aiohttp
import discord
from discord.ext import commands

class Animal(commands.Cog):
    def __init__(self, bot, database):
        self.bot = bot
        self.database = database
        self.create_table()

    def create_table(self):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS farm (
                        user_id INTEGER PRIMARY KEY,
                        coins INTEGER,
                        animals INTEGER,
                        barns INTEGER,
                        campfires INTEGER,
                        water_wells INTEGER,
                        plants INTEGER,
                        seed_type INTEGER,
                        water_level INTEGER,
                        fertilizer_level INTEGER,
                        last_cared datetime,
                        idle_time INTEGER
                        )''')
        conn.commit()
        conn.close()

    @commands.hybrid_command()
    async def buyanimal(self, ctx):
        """Buy an animal for your farm!"""
        user_id = ctx.message.author.id
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute("SELECT * FROM farm WHERE user_id=?", (user_id,))
        if user := c.fetchone():
            new_balance = user[1] - 5000
            if new_balance < 0:
                embed = discord.Embed(title="Transaction Failed", description="`You don't have enough coins. You need 5,000.`", color=0x2a2d31)
                embed.set_footer(text="View documentation for all commands.")
                await ctx.send(embed=embed)
                return
            new_animal_count = user[2] + 1  # Increment the animal count by 1
            if new_animal_count > 19:
                embed = discord.Embed(title="Transaction Failed", description="`You can't own more than 19 animals.`", color=0x2a2d31)
                embed.set_footer(text="View documentation for all commands.")
                await ctx.send(embed=embed)
                return
            c.execute("UPDATE farm SET coins = ?, animals = ? WHERE user_id=?", (new_balance, new_animal_count, user_id))
            conn.commit()
            image_url = f"https://vashly.com/wp-content/uploads/2023/06/{new_animal_count}.png"
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    if resp.status != 200:
                        embed = discord.Embed(title="Transaction Failed", description="`Could not download file. Contact Support.`", color=0x2a2d31)
                        embed.set_footer(text="View documentation for all commands.")
                        await ctx.send(embed=embed)
                        return
                    data = await resp.read()
                    await session.close()
            embed = discord.Embed(title="Transaction Successful", color=0x2a2d31)
            embed.set_footer(text="View documentation for all commands.")
            embed.set_image(url=image_url)
        else:
            embed = discord.Embed(title="Transaction Failed", description="`User not found. Contact Support.`", color=0x2a2d31)
            embed.set_footer(text="View documentation for all commands.")
        await ctx.send(embed=embed)



async def setup(bot):
    database = "farm.db"  
    await bot.add_cog(Animal(bot, database))