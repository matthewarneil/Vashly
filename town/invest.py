import discord
from discord.ext import commands
import sqlite3
import random

class Invest(commands.Cog):
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
    async def invest(self, ctx, amount:int):
        """Invest a specified amount of coins in the virtual stock market.
        
        Parameters
        -----------
        amount: amount
            Select the amount you want to invest!
        
        """
        user_id = str(ctx.author.id)
        if not self.user_exists(user_id):
            self.add_user(user_id)

        # Retrieve user's income
        self.cursor.execute("SELECT income FROM users WHERE discord_id=?", (user_id,))
        result = self.cursor.fetchone()
        if result is None:
            await ctx.send("You do not have an income yet!")
            return
        income = result[0]

        # Check if user has enough coins to invest
        if amount > income or amount < 1:
            await ctx.send("You do not have enough coins to invest that much, or the investment amount must be at least 1 coin!")
            return

        # Calculate a random return on investment (ROI) between -50% and 50%
        roi = random.uniform(-0.5, 0.5)

        # Calculate the investment result and update user's income, happiness, and population
        result = int(amount * (1 + roi))
        self.cursor.execute(
            "UPDATE users SET income=income+?, happiness=happiness-1, population=population-1 WHERE discord_id=?",
            (result - amount, user_id),
        )
        self.connection.commit()

        # Send an embed with the investment result
        if roi >= 0:
            message = f"You earned a {round(roi*100)}% ROI and gained {result - amount} coins!"
        else:
            message = f"You lost a {round(abs(roi)*100)}% ROI and lost {amount - result} coins!"
        embed = discord.Embed(title="Investment Result", color=0x2a2d31)
        embed.set_author(name=ctx.author.name, icon_url=str(ctx.author.avatar.url))
        embed.add_field(name="Your investment:", value=f"```{amount} coins```", inline=False)
        embed.add_field(name="Return on investment:", value=f"```{round(roi*100)}%```", inline=False)
        embed.add_field(name="Result:", value=f"```{message}```", inline=False)
        embed.add_field(name="New income:", value=f"```{income+result-amount} coins```", inline=False)
        embed.set_footer(text="View documentation for all commands.")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Invest(bot))
