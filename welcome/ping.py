from discord.ext import commands
import discord
import sqlite3
import asyncio

class PingOnJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('welcome.db')
        self.c = self.conn.cursor()
        self.c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            guild_id INTEGER PRIMARY KEY,
            status INTEGER,
            channel_id INTEGER
        )
        ''')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = member.guild.id
        self.c.execute('SELECT status, channel_id FROM settings WHERE guild_id = ?', (guild_id,))
        setting = self.c.fetchone()
        if setting is None or setting[0] == 0:
            return
        channel = self.bot.get_channel(setting[1])
        if channel is None:
            return
        message = await channel.send(f'{member.mention}')
        await asyncio.sleep(2)
        await message.delete()

    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
    async def ghostping(self, ctx, status: str, channel: discord.TextChannel = None):
        """ping on join.
        
        Parameters
        -----------
        status: status
            enable or disable the ping.
        
        Parameters
        -----------
        channel: channel
            Select the channel for the ghost-ping.
        
        """
        guild_id = ctx.guild.id
        if status.lower() not in ['enabled', 'disabled']:
            await ctx.send("`Invalid status. Use enabled or disabled.`",  ephemeral=True)
            return

        new_status = 1 if status.lower() == 'enabled' else 0
        self.c.execute('SELECT status, channel_id FROM settings WHERE guild_id = ?', (guild_id,))
        setting = self.c.fetchone()

        if setting is None:
            self.c.execute('INSERT INTO settings VALUES (?, ?, ?)', (guild_id, new_status, channel.id if channel else None))
        else:
            self.c.execute('UPDATE settings SET status = ?, channel_id = ? WHERE guild_id = ?', 
                           (new_status, channel.id if channel else setting[1], guild_id))
        self.conn.commit()

        await ctx.send(f"`The ping upon joining is {status}" + (f" in the {channel.name} channel!`" if channel else ""), ephemeral=True)

async def setup(bot):
    await bot.add_cog(PingOnJoin(bot))
