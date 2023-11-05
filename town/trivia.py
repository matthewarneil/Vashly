import discord
from discord.ext import commands
import sqlite3
import random
import time
import requests
import html

class Trivia(commands.Cog):
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
        self.user_last_trivia_time = {}

    def user_exists(self, discord_id):
        self.cursor.execute("SELECT discord_id FROM users WHERE discord_id=?", (discord_id,))
        return self.cursor.fetchone() is not None

    def add_user(self, discord_id):
        self.cursor.execute("INSERT INTO users (discord_id, population, income, happiness, infrastructure) VALUES (?, 0, 0, 0, 0)", (discord_id,))
        self.connection.commit()

    @commands.hybrid_command()
    @commands.cooldown(1, 300, commands.BucketType.user)  # 5 minutes cooldown per user
    async def trivia(self, ctx):
        """Answer a trivia question to gain coins."""
        embed = discord.Embed(title="Trivia", color=0x2a2d31)
        current_time = time.time()
        last_trivia_time = self.user_last_trivia_time.get(ctx.author.id, 0)
        if current_time - last_trivia_time < 300:  # 300 seconds = 5 minutes
            embed.description = "`You can only play trivia once every 5 minutes!`"
            embed.set_footer(text="View documentation for all commands.")
            await ctx.send(embed=embed)
            return

        response = requests.get("https://opentdb.com/api.php?amount=1&type=multiple")
        if response.status_code == 200:
            data = response.json()
            if data["response_code"] == 0:
                question = html.unescape(data["results"][0]["question"])
                correct_answer = html.unescape(data["results"][0]["correct_answer"])
                incorrect_answers = [html.unescape(answer) for answer in data["results"][0]["incorrect_answers"]]

                answers = incorrect_answers + [correct_answer]
                random.shuffle(answers)

                options = "\n".join([f"{chr(65+i)}. {answer}" for i, answer in enumerate(answers)])

                embed.add_field(name="Question", value=question, inline=False)
                embed.add_field(name="Options", value=options, inline=False)
                embed.set_footer(text="View documentation for all commands.")
                embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
                await ctx.send(embed=embed)

                def check_answer(msg):
                    return msg.author == ctx.author and msg.channel == ctx.channel

                try:
                    msg = await self.bot.wait_for("message", check=check_answer, timeout=30)
                except TimeoutError:
                    embed.description = "`You took too long to answer!`"
                    embed.set_footer(text="View documentation for all commands.")
                    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
                    await ctx.send(embed=embed)
                    return

                user_answer = msg.content.strip().upper()
                correct_index = answers.index(correct_answer)
                correct_option = chr(65 + correct_index)

                if user_answer == correct_option:
                    coins_gained = random.randint(10, 20)
                    try:
                        self.cursor.execute(
                            "UPDATE users SET income=income+?, happiness=happiness+1, population=population+1 WHERE discord_id=?",
                            (coins_gained, str(ctx.author.id)),
                        )
                        self.connection.commit()
                        embed.description = f"✅ Correct! You gained `{coins_gained}` coins! Your new balance is `{self.get_user_balance(ctx.author.id)}` coins. Your happiness and population increased by 1."
                    except Exception as e:
                        print(f"Error updating user balance: {e}")
                        embed.description = "`Sorry, there was an error updating your balance. Please try again later`"
                        embed.set_footer(text="View documentation for all commands.")
                        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
                else:
                    embed.description = f"❌ Wrong answer! The correct answer was `{correct_option}`. You didn't gain any coins."
                    embed.set_footer(text="View documentation for all commands.")
                self.user_last_trivia_time[ctx.author.id] = current_time
                embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
                await ctx.send(embed=embed)
            else:
                embed.description = "`Failed to fetch a trivia question. Please try again later.`"
                embed.set_footer(text="View documentation for all commands.")
                embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
                await ctx.send(embed=embed)
        else:
            embed.set_footer(text="View documentation for all commands.")
            embed.description = "`Failed to fetch a trivia question. Please try again later.`"
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)

    def get_user_balance(self, discord_id):
        """Get the current balance of a user."""
        self.cursor.execute("SELECT income FROM users WHERE discord_id=?", (str(discord_id),))
        row = self.cursor.fetchone()
        return row[0] if row is not None else 0


async def setup(bot):
    await bot.add_cog(Trivia(bot))
