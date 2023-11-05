import discord
from discord.ext import commands
import sqlite3
import random
import time

class Lottery(commands.Cog):
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
        self.user_last_lottery_time = {}  # dictionary to store the last time the command was used by each user

    def user_exists(self, user_id):
        self.cursor.execute("SELECT discord_id FROM users WHERE discord_id=?", (user_id,))
        return self.cursor.fetchone() is not None

    def add_user(self, user_id):
        self.cursor.execute("INSERT INTO users (discord_id, population, income, happiness, infrastructure) VALUES (?, 0, 0, 0, 0)", (user_id,))
        self.connection.commit()

    @commands.hybrid_command()
    async def lottery(self, ctx, amount:int):
        """Buy a ticket for a chance to win a large amount of coins. Can only be used once per week.

        Parameters
        -----------
        amount: amount
            Select the amount you want to buy!
        
        """
        user_id = str(ctx.author.id)
        if not self.user_exists(user_id):
            self.add_user(user_id)

        current_time = time.time()
        last_lottery_time = self.user_last_lottery_time.get(user_id, 0)  # get the last time the command was used by this user
        if current_time - last_lottery_time < 604800: # 604800 seconds = 1 week
            await ctx.send("`You can only use the lottery command once per week!`")
            return

        # Retrieve user's income
        self.cursor.execute("SELECT income FROM users WHERE discord_id=?", (user_id,))
        result = self.cursor.fetchone()
        if result is None:
            await ctx.send("`You do not have an income yet. Use the work command to earn some coins!`")
            return
        income = result[0]

        # Check if user has enough coins to buy a lottery ticket
        if amount > income or amount < 1:
            await ctx.send("You do not have enough coins to buy a lottery ticket, or the ticket price must be at least 1 coin!")
            return

        winning_number = random.randint(1, 100)

        user_number = random.randint(1, 100)

        if user_number == winning_number:
            result = int(amount * 100)
            message = f"You won the lottery! Your prize is {result} coins!"
        else:
            result = -amount
            message = "Sorry, your number did not match the winning number. Better luck next time!"

        self.cursor.execute(
            "UPDATE users SET income=income+?, happiness=happiness-1, population=population-1 WHERE discord_id=?",
            (result, user_id),
        )
        self.connection.commit()

        # Update the last lottery time for this user
        self.user_last_lottery_time[user_id] = current_time

        # Send an embed with the lottery result
        embed = discord.Embed(title="Lottery Result", color=0x2a2d31)
        embed.set_author(name=ctx.author.name, icon_url=str(ctx.author.avatar.url))
        embed.add_field(name="Your ticket:", value=f"```{amount} coins```", inline=False)
        embed.add_field(name="Winning number:", value=f"```{winning_number}```", inline=False)
        embed.add_field(name="Your number:", value=f"```{user_number}```", inline=False)
        embed.add_field(name="Result:", value=f"```{message}```", inline=False)
        embed.add_field(name="New income:", value=f"```{income+result} coins```", inline=False)
        embed.set_footer(text="View documentation for all commands.")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Lottery(bot))
