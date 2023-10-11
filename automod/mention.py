import discord
import sqlite3
from discord.ext import commands
import asyncio
from datetime import timedelta

class MentionFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect("automod.db")
        self.create_table()
        self.server_settings_cache = {}

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS mention_filter_settings (
                            server_id INTEGER PRIMARY KEY,
                            enabled INTEGER DEFAULT 0,
                            max_mentions INTEGER DEFAULT 2
                          )""")
        self.conn.commit()

    async def get_server_settings(self, server_id):
        if server_id not in self.server_settings_cache:
            cursor = self.conn.cursor()
            cursor.execute("SELECT enabled, max_mentions FROM mention_filter_settings WHERE server_id = ?", (server_id,))
            result = cursor.fetchone()
            self.server_settings_cache[server_id] = result or (1, 3)
        return self.server_settings_cache[server_id]

    @commands.Cog.listener()
    async def on_ready(self):
        self.load_settings()

    def load_settings(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT server_id, enabled, max_mentions FROM mention_filter_settings")
        results = cursor.fetchall()
        for server_id, enabled, max_mentions in results:
            self.server_settings_cache[server_id] = (enabled, max_mentions)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.author.guild_permissions.administrator:
            return

        enabled, max_mentions = await self.get_server_settings(message.guild.id)

        if not enabled:
            return

        mentions = message.mentions
        if len(mentions) > max_mentions:
            await message.delete()
            await message.author.timeout(timedelta(minutes=10), reason="Automod")
            warning_msg = await message.channel.send(f"`{message.author.name} - please refrain from spamming mentions.`")
            await asyncio.sleep(5)  # wait for 5 seconds
            await warning_msg.delete()


    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
    async def mentionfilter(self, ctx, enable: bool, max_mentions: int):
        """Enables or disables the mention filter for this server and sets the max number of mentions.
        
        Parameters
        -----------
        enable: enable
            enable or disable the command.

        Parameters
        -----------
        max_mentions: max_mentions
            Set the max mentions per message.
        
        """
        cursor = self.conn.cursor()
        cursor.execute("REPLACE INTO mention_filter_settings (server_id, enabled, max_mentions) VALUES (?, ?, ?)", (ctx.guild.id, enable, max_mentions))
        self.conn.commit()
        self.server_settings_cache[ctx.guild.id] = (enable, max_mentions)
        await ctx.send(f"`Mention filter has been {'enabled' if enable else 'disabled'} and the max number of mentions has been set to {max_mentions}.`",  ephemeral=True)

async def setup(bot):
   await bot.add_cog(MentionFilter(bot))
