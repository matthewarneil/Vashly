import discord
import random
import sqlite3
from discord.ext import commands

conn = sqlite3.connect('messaging.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        user_id INTEGER,
        guild_id INTEGER,
        message_count INTEGER,
        PRIMARY KEY (user_id, guild_id)
    )
''')
conn.commit()

class MessageCounter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guilds = set()

    @commands.Cog.listener()
    async def on_message(self, message):
        # ignore messages from bots
        if message.author.bot:
            return

        # ignore messages from untracked guilds
        if message.guild.id not in self.guilds:
            return

        # update the user's message count in the database
        cursor.execute('''
            INSERT OR IGNORE INTO messages (user_id, guild_id, message_count)
            VALUES (?, ?, 1)
        ''', (message.author.id, message.guild.id))

        cursor.execute('''
            UPDATE messages
            SET message_count = message_count + 1
            WHERE user_id = ? AND guild_id = ?
        ''', (message.author.id, message.guild.id))

        conn.commit()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.guilds.add(guild.id)

async def setup(bot):
    message_counter = MessageCounter(bot)
    for guild in bot.guilds:
        message_counter.guilds.add(guild.id)
    await bot.add_cog(message_counter)

