import discord
import json
import random
import requests
from discord.ext import commands

class news(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def news(self, ctx):
        """Shows the latest crypto news."""
        # Enter your NewsAPI key
        api_key = ''
        url = f'https://newsapi.org/v2/everything?q=cryptocurrency&sortBy=publishedAt&apiKey={api_key}'
        response = requests.get(url)
        news = json.loads(response.text)

        if news['status'] == 'ok':
            articles = news['articles'][:5]  # limit to 5 articles
            embed = discord.Embed(title="Crypto News", color=0x2a2d31)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            for article in articles:
                title = article['title']
                url = article['url']
                embed.add_field(name=title, value=url, inline=False)
                embed.set_footer(text="View documentation for all commands.")
            await ctx.send(embed=embed)
        else:
            await ctx.send("Sorry, something went wrong while fetching the news.")

async def setup(bot):
    await bot.add_cog(news(bot))
