import discord
import sqlite3
from discord.ext import commands
import asyncio
from datetime import timedelta

class CapsFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect("automod.db")
        self.create_table()
        self.server_settings_cache = {}

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS caps_filter_settings (
                            server_id INTEGER PRIMARY KEY,
                            enabled INTEGER DEFAULT 0,
                            caps_limit INTEGER DEFAULT 10
                          )""")
        self.conn.commit()

    async def is_caps_filter_enabled(self, server_id):
        if server_id not in self.server_settings_cache:
            cursor = self.conn.cursor()
            cursor.execute("SELECT enabled, caps_limit FROM caps_filter_settings WHERE server_id = ?", (server_id,))
            result = cursor.fetchone()
            self.server_settings_cache[server_id] = result or (1, 10)
        return self.server_settings_cache[server_id][0]

    async def get_caps_limit(self, server_id):
        if server_id not in self.server_settings_cache:
            await self.is_caps_filter_enabled(server_id)
        return self.server_settings_cache[server_id][1]

    @commands.Cog.listener()
    async def on_ready(self):
        self.load_settings()

    def load_settings(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT server_id, enabled, caps_limit FROM caps_filter_settings")
        results = cursor.fetchall()
        for server_id, enabled, caps_limit in results:
            self.server_settings_cache[server_id] = (enabled, caps_limit)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.author.guild_permissions.administrator:
            return

        if not await self.is_caps_filter_enabled(message.guild.id):
            return

        content = message.content
        caps_limit = await self.get_caps_limit(message.guild.id)
        if content.isupper() and len(content) > caps_limit:
            await message.delete()
            warning_msg = await message.channel.send(f"`{message.author.name} - please refrain from using excessive caps.`")
            await asyncio.sleep(5)  # wait for 5 seconds
            await warning_msg.delete()
            await message.author.timeout(timedelta(minutes=10), reason="Excessive use of capital letters")

    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
    async def capsfilter(self, ctx, enable: bool = None, limit: int = None):
        """Enables or disables the caps filter and sets the caps limit for this server.
        Parameters
        -----------
        enable: enable
            Enable or disable the command.
        
        Parameters
        -----------
        limit: limit
            The max amount of capital letters.
        
        """
        if enable is not None:
            cursor = self.conn.cursor()
            cursor.execute("REPLACE INTO caps_filter_settings (server_id, enabled) VALUES (?, ?)", (ctx.guild.id, int(enable)))
            self.conn.commit()
            self.server_settings_cache[ctx.guild.id] = (enable, await self.get_caps_limit(ctx.guild.id))

        if limit is not None:
            cursor = self.conn.cursor()
            cursor.execute("REPLACE INTO caps_filter_settings (server_id, caps_limit) VALUES (?, ?)", (ctx.guild.id, limit))
            self.conn.commit()
            self.server_settings_cache[ctx.guild.id] = (await self.is_caps_filter_enabled(ctx.guild.id), limit)

        enable_msg = f"`Caps filter has been {'enabled' if enable else 'disabled'}.`" if enable is not None else ""
        limit_msg = f"`Caps limit has been set to {limit}.`" if limit is not None else ""
        if msg := f"{enable_msg} {limit_msg}".strip():
            await ctx.send(msg, ephemeral=True)

async def setup(bot):
    await bot.add_cog(CapsFilter(bot))
