import discord
import sqlite3
from discord.ext import commands
import asyncio
from datetime import timedelta

class Spam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect("automod.db")
        self.create_table()
        self.server_settings_cache = {}
        self.last_message_times = {}

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS spam_settings (
                            server_id INTEGER PRIMARY KEY,
                            enabled INTEGER DEFAULT 0,
                            spam_threshold INTEGER DEFAULT 3,
                            spam_time_interval INTEGER DEFAULT 1
                          )""")
        self.conn.commit()

    async def get_server_settings(self, server_id):
        if server_id not in self.server_settings_cache:
            cursor = self.conn.cursor()
            cursor.execute("SELECT enabled, spam_threshold, spam_time_interval FROM spam_settings WHERE server_id = ?", (server_id,))
            result = cursor.fetchone()
            self.server_settings_cache[server_id] = result or (1, 3, 1)
        return self.server_settings_cache[server_id]

    @commands.Cog.listener()
    async def on_ready(self):
        self.load_settings()

    def load_settings(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT server_id, enabled, spam_threshold, spam_time_interval FROM spam_settings")
        results = cursor.fetchall()
        for server_id, enabled, spam_threshold, spam_time_interval in results:
            self.server_settings_cache[server_id] = (enabled, spam_threshold, spam_time_interval)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.author.guild_permissions.administrator:
            return

        enabled, spam_threshold, spam_time_interval = await self.get_server_settings(message.guild.id)

        if not enabled:
            return

        author_id = message.author.id

        if author_id in self.last_message_times:
            time_diff = message.created_at.timestamp() - self.last_message_times[author_id]['timestamp']
            if time_diff < spam_time_interval:
                spam_count = self.last_message_times[author_id]['spam_count'] + 1
                self.last_message_times[author_id]['spam_count'] = spam_count
                
                if spam_count >= spam_threshold:
                    async for msg in message.channel.history(limit=spam_count):
                        if msg.author == message.author:
                            await msg.delete()

                    warning_msg = await message.channel.send(f"`{message.author.name} - please refrain from spamming.`")
                    await asyncio.sleep(5)
                    await message.author.timeout(timedelta(minutes=10), reason="Automod")
                    await warning_msg.delete()
                    
                    self.last_message_times[author_id]['spam_count'] = 1
                    self.last_message_times[author_id]['timestamp'] = message.created_at.timestamp()

                    return
            else:
                self.last_message_times[author_id]['spam_count'] = 1
                self.last_message_times[author_id]['timestamp'] = message.created_at.timestamp()
        else:
            self.last_message_times[author_id] = {'timestamp': message.created_at.timestamp(), 'spam_count': 1}



    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
    async def spamfilter(self, ctx, enable: bool, threshold: int, interval: int):
        """Enables or disables the spam filter, and allows adjusting the spam threshold and time interval.
        
        Parameters
        -----------
        enable: enable
            enable or disable the command.
        
        Parameters
        -----------
        threshold: threshold
            Set the amount of messages for it to be activated.

        Parameters
        -----------
        interval: interval
            Set the interval (seconds) between messages for it to be classed as spam.
        """
        cursor = self.conn.cursor()
        cursor.execute("REPLACE INTO spam_settings (server_id, enabled, spam_threshold, spam_time_interval) VALUES (?, ?, ?, ?)", (ctx.guild.id, enable, threshold, interval))
        self.conn.commit()
        self.server_settings_cache[ctx.guild.id] = (enable, threshold, interval)
        await ctx.send(f"`Spam filter has been {'enabled' if enable else 'disabled'}. Threshold: {threshold}. Interval: {interval}`", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Spam(bot))
