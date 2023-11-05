import discord
from discord.ext import commands
import sqlite3
import random

class TownStatus(commands.Cog):
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

    @commands.hybrid_command()
    async def townstatus(self, ctx):
        """Display the town's statistics and perform checks."""
        embed = discord.Embed(title="Town Status", color=0x2a2d31)

        # Fetch user's statistics from the database
        self.cursor.execute("SELECT population, income, happiness, infrastructure FROM users WHERE discord_id=?", (ctx.author.id,))
        row = self.cursor.fetchone()
        if row is None:
            # User does not exist in the database
            embed.description = "`You are not registered as a town resident.`"
            await ctx.send(embed=embed)
            return

        population, income, happiness, infrastructure = row

        # Check and update balance if negative
        if income < 0:
            income = 0
            self.cursor.execute("UPDATE users SET income=0 WHERE discord_id=?", (ctx.author.id,))
            self.connection.commit()

        # Check happiness and population
        if happiness > 5 or happiness < 5 or population > 5 or population < 5:
            # User needs to solve a complex math question or lose 500 coins
            question_number1 = random.randint(1, 10)
            question_number2 = random.randint(1, 10)
            operation = random.choice(['+', '-'])
            question = f"`Solve the following question: {question_number1} {operation} {question_number2}!`"
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            embed.add_field(name="Act swiftly and resolve the question to safeguard your town!", value=question, inline=False)
            await ctx.send(embed=embed)

            def check_answer(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel

            try:
                msg = await self.bot.wait_for("message", check=check_answer, timeout=30)
            except TimeoutError:
                embed.description = "`You took too long to answer! 500 coins have been deducted.`"
                await ctx.send(embed=embed)
                self.cursor.execute("UPDATE users SET income=income-500 WHERE discord_id=?", (ctx.author.id,))
                self.connection.commit()
                return

            try:
                user_answer = int(msg.content)
            except ValueError:
                embed.description = "`Invalid answer. 500 coins have been deducted.`"
                await ctx.send(embed=embed)
                self.cursor.execute("UPDATE users SET income=income-500 WHERE discord_id=?", (ctx.author.id,))
                self.connection.commit()
                return

            correct_answer = question_number1 + question_number2 if operation == '+' else question_number1 - question_number2
            if user_answer == correct_answer:
                embed.description = "`Correct answer!`"
                await ctx.send(embed=embed)
            else:
                embed.description = "`Wrong answer. 500 coins have been deducted.`"
                await ctx.send(embed=embed)
                self.cursor.execute("UPDATE users SET income=income-500 WHERE discord_id=?", (ctx.author.id,))
                self.connection.commit()

        # Update the embed with the user's statistics
        embed.add_field(name="Population", value=str(population), inline=True)
        embed.add_field(name="Income", value=str(income), inline=True)
        embed.add_field(name="Happiness", value=str(happiness), inline=True)
        embed.add_field(name="Infrastructure", value=str(infrastructure), inline=True)

        house_level = infrastructure  # Assuming house level corresponds to infrastructure level
        house_image_url = f"https://vashly.com/wp-content/uploads/2023/06/house-{house_level}.png"
        embed.set_image(url=house_image_url)
        embed.set_footer(text="Your population and happiness should fall within the range of zero to five.")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TownStatus(bot))
