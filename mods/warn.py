import discord
import sqlite3
from discord.ext import commands

class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            self.conn = sqlite3.connect('warn.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS warnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    moderator_id INTEGER,
                    guild_id INTEGER,
                    reason TEXT
                )
            ''')
            self.conn.commit()
        except Exception as e:
            print(f"An error occurred while creating the table: {e}")

    @commands.hybrid_command()
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str):
        """Warns a user and stores the warning in a database.
        
        Parameters
        -----------
        member: member
            Select the member to warn.

        Parameters
        -----------
        reason: reason
            Write the reason for the warn.
        """
        try:
            self.cursor.execute('''
                INSERT INTO warnings (user_id, moderator_id, guild_id, reason)
                VALUES (?, ?, ?, ?)
            ''', (member.id, ctx.author.id, ctx.guild.id, reason))
            self.conn.commit()

            embed = discord.Embed(title='User Warned', description=f'{member.mention} has been warned by - {ctx.author.mention}.\n\nA warning is an official notice from the server staff that a user has broken a rule. If a user receives multiple warnings, they may be kicked or banned from the server.', color=0x2a2d31)
            embed.add_field(name='Reason', value=reason)
            embed.set_footer(text="View documentation for all commands.")
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)

            dm_embed = discord.Embed(title='You have been warned', description=f'You have been warned by - {ctx.author.mention}.\n\nA warning is an official notice from the server staff that you have broken a rule. Please take this as a reminder to follow the rules to avoid further consequences.', color=0x2a2d31)
            dm_embed.add_field(name='Reason', value=reason)
            embed.set_footer(text="View documentation for all commands.")
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            await member.send(embed=dm_embed)
        except Exception as e:
            print(f"An error occurred while warning the user: {e}")

async def setup(bot):
    try:
        await bot.add_cog(Warn(bot))
    except Exception as e:
        print(f"An error occurred while setting up the Warn cog: {e}")
