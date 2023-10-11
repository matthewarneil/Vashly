import discord
import sqlite3
import re
from discord.ext import commands
import asyncio
from datetime import timedelta

class LinkFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect("automod.db")
        self.create_table()
        self.server_settings_cache = {}

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS link_filter_settings (
                            server_id INTEGER PRIMARY KEY,
                            enabled INTEGER DEFAULT 0
                          )""")
        self.conn.commit()

    async def is_link_filter_enabled(self, server_id):
        if server_id not in self.server_settings_cache:
            cursor = self.conn.cursor()
            cursor.execute("SELECT enabled FROM link_filter_settings WHERE server_id = ?", (server_id,))
            result = cursor.fetchone()
            self.server_settings_cache[server_id] = result[0] if result else 1
        return self.server_settings_cache[server_id]

    @commands.Cog.listener()
    async def on_ready(self):
        self.load_settings()

    def load_settings(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT server_id, enabled FROM link_filter_settings")
        results = cursor.fetchall()
        for server_id, enabled in results:
            self.server_settings_cache[server_id] = enabled

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.author.guild_permissions.administrator:
            return

        if not await self.is_link_filter_enabled(message.guild.id):
            return

        if re.search("(?P<url>https?://[^\s]+)", message.content):
            await message.delete()
            await message.author.timeout(timedelta(minutes=10), reason="Automod")
            warning_msg = await message.channel.send(f"`{message.author.name} - please refrain from sending links.`")
            await asyncio.sleep(5)  # wait for 5 seconds
            await warning_msg.delete()


    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
    async def linkfilter(self, ctx, enable: bool):
        """Enables or disables the link filter for this server.
        
        Parameters
        -----------
        enable: enable
            enable or disable the command.
        
        
        """
        cursor = self.conn.cursor()
        cursor.execute("REPLACE INTO link_filter_settings (server_id, enabled) VALUES (?, ?)", (ctx.guild.id, enable))
        self.conn.commit()
        self.server_settings_cache[ctx.guild.id] = enable
        await ctx.send(f"`Link filter has been {'enabled' if enable else 'disabled'}.`", ephemeral=True)


async def setup(bot):
   await bot.add_cog(LinkFilter(bot))
