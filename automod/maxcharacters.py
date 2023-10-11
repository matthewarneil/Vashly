import discord
import sqlite3
from discord.ext import commands
import asyncio
from datetime import timedelta

class MaxCharFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect("automod.db")
        self.create_table()
        self.server_settings_cache = {}

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS max_char_settings (
                            server_id INTEGER PRIMARY KEY,
                            enabled INTEGER DEFAULT 0,
                            max_chars INTEGER DEFAULT 500
                          )""")
        self.conn.commit()

    async def get_server_settings(self, server_id):
        if server_id not in self.server_settings_cache:
            cursor = self.conn.cursor()
            cursor.execute("SELECT enabled, max_chars FROM max_char_settings WHERE server_id = ?", (server_id,))
            result = cursor.fetchone()
            self.server_settings_cache[server_id] = result or (1, 500)
        return self.server_settings_cache[server_id]

    @commands.Cog.listener()
    async def on_ready(self):
        self.load_settings()

    def load_settings(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT server_id, enabled, max_chars FROM max_char_settings")
        results = cursor.fetchall()
        for server_id, enabled, max_chars in results:
            self.server_settings_cache[server_id] = (enabled, max_chars)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.author.guild_permissions.administrator:
            return

        enabled, max_chars = await self.get_server_settings(message.guild.id)

        if not enabled:
            return

        if len(message.content) > max_chars:
            await message.delete()
            await message.author.timeout(timedelta(minutes=10), reason="Automod")
            warning_msg = await message.channel.send(f"`{message.author.name} - please limit your message to {max_chars} characters.`")
            await asyncio.sleep(5)
            await warning_msg.delete()


    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
    async def maxchar(self, ctx, enable: bool, max_chars: int):
        """Enables or disables the max character limit for messages in this server.
        
        Parameters
        -----------
        enable: enable
            enable or disable the command.
        
        Parameters
        -----------
        max_chars: max_chars
            Set the max amount of characters per message.
        
        """
        cursor = self.conn.cursor()
        cursor.execute("REPLACE INTO max_char_settings (server_id, enabled, max_chars) VALUES (?, ?, ?)", (ctx.guild.id, enable, max_chars))
        self.conn.commit()
        self.server_settings_cache[ctx.guild.id] = (enable, max_chars)
        await ctx.send(f"`Max character filter has been {'enabled' if enable else 'disabled'} and the max character limit has been set to {max_chars}.`", ephemeral=True)


async def setup(bot):
    await bot.add_cog(MaxCharFilter(bot))
