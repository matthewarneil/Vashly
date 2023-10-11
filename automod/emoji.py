import discord
import sqlite3
import regex
import asyncio
from discord.ext import commands
from datetime import timedelta

class EmojiSpamBlocker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect("automod.db")
        self.create_table()
        self.server_settings_cache = {}

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS emoji_spam_settings (
                            server_id INTEGER PRIMARY KEY,
                            enabled INTEGER DEFAULT 0,
                            emoji_limit INTEGER DEFAULT 5
                          )""")
        self.conn.commit()

    async def is_emoji_spam_filter_enabled(self, server_id):
        if server_id not in self.server_settings_cache:
            cursor = self.conn.cursor()
            cursor.execute("SELECT enabled, emoji_limit FROM emoji_spam_settings WHERE server_id = ?", (server_id,))
            result = cursor.fetchone()
            self.server_settings_cache[server_id] = result or (1, 5)
        return self.server_settings_cache[server_id][0]

    async def get_emoji_limit(self, server_id):
        if server_id not in self.server_settings_cache:
            await self.is_emoji_spam_filter_enabled(server_id)
        return self.server_settings_cache[server_id][1]

    @commands.Cog.listener()
    async def on_ready(self):
        self.load_settings()

    def load_settings(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT server_id, enabled, emoji_limit FROM emoji_spam_settings")
        results = cursor.fetchall()
        for server_id, enabled, emoji_limit in results:
            self.server_settings_cache[server_id] = (enabled, emoji_limit)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.author.guild_permissions.administrator:
            return

        if not await self.is_emoji_spam_filter_enabled(message.guild.id):
            return

        emoji_count = sum(bool(regex.match(r'\p{So}', c))
                      for c in message.content)
        emoji_limit = await self.get_emoji_limit(message.guild.id)
        if emoji_count > emoji_limit:
            await message.delete()
            await message.author.timeout(timedelta(minutes=10), reason="Automod")
            warning_msg = await message.channel.send(f"`{message.author.name} - please refrain from using a high amount of emojis.`")
            await asyncio.sleep(5)  # wait for 5 seconds
            await warning_msg.delete()


    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
    async def emojispam(self, ctx, enable: bool, emoji_limit: int):
        """Enables or disables the emoji spam filter for this server and sets the max emoji limit.
        
        Parameters
        -----------
        enable: enable
            enable or disable the command.

        Parameters
        -----------
        emoji_limit: emoji_limit
            Set the max amount of emojis.
        """
        cursor = self.conn.cursor()
        cursor.execute("REPLACE INTO emoji_spam_settings (server_id, enabled, emoji_limit) VALUES (?, ?, ?)", (ctx.guild.id, enable, emoji_limit))
        self.conn.commit()
        self.server_settings_cache[ctx.guild.id] = (enable, emoji_limit)
        await ctx.send(f"`Emoji spam filter has been {'enabled' if enable else 'disabled'} and the max emoji limit has been set to {emoji_limit}.`", ephemeral=True)


async def setup(bot):
   await bot.add_cog(EmojiSpamBlocker(bot))
