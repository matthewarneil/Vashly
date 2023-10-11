import discord
import sqlite3
from discord.ext import commands
import asyncio
from datetime import timedelta

class CharacterSpamFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect("automod.db")
        self.create_table()
        self.server_settings_cache = {}

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS char_spam_settings (
                            server_id INTEGER PRIMARY KEY,
                            enabled INTEGER DEFAULT 0,
                            char_limit INTEGER DEFAULT 5
                          )""")
        self.conn.commit()

    async def is_char_spam_filter_enabled(self, server_id):
        if server_id not in self.server_settings_cache:
            cursor = self.conn.cursor()
            cursor.execute("SELECT enabled, char_limit FROM char_spam_settings WHERE server_id = ?", (server_id,))
            result = cursor.fetchone()
            self.server_settings_cache[server_id] = result or (1, 5)
        return self.server_settings_cache[server_id][0]

    async def get_char_limit(self, server_id):
        if server_id not in self.server_settings_cache:
            await self.is_char_spam_filter_enabled(server_id)
        return self.server_settings_cache[server_id][1]

    @commands.Cog.listener()
    async def on_ready(self):
        self.load_settings()

    def load_settings(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT server_id, enabled, char_limit FROM char_spam_settings")
        results = cursor.fetchall()
        for server_id, enabled, char_limit in results:
            self.server_settings_cache[server_id] = (enabled, char_limit)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.author.guild_permissions.administrator:
            return

        if not await self.is_char_spam_filter_enabled(message.guild.id):
            return

        content = message.content.lower()
        char_limit = await self.get_char_limit(message.guild.id)
        repeated_chars = set()
        curr_char = None
        count = 0
        for char in content:
            if char == curr_char:
                count += 1
                if count > char_limit:
                    repeated_chars.add(char)
            else:
                count = 1
                curr_char = char
        if repeated_chars:
            await message.delete()
            await message.author.timeout(timedelta(minutes=10), reason="Automod")
            warning_msg = await message.channel.send(f"`{message.author.name} - please refrain from using excessive repeated characters in a row such as {', '.join(repeated_chars)}.`")
            await asyncio.sleep(5)  # wait for 5 seconds
            await warning_msg.delete()

    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
    async def charspam(self, ctx, enable: bool = None, limit: int = None):
        """Enables or disables the character spam filter and sets the character limit for this server.
         Parameters
        -----------
        enable: enable
            Enable or disable the command.

        Parameters
        -----------
        limit: limit
            Set the max amount of repeated characters.
        
        
        """
        cursor = self.conn.cursor()
        if enable is not None:
            cursor.execute("REPLACE INTO char_spam_settings (server_id, enabled) VALUES (?, ?)", (ctx.guild.id, int(enable)))
            self.conn.commit()
        self.server_settings_cache[ctx.guild.id] = (enable, await self.get_char_limit(ctx.guild.id))

        if limit is not None:
            cursor.execute("UPDATE char_spam_settings SET char_limit = ? WHERE server_id = ?", (limit, ctx.guild.id))
            self.conn.commit()
            self.server_settings_cache[ctx.guild.id] = (await self.is_char_spam_filter_enabled(ctx.guild.id), limit)

        enable_msg = f"`Character spam filter has been {'enabled' if enable else 'disabled'}.`" if enable is not None else ""
        limit_msg = f"`Character limit has been set to {limit}.`" if limit is not None else ""
        if msg := f"{enable_msg} {limit_msg}".strip():
            await ctx.send(msg, ephemeral=True)




async def setup(bot):
    await bot.add_cog(CharacterSpamFilter(bot))
