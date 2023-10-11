import discord
from discord.ext import commands
import sqlite3

# Create database connection
conn = sqlite3.connect("partnership.db")
c = conn.cursor()

class SetPartners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
    async def setpartner(self, ctx, channel: discord.TextChannel):
        """Set Partnership Logging.
        
        Parameters
        -----------
        channel: channel
            Select the channel to enable partnership tracking.
        """
        c.execute("DELETE FROM partnership_channels WHERE guild_id=?", (ctx.guild.id,))
        c.execute("INSERT INTO partnership_channels (guild_id, channel_id) VALUES (?, ?)", (ctx.guild.id, channel.id,))
        conn.commit()
        await ctx.send(f"**Partnership channel set to {channel.mention}.**")

    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
    async def removepartner(self, ctx, channel: discord.TextChannel):
        """Remove Partnership Logging.
        
        Parameters
        -----------
        channel: channel
            Select the channel to remove from partnership tracking.
        """
        c.execute("DELETE FROM partnership_channels WHERE guild_id=? AND channel_id=?", (ctx.guild.id, channel.id))
        conn.commit()
        await ctx.send(f"**Partnership channel removed from {channel.mention}.**")

async def setup(bot):
    await bot.add_cog(SetPartners(bot))
