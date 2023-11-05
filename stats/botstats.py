import discord
from discord.ext import commands

class BotStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    @commands.is_owner()
    async def botstats(self, ctx):
        """Displays various statistics of the bot."""
        total_servers = len(self.bot.guilds)
        total_members = len(self.bot.users)
        total_online_members = sum(
            member.status != discord.Status.offline
            for member in self.bot.get_all_members()
        )
        total_text_channels = sum(len(server.text_channels) for server in self.bot.guilds)
        total_voice_channels = sum(len(server.voice_channels) for server in self.bot.guilds)
        max_members = 0
        max_server = None

        for server in self.bot.guilds:
            if server.member_count > max_members:
                max_members = server.member_count
                max_server = server

        stats_embed = discord.Embed(title="Bot Statistics", description="```Please make certain to maintain the secrecy of our privacy guidelines by privately examining the bot's metrics provided here.```", color=0x2a2d31)
        stats_embed.add_field(name="Total Servers", value=str(total_servers), inline=False)
        stats_embed.add_field(name="Total Members", value=str(total_members), inline=False)
        stats_embed.add_field(name="Text Channels", value=str(total_text_channels), inline=False)
        stats_embed.add_field(name="Voice Channels", value=str(total_voice_channels), inline=False)
        stats_embed.add_field(name="Most Members", value=f"{max_server.name} ({max_members} members)", inline=False)

        await ctx.send(embed=stats_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(BotStats(bot))
