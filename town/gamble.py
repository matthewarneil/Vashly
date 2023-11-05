import datetime
import discord
from discord.ext import commands
import sqlite3
import random

class Gamble(commands.Cog):
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

    def user_exists(self, user_id):
        self.cursor.execute("SELECT discord_id FROM users WHERE discord_id=?", (user_id,))
        return self.cursor.fetchone() is not None

    def add_user(self, user_id):
        self.cursor.execute("INSERT INTO users (discord_id, population, income, happiness, infrastructure) VALUES (?, 0, 0, 0, 0)", (user_id,))
        self.connection.commit()

    @commands.hybrid_command()
    async def gamble(self, ctx, amount:int):
        """Gamble a specified amount of coins.
        
        Parameters
        -----------
        amount: amount
            Select the amount you want to gamble!
        
        """
        user_id = str(ctx.author.id)
        if not self.user_exists(user_id):
            self.add_user(user_id)

        # Retrieve user's income
        self.cursor.execute("SELECT income FROM users WHERE discord_id=?", (user_id,))
        result = self.cursor.fetchone()
        if result is None:
            await ctx.send("`You do not have an income yet!`")
            return
        income = result[0]

        # Check if user has enough coins to gamble and if they are not gambling all their coins
        if amount > income or amount >= income > 1:
            await ctx.send("`You do not have enough coins to gamble that much, or you must leave at least 1 coin!`")
            return

        # Simulate a coin toss
        result = random.choice(['heads', 'tails'])

        # Calculate winnings or losses
        if result == 'heads':
            winnings = amount
            message = f"You won {winnings} coins! Congrats!"
        else:
            winnings = -amount
            message = f"You lost {amount} coins. Better luck next time!"

        # Update user's income, happiness, and population
        self.cursor.execute(
            "UPDATE users SET income=income+?, happiness=happiness-1, population=population-1 WHERE discord_id=?",
            (winnings, user_id),
        )
        self.connection.commit()

        embed = discord.Embed(title="Gambling - Taking A Chance!", color=0x2a2d31)
        embed.set_author(name=ctx.author.name, icon_url=str(ctx.author.avatar.url))
        embed.add_field(name="Your bet:", value=f"```{amount} coins```", inline=False)
        embed.add_field(name="Coin landed on:", value=f"```{result}```", inline=False)
        embed.add_field(name="Result:", value=f"```{message}```", inline=False)
        embed.add_field(name="New income:", value=f"```{income+winnings} coins```", inline=False)
        embed.set_footer(text="View documentation for all commands.")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Gamble(bot))
