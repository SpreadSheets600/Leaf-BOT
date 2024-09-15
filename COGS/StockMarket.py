import os
import discord
import finnhub
from polygon import RESTClient
from discord.ext.pages import *
from discord.ext import commands
from discord import SlashCommandGroup
from discord.ext.pages import Paginator, Page
from discord.ext import commands, bridge, pages

from dotenv import *

load_dotenv()

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")


class MarketInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.polygon = RESTClient(POLYGON_API_KEY)
        self.finnhub = finnhub.Client(api_key=FINNHUB_API_KEY)

    market = SlashCommandGroup(name="market", description="Market Commands")

    @market.command(name="search", description="Search For A Symbol")
    async def search(self, ctx: discord.ApplicationContext, symbol: str):
        data = self.finnhub.symbol_lookup(symbol)

        try:
            if data:
                total_results = data["count"]
                results = data["result"]

                embeds = []

                chunk_size = 4
                for i in range(0, len(results), chunk_size):
                    chunk = results[i : i + chunk_size]

                    description = ""
                    for result in chunk:
                        description += (
                            f"**Symbol :** {result['displaySymbol']}\n"
                            f"**Description :** {result['description']}\n"
                            f"**Type :** {result['type']}\n\n"
                        )

                    embed = discord.Embed(
                        title="Search Results",
                        description=description,
                        color=discord.Color.green(),
                    )

                    embeds.append(embed)

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
                            "⬜",
                            style=discord.ButtonStyle.gray,
                            disabled=True,
                            row=1,
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
                embed = discord.Embed(
                    title="Error",
                    description="No Results Found",
                    color=discord.Color.red(),
                )

                await ctx.respond(embed=embed)

        except Exception as e:
            print(f"Stock Market Error : {e}")


def setup(bot):
    bot.add_cog(MarketInfo(bot))
