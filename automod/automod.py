import discord
from discord.ext import commands
import sqlite3
import asyncio

class SettingsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('automod.db')  # replace with your database name

    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
    async def automod(self, ctx):
        """View The New Automatic Moderation Configuration!"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM server_settings WHERE server_id = ?", (ctx.guild.id,))
        server_settings = cursor.fetchone()
        cursor.execute("SELECT * FROM caps_filter_settings WHERE server_id = ?", (ctx.guild.id,))
        caps_settings = cursor.fetchone()
        cursor.execute("SELECT * FROM char_spam_settings WHERE server_id = ?", (ctx.guild.id,))
        char_settings = cursor.fetchone()
        cursor.execute("SELECT * FROM emoji_spam_settings WHERE server_id = ?", (ctx.guild.id,))
        emoji_settings = cursor.fetchone()
        cursor.execute("SELECT * FROM image_attachment_settings WHERE server_id = ?", (ctx.guild.id,))
        image_settings = cursor.fetchone()
        cursor.execute("SELECT * FROM discord_link_settings WHERE server_id = ?", (ctx.guild.id,))
        link_settings = cursor.fetchone()
        cursor.execute("SELECT * FROM link_filter_settings WHERE server_id = ?", (ctx.guild.id,))
        link_filter_settings = cursor.fetchone()
        cursor.execute("SELECT * FROM max_char_settings WHERE server_id = ?", (ctx.guild.id,))
        max_char_settings = cursor.fetchone()
        cursor.execute("SELECT * FROM mention_filter_settings WHERE server_id = ?", (ctx.guild.id,))
        mention_settings = cursor.fetchone()
        cursor.execute("SELECT * FROM spam_settings WHERE server_id = ?", (ctx.guild.id,))
        spam_settings = cursor.fetchone()

        embed = discord.Embed(
            title="Welcome To The New Automatic Moderation Wizard!",
            description="**Beta Release - 28/04/23**\nWelcome to `Vashlys` new artificial learning automatic moderation!",
            color=0x2a2d31
        )

        embed.add_field(
            name="`1)` /badwords",
            value="Enable or disable bad words.",
            inline=False
        )

        embed.add_field(
            name="`2)` /capsfilter ",
            value="Enable or disable & set the CAPS limit.",
            inline=False
        )

        embed.add_field(
            name="`3)` /charspam",
            value="Enable or disable & set the amount of character spam such as `aaaaaaaaa.`",
            inline=False
        )

        embed.add_field(
            name="`4)` /emojispam",
            value="Enable or disable & set the amount of emoji spam.",
            inline=False
        )

        embed.add_field(
            name="`5)` /imagefilter",
            value="Enable or disable & set the amount of image attachments per message.",
            inline=False
        )

        embed.add_field(
            name="`6)` /invitefilter",
            value="Enable or disable discord link blocking.",
            inline=False
        )

        embed.add_field(
            name="`7)` /linkfilter",
            value="Enable or disable link blocking.",
            inline=False
        )

        embed.add_field(
            name="`8)` /maxchar",
            value="Enable or disable the maximum characters per message and set the character limit that users can send in a message. For example, a 500-character limit means the total number of individual characters allowed, not 500 words.",
            inline=False
        )

        embed.add_field(
            name="`9)` /mentionfilter",
            value="Enable or disable max mentions per message & set the max mentions per message.",
            inline=False
        )

        embed.add_field(
            name="`10)` /spamfilter ",
            value="Enable or disable the spam filter - set the threshold and the interval time for activation. For example, if the threshold is set to 5 and the interval is set to 3 seconds, the bot will classify a user who sends 5 messages within 3 seconds as spamming and warn the target user.",
            inline=False
        )



        await ctx.send(embed=embed)


        settings_pages = [
            {'title': 'Swear Filter', 'enabled': bool(server_settings[1]), 'description': 'Filters out swear words in messages.'},
            {'title': 'Caps Filter', 'enabled': bool(caps_settings[1]), 'description': f'Filters messages with more than {caps_settings[2]} capital letters.'},
            {'title': 'Character Spam Filter', 'enabled': bool(char_settings[1]), 'description': f'Filters messages with more than {char_settings[2]} consecutive characters.'},
            {'title': 'Emoji Spam Filter', 'enabled': bool(emoji_settings[1]), 'description': f'Filters messages with more than {emoji_settings[2]} consecutive emojis.'},
            {'title': 'Image Attachment Filter', 'enabled': bool(image_settings[1]), 'description': f'Filters messages with more than {image_settings[2]} image attachments.'},
            {'title': 'Discord Link Filter', 'enabled': bool(link_settings[1]), 'description': 'Filters out links to Discord servers.'},
            {'title': 'Link Filter', 'enabled': bool(link_filter_settings[1]), 'description': 'Filters out links in messages.'},
            {'title': 'Max Character Limit', 'enabled': bool(max_char_settings[1]), 'description': f'Filters messages with more than {max_char_settings[2]} characters.'},
            {'title': 'Mention Filter', 'enabled': bool(mention_settings[1]), 'description': f'Filters messages with more than {mention_settings[2]} mentions.'},
            {'title': 'Spam Filter', 'enabled': bool(spam_settings[1]), 'description': f'Filters users who send more than {spam_settings[2]} messages within {spam_settings[3]} seconds.'},
        ]

        current_page = 0

        embed = self.create_embed(settings_pages[current_page])
        msg = await ctx.send(embed=embed)

        if len(settings_pages) > 1:
        # add reactions for pagination
            await msg.add_reaction('⬅️')
            await msg.add_reaction('➡️')

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in {'⬅️', '➡️'}

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=600.0, check=check)
            except Exception:
                # stop listening for reactions after 60 seconds
                break
            else:
                if str(reaction.emoji) == '➡️' and current_page < len(settings_pages) - 1:
                    current_page += 1
                    embed = self.create_embed(settings_pages[current_page])
                    await msg.edit(embed=embed)
                elif str(reaction.emoji) == '⬅️' and current_page > 0:
                    current_page -= 1
                    embed = self.create_embed(settings_pages[current_page])
                    await msg.edit(embed=embed)

    def create_embed(self, settings):
        embed = discord.Embed(title=settings['title'],  color=0x2a2d31)
        embed.add_field(name='Enabled', value=str(settings['enabled']))
        embed.add_field(name='Description', value=settings['description'], inline=False)
        return embed



async def setup(bot):
   await bot.add_cog(SettingsCog(bot))
