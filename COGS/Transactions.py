import os
import discord
import finnhub
import sqlite3
from discord import option
from discord.ext.pages import *
from discord.ext import commands
from coinpaprika.client import Client
from discord.ext.pages import Paginator, Page
from discord import SlashCommandGroup, options
from discord.ext import commands, bridge, pages

TRANSACTION_LOG = 1284534867371233383

from dotenv import *

load_dotenv()

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")


class Transactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.finnhub = finnhub.Client(api_key=FINNHUB_API_KEY)

    @commands.command(
        name="buy", aliases=["purchase", "b"], description="Buy CyptoCurrency"
    )
    @option(
        "symbol",
        description="The Crypto Symbol",
        choices=[
            "XR - XRP",
            "SOL - Solana",
            "UNI - Uniswap",
            "BTC - Bitcoin",
            "ADA - Cardano",
            "USDT - Tether",
            "TON - Toncoin",
            "DOT - Polkadot",
            "ETH - Ethereum",
            "LTC - Litecoin",
            "DOGE - Dogecoin",
            "USDC - USD Coin",
            "AVAX - Avalanche",
            "LINK - Chainlink",
            "BNB - Binanace Coin",
        ],
    )
    async def buy(self, ctx: discord.ApplicationContext, symbol: str = None):
        await ctx.defer()

        if symbol:
            coinpaprika = Client()
            symbol_main = symbol.replace(" ", "").lower()

            data = coinpaprika.ticker(symbol_main)
            coin = coinpaprika.coin(symbol_main)

            if data:
                embed = discord.Embed(
                    title=f"Buy {data['name']}",
                    description=f"**Symbol :** {data['symbol']}\n**Price :** $ {round(data['quotes']['USD']['price'],2):,}",
                    color=discord.Color.green(),
                )
