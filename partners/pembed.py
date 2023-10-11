import discord
from discord.ext import commands
import sqlite3
import re
import random

# Create database connection and table
conn = sqlite3.connect("partnership.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    guild_id INTEGER,
    user_id INTEGER,
    points INTEGER
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS partnership_channels (
    id INTEGER PRIMARY KEY,
    guild_id INTEGER,
    channel_id INTEGER
)
""")

# Create a table for the embed settings
c.execute("""
CREATE TABLE IF NOT EXISTS embed_settings (
    id INTEGER PRIMARY KEY,
    guild_id INTEGER,
    title TEXT,
    description TEXT
)
""")

conn.commit()

class Pembed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
    async def pembed(self, ctx, title: str, description: str):
        """Edit partnership tracking embed.

        Parameters
        -----------
        title: title
            Edit embed title: You can use: {user} = username {points} = partnership points.

        Parameters
        -----------
        description: description
            Edit embed description: You can use: {user} = username {points} = partnership points {line} = paragraph indents.
        """
        c.execute("SELECT id FROM embed_settings WHERE guild_id=?", (ctx.guild.id,))
        row = c.fetchone()

        if row is None:
            c.execute("INSERT INTO embed_settings (guild_id, title, description) VALUES (?, ?, ?)", (ctx.guild.id, title, description))
        else:
            c.execute("UPDATE embed_settings SET title=?, description=? WHERE guild_id=?", (title, description, ctx.guild.id))

        conn.commit()
        await ctx.send("**Partnership embed message has been updated.**")


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        c.execute("SELECT channel_id FROM partnership_channels WHERE guild_id=?", (message.guild.id,))
        channels = [row[0] for row in c.fetchall()]

        if message.channel.id in channels:
            if not re.search(r"(https?://)?(www\.)?(discord(\.|\.gg)|invite\.)\S+", message.content):
                return

            c.execute("SELECT id, points FROM users WHERE user_id=? AND guild_id=?", (message.author.id, message.guild.id))
            if row := c.fetchone():
                user_id, points = row
                points += 1
                c.execute("UPDATE users SET points=? WHERE id=?", (points, user_id))
            else:
                points = 1
                c.execute("INSERT INTO users (user_id, guild_id, points) VALUES (?, ?, ?)", (message.author.id, message.guild.id, points))

            conn.commit()

            # Fetch the custom embed settings from the database
            c.execute("SELECT title, description FROM embed_settings WHERE guild_id=?", (message.guild.id,))
            if row := c.fetchone():
                title, description = row
            else:
                # If there's no custom settings, use the default ones
                title = "🔥 Thanks For Partnering!"
                description = "Thanks `{user}` - This server partnership has been recorded. \n\nYou now have `{points}` partnership points!"

            # Replace placeholders with actual values
            title = title.replace("{user}", message.author.name).replace("{points}", str(points))
            description = description.replace("{user}", message.author.name).replace("{points}", str(points))
            
            # Replace "{line}" with "\n\n" to create a space
            description = description.replace("{line}", "\n\n")

            embed = discord.Embed(title=title, description=description, color=0x2a2d31)
            await message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Pembed(bot))
