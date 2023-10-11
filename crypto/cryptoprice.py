api_key = ''


import discord
import random
import requests
from discord.ext import commands

class cprice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def cprice(self, ctx, symbol: str=None):
        """Displays the latest price and change in value for a given cryptocurrency symbol.
        
        Parameters
        -----------
        symbol: symbol
            Choose the symbol to search (example: BTC).
        
        """
        if not symbol.isalnum() or len(symbol) > 10:
            await ctx.send("`Invalid cryptocurrency symbol. Please enter a valid symbol (alphanumeric and <= 10 characters).`")
            return

        api_url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={symbol}&convert=USD"
        headers = {'X-CMC_PRO_API_KEY': api_key}
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if symbol.upper() not in data['data']:
                await ctx.send(f"`Sorry, could not find price information for {symbol.upper()}.`")
                return
            quote = data['data'][symbol.upper()]['quote']['USD']
            price = quote['price']
            percent_change_1h = quote['percent_change_1h']
            percent_change_24h = quote['percent_change_24h']
            percent_change_7d = quote['percent_change_7d']
            change_1h = round(price * percent_change_1h / 100, 2)
            change_24h = round(price * percent_change_24h / 100, 2)
            change_7d = round(price * percent_change_7d / 100, 2)
            embed = discord.Embed(title=f"```{symbol.upper()}```", description=f"**Current Price:** ```${price:.2f}```\n**1 Hour:** ```${change_1h:.2f} ({percent_change_1h:.2f}%)```\n**24 Hours:** ```${change_24h:.2f} ({percent_change_24h:.2f}%)```\n**7 Days:** ```${change_7d:.2f} ({percent_change_7d:.2f}%)```\nPlease note that prices may have changed since this information was last updated.", color=0x2a2d31)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
            await ctx.send(embed=embed)
        elif response.status_code == 400:
            await ctx.send("`Invalid cryptocurrency symbol. Please enter a valid symbol (alphanumeric and <= 10 characters).`")
        else:
            await ctx.send("Sorry, there was an error retrieving the price information.")

async def setup(bot):
    await bot.add_cog(cprice(bot))

