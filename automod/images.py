import discord
import sqlite3
from discord.ext import commands
import asyncio
from datetime import timedelta

class ImageAttachmentFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect("automod.db")
        self.create_table()
        self.server_settings_cache = {}

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS image_attachment_settings (
                            server_id INTEGER PRIMARY KEY,
                            enabled INTEGER DEFAULT 0,
                            image_limit INTEGER DEFAULT 3
                          )""")
        self.conn.commit()

    async def is_image_attachment_filter_enabled(self, server_id):
        if server_id not in self.server_settings_cache:
            cursor = self.conn.cursor()
            cursor.execute("SELECT enabled, image_limit FROM image_attachment_settings WHERE server_id = ?", (server_id,))
            result = cursor.fetchone()
            self.server_settings_cache[server_id] = result or (1, 3)
        return self.server_settings_cache[server_id][0]

    async def get_image_limit(self, server_id):
        if server_id not in self.server_settings_cache:
            await self.is_image_attachment_filter_enabled(server_id)
        return self.server_settings_cache[server_id][1]

    @commands.Cog.listener()
    async def on_ready(self):
        self.load_settings()

    def load_settings(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT server_id, enabled, image_limit FROM image_attachment_settings")
        results = cursor.fetchall()
        for server_id, enabled, image_limit in results:
            self.server_settings_cache[server_id] = (enabled, image_limit)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.author.guild_permissions.administrator:
            return

        if not await self.is_image_attachment_filter_enabled(message.guild.id):
            return

        image_limit = await self.get_image_limit(message.guild.id)
        if len(message.attachments) > image_limit:
            await message.delete()
            await message.author.timeout(timedelta(minutes=10), reason="Automod")
            warning_msg = await message.channel.send(f"`{message.author.name} - please refrain from sending more than {image_limit} images in one message.`")
            await asyncio.sleep(5)  # wait for 5 seconds
            await warning_msg.delete()


    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
    async def imagefilter(self, ctx, enable: bool, image_limit: int):
        """Enables or disables the image attachment filter for this server and sets the max image limit.
        
        Parameters
        -----------
        enable: enable
            enable or disable the command.

        Parameters
        -----------
        image_limit: image_limit
            Set the max amount of images a user can send.
        
        
        """
        cursor = self.conn.cursor()
        cursor.execute("REPLACE INTO image_attachment_settings (server_id, enabled, image_limit) VALUES (?, ?, ?)", (ctx.guild.id, enable, image_limit))
        self.conn.commit()
        self.server_settings_cache[ctx.guild.id] = (enable, image_limit)
        await ctx.send(f"`Image attachment filter has been {'enabled' if enable else 'disabled'} and the max image limit has been set to {image_limit}.`", ephemeral=True)



async def setup(bot):
    await bot.add_cog(ImageAttachmentFilter(bot))
