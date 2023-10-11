import discord
import re
import requests
import sqlite3
from discord.ext import commands
from datetime import datetime, timedelta

class SwearFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bad_words = self.load_bad_words()
        self.conn = sqlite3.connect("automod.db")
        self.create_table()
        self.server_settings_cache = {}

    def load_bad_words(self):
        bad_words_url = "https://www.cs.cmu.edu/~biglou/resources/bad-words.txt"
        response = requests.get(bad_words_url)
        words = response.text.split("\n")
        return [word.strip() for word in words]

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS server_settings (
                            server_id INTEGER PRIMARY KEY,
                            swear_filter_enabled INTEGER DEFAULT 0
                          )""")
        self.conn.commit()

    async def is_swear_filter_enabled(self, server_id):
        if server_id not in self.server_settings_cache:
            cursor = self.conn.cursor()
            cursor.execute("SELECT swear_filter_enabled FROM server_settings WHERE server_id = ?", (server_id,))
            result = cursor.fetchone()
            self.server_settings_cache[server_id] = result and result[0]
        return self.server_settings_cache[server_id]

    @commands.Cog.listener()
    async def on_ready(self):
        self.load_settings()

    def load_settings(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT server_id, swear_filter_enabled FROM server_settings")
        results = cursor.fetchall()
        for server_id, enabled in results:
            self.server_settings_cache[server_id] = enabled

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.author.guild_permissions.administrator:
            return

        if message.attachments:
            return

        if not await self.is_swear_filter_enabled(message.guild.id):
            return

        content = message.content.lower()
        for word in self.bad_words:
            if word and word.lower() in content.split():
                await message.delete()
                warning_msg = await message.channel.send(f"`{message.author.name} - please refrain from using inappropriate language.`")
                await warning_msg.delete(delay=5)  # delete after 5 seconds
                await message.author.timeout(timedelta(minutes=10), reason="Automod")
                break

    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
    async def badwords(self, ctx, enable: bool):
        """Enables or disables the swear filter for this server.
        Parameters
        -----------
        enable: enable
            Enable or disable the command.

        """
        cursor = self.conn.cursor()
        cursor.execute("REPLACE INTO server_settings (server_id, swear_filter_enabled) VALUES (?, ?)", (ctx.guild.id, enable))
        self.conn.commit()
        self.server_settings_cache[ctx.guild.id] = enable
        await ctx.send(f"`Swear filter has been {'enabled' if enable else 'disabled'}.`", ephemeral=True)


async def setup(bot):
    await bot.add_cog(SwearFilter(bot))
