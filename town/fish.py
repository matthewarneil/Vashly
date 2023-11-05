import random
import time
import sqlite3
import discord
import asyncio
from discord.ext import commands

class Fish(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.connection = sqlite3.connect('town.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                                discord_id INTEGER PRIMARY KEY,
                                population INTEGER NOT NULL,
                                income INTEGER NOT NULL,
                                happiness INTEGER NOT NULL,
                                infrastructure INTEGER NOT NULL
                            )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS buildings (
                                id INTEGER PRIMARY KEY,
                                discord_id INTEGER,
                                building_type TEXT NOT NULL,
                                building_level INTEGER NOT NULL,
                                FOREIGN KEY(discord_id) REFERENCES users(discord_id)
                            )""")
        self.last_fished = {} # dictionary to store the last time the command was used by each user

    def user_exists(self, user_id):
        self.cursor.execute("SELECT discord_id FROM users WHERE discord_id=?", (user_id,))
        return self.cursor.fetchone() is not None

    def add_user(self, user_id):
        self.cursor.execute("INSERT INTO users (discord_id, population, income, happiness, infrastructure) VALUES (?, 0, 0, 0, 0)", (user_id,))
        self.connection.commit()

    def get_user_balance(self, user_id):
        """Get the current balance of a user."""
        self.cursor.execute("SELECT balance FROM users WHERE discord_id=?", (str(user_id),))
        row = self.cursor.fetchone()
        return row[0] if row is not None else 0
    
    @commands.hybrid_command()
    async def fish(self, ctx):
        """Fish for coins!"""
        user_id = str(ctx.author.id)
        if not self.user_exists(user_id):
            self.add_user(user_id)

        if user_id in self.last_fished and time.time() - self.last_fished[user_id] < 1800:
            # User can only fish once every 30 minutes (1800 seconds)
            await ctx.send(embed=discord.Embed(description="`You can only fish once every 30 minutes!`", color=0x2a2d31))
            return

        # Generate a random number between 1 and 100 for the amount of coins won
        coins_won = random.randint(1, 100)

        # Generate a random math question for the user to answer to catch the fish
        x = random.randint(1, 10)
        y = random.randint(1, 10)
        operator = random.choice(["+", "-", "*"])
        question = f"`Solve: {x} {operator} {y}?`"

        # Send the math question to the user and wait for their answer
        embed = discord.Embed(description=f"You cast your line and wait for a fish to bite...\n A fish is now biting! Answer this math question to catch it!\n\n{question}", color=0x2a2d31)
        embed.set_footer(text="View documentation for all commands.")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        message = await ctx.send(embed=embed)
        try:
            answer = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=30)
        except asyncio.TimeoutError:
            await message.edit(embed=discord.Embed(description="`You took too long to answer the math question! The fish got away.`", color=0x2a2d31))
            return

        try:
            result = int(eval(f"{x} {operator} {y}"))
            if int(answer.content) != result:
                await message.edit(embed=discord.Embed(description="`Incorrect answer! The fish got away.`", color=0x2a2d31))
                return
        except Exception:
            await message.edit(embed=discord.Embed(description="`Invalid answer! The fish got away.`", color=0x2a2d31))
            return

        # Add the coins won to the user's balance and update their last_fished time
        self.cursor.execute("UPDATE users SET income=income+?, happiness=happiness+1, population=population+1 WHERE discord_id=?", (coins_won, user_id))
        self.connection.commit()
        self.last_fished[user_id] = time.time()

        embed = discord.Embed(description=f"`You caught a fish and won {coins_won} coins!`", color=0x2a2d31)
        embed.set_footer(text="View documentation for all commands.")
        await message.edit(embed=embed)

async def setup(bot):
    await bot.add_cog(Fish(bot))
