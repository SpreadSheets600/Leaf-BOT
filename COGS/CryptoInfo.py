import os
import io
import discord
import finnhub
import requests
import pandas as pd
import mplfinance as mpf
from discord import option
from polygon import RESTClient
import matplotlib.pyplot as plt
from discord.ext.pages import *
from discord.ext import commands
from coinpaprika.client import Client
from discord.ext.pages import Paginator, Page
from discord import SlashCommandGroup, options
from discord.ext import commands, bridge, pages

from dotenv import *

load_dotenv()

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")


class CryptoInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.polygon = RESTClient(POLYGON_API_KEY)
        self.finnhub = finnhub.Client(api_key=FINNHUB_API_KEY)

    market = SlashCommandGroup(name="market", description="Crypto Commands")

    @market.command(name="search", description="Search For A Symbol")
    async def search(
        self, ctx: discord.ApplicationContext, name: str = None, symbol: str = None
    ):
        await ctx.defer()

        coinpaprika = Client()
        coins = coinpaprika.coins()

        embeds = []

        try:
            if name:
                matching_coins = [
                    coin
                    for coin in coins
                    if name.lower() in coin["name"].lower() and name.lower() in "True"
                ]

            elif symbol:
                matching_coins = [
                    coin
                    for coin in coins
                    if symbol.lower() in coin["name"].lower()
                    and symbol.lower() in "True"
                ]

            chunk_size = 9
            for i in range(0, len(matching_coins), chunk_size):
                chunk = matching_coins[i : i + chunk_size]

                embed = discord.Embed(
                    title="Search Results",
                    color=discord.Color.green(),
                )

                for result in chunk:
                    embed.add_field(
                        name=f"{result['name']} ( {result['symbol']} )",
                        value=(
                            f"**Rank :** {result['rank']}\n"
                            f"**Type :** {result['type'].upper()}\n\n"
                            f"**ID :** {result['id']}\n"
                        ),
                        inline=True,
                    )

                embeds.append(embed)

            if embeds:

                paginator = Paginator(
                    pages=embeds,
                    show_indicator=True,
                    use_default_buttons=False,
                    disable_on_timeout=True,
                    custom_buttons=[
                        PaginatorButton(
                            "first", label="<<", style=discord.ButtonStyle.green, row=1
                        ),
                        PaginatorButton(
                            "prev", label="<", style=discord.ButtonStyle.green
                        ),
                        PaginatorButton(
                            "page_indicator",
                            style=discord.ButtonStyle.gray,
                            disabled=True,
                            row=0,
                        ),
                        PaginatorButton(
                            "⬜", style=discord.ButtonStyle.gray, disabled=True, row=1
                        ),
                        PaginatorButton(
                            "next", label=">", style=discord.ButtonStyle.green
                        ),
                        PaginatorButton(
                            "last", label=">>", style=discord.ButtonStyle.green, row=1
                        ),
                    ],
                )

                await paginator.respond(ctx.interaction)
            else:
                await ctx.respond(f"No Coins Found For : {symbol}", ephemeral=True)

        except Exception as e:
            print(f"Stock Market Error : {e}")
            await ctx.respond(f"An Error Occurred : {e}", ephemeral=True)

    @market.command(name="chart", description="Get Chart For A Symbol")
    async def chart(
        self,
        ctx: discord.ApplicationContext,
        symbol: str = None,
        interval: str = "1d",
        limit: int = 20,
    ):
        if symbol is None:
            embed = discord.Embed(
                title="Error",
                description="Please Enter A Symbol",
                color=discord.Color.red(),
            )
            embed.add_field(
                name="Format", value="**{ <symbol>-<name> }**", inline=False
            )
            embed.add_field(name="Example", value="**btc-bitcoin**", inline=False)

            return await ctx.respond(embed=embed, ephemeral=True)

        await ctx.defer()

        crytpo_symbol = symbol.split("-")[0].upper() + "USDT"

        try:

            if crytpo_symbol:
                url = f"https://api.binance.com/api/v3/klines?symbol={crytpo_symbol.upper()}&interval={interval}&limit={limit}"
                response = requests.get(url)

                if response.status_code != 200:
                    raise Exception(
                        f"API Returned A Non - 200 Status : {response.status_code}"
                    )

                data = response.json()

                if len(data) == 0:
                    embed = discord.Embed(
                        title="Error",
                        description="No Results Found\nPlease Check The Symbol",
                        color=discord.Color.red(),
                    )
                    embed.add_field(
                        name="Format", value="**{ <symbol>-<name> }**", inline=False
                    )
                    embed.add_field(
                        name="Example", value="**btc-bitcoin**", inline=False
                    )

                    await ctx.respond(embed=embed)
                    return

                df = pd.DataFrame(
                    data,
                    columns=[
                        "Timestamp",
                        "Open",
                        "High",
                        "Low",
                        "Close",
                        "Volume",
                        "Close_time",
                        "Quote_asset_volume",
                        "Number_of_trades",
                        "Taker_buy_base",
                        "Taker_buy_quote",
                        "Ignore",
                    ],
                )

                df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")
                df["Open"] = df["Open"].astype(float)
                df["High"] = df["High"].astype(float)
                df["Low"] = df["Low"].astype(float)
                df["Close"] = df["Close"].astype(float)
                df["Volume"] = df["Volume"].astype(float)
                df.set_index("Timestamp", inplace=True)

                market_color = mpf.make_marketcolors(
                    up="#49c686cc",
                    down="#c2423fcc",
                    volume="in",
                    edge="inherit",
                    inherit=True,
                )
                style = mpf.make_mpf_style(
                    base_mpf_style="mike", marketcolors=market_color
                )

                buf = io.BytesIO()

                mpf.plot(
                    df,
                    type="candle",
                    style=style,
                    volume=True,
                    ylabel="Price",
                    tight_layout=True,
                    show_nontrading=True,
                    savefig=dict(fname=buf, dpi=500, format="png"),
                )

                buf.seek(0)

                file = discord.File(buf, filename="Chart.png")

                if "d" in interval:
                    interval = interval.replace("d", " Day(s)")

                elif "h" in interval:
                    interval = interval.replace("h", " Hour(s)")

                elif "m" in interval:
                    interval = interval.replace("m", " Months(s)")

                embed = discord.Embed(
                    title=f"{crytpo_symbol.upper()} Chart",
                    description=f"**Interval :** {interval}\n**Limit :** {limit}",
                    color=discord.Color.green(),
                )
                embed.set_image(url="attachment://Chart.png")

                await ctx.respond(file=file, embed=embed)

                buf.close()

            else:

                await ctx.respond(
                    "Please Provide A Valid Cryptocurrency Symbol", ephemeral=True
                )

        except Exception as e:
            print(f"An Error Occurred: {e}")


def setup(bot):
    bot.add_cog(CryptoInfo(bot))
