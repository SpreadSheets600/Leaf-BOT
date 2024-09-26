import io
import json
import discord
import requests
import traceback
import pandas as pd
import mplfinance as mpf
from discord.ext.pages import *
from discord.ext import commands
from coinpaprika.client import Client
from datetime import datetime, timedelta
from discord.ext.pages import Paginator, Page
from discord import SlashCommandGroup, options
from discord.ext import commands, bridge, pages


class Transactions(commands.Cog):
    def __init__(self) -> None:
        super().__init__()

    def get_user(self, user_id):
        with open(f"Users/{user_id}.json", "r") as f:
            data = json.load(f)

        return data

    def update_user(self, user_id, data):

        with open(f"Users/{user_id}.json", "w") as f:
            json.dump(data, f)

    def get_id(self, symbol):

        symbol = symbol.upper()

        with open("Currency.json", "r") as f:
            coins = json.load(f)

        return coins.get(symbol, {}).get("id", None)

    crypto = SlashCommandGroup(name="crypto", description="Crypto Commands")

    @crypto.command(name="quote", description="Get Crypto Quote")
    async def quote(
        self,
        ctx: discord.ApplicationContext,
        symbol: str = None,
    ):

        if symbol is None:
            embed = discord.Embed(
                title="Error",
                description="Please Enter A Symbol",
                color=discord.Color.red(),
            )
            embed.add_field(name="Format", value="**{ <symbol> }**", inline=False)
            embed.add_field(name="Example", value="**btc**", inline=False)

            return await ctx.respond(embed=embed, ephemeral=True)

        await ctx.defer()

        if symbol:
            try:
                coinpaprika = Client()
                symbol_main = self.get_id(symbol)

                data = coinpaprika.ticker(symbol_main)
                coin = coinpaprika.coin(symbol_main)

            except Exception as e:
                print(f"Stock Market Error : {e}")

                embed = discord.Embed(
                    title="Error Wrong Symbol",
                    description="Invalid Symbol",
                    color=discord.Color.red(),
                )

                embed.add_field(name="Format", value="**{ <symbol> }**", inline=False)
                embed.add_field(name="Example", value="**btc**", inline=False)

                return await ctx.respond(embed=embed)

        try:
            if data:
                embed = discord.Embed(
                    title=f"{data['name']} Quote",
                    description=f"**Symbol :** {data['symbol']}\n\n"
                    f"**Rank :** {data['rank']}\n"
                    f"**Type :** {coin['type'].upper()}\n"
                    f"### **Price :** $ {round(data['quotes']['USD']['price'],2):,}\n\n"
                    f"**Max Supply :** {round(data['max_supply']):,}\n"
                    f"**Total Supply :** {round(data['total_supply']):,}\n\n"
                    f"**Volume :** {round(data['quotes']['USD']['volume_24h']):,}\n"
                    f"**Market Cap :** {round(data['quotes']['USD']['market_cap']):,}\n\n",
                    color=discord.Color.green(),
                )

                url = coin["logo"]

                if url:
                    embed.set_thumbnail(url=url)

                symbol = symbol.upper() + "USDT"
                print(symbol)
                await ctx.respond(embed=embed, view=ViewChart(symbol))

            else:
                embed = discord.Embed(
                    title="Error",
                    description="No Results Found",
                    color=discord.Color.red(),
                )

                await ctx.respond(embed=embed)

        except Exception as e:
            print(f"Stock Market Error : {e}")

    @crypto.command(name="buy", description="Buy Crypto")
    async def buy(self, ctx, crypto: str = None, amount: float = None):

        try:
            if not crypto:
                embed = discord.Embed(
                    title="Error",
                    description="Please Enter A Symbol",
                    color=discord.Color.red(),
                )
                embed.add_field(name="Format", value="**{ <symbol> }**", inline=False)
                embed.add_field(name="Example", value="**btcn**", inline=False)

                return await ctx.respond(embed=embed, ephemeral=True)

            if not amount:
                embed = discord.Embed(
                    title="Error",
                    description="Please Enter An Amount",
                    color=discord.Color.red(),
                )
                embed.add_field(name="Format", value="**{ <amount> }**", inline=False)
                embed.add_field(name="Example", value="**100**", inline=False)

                return await ctx.respond(embed=embed, ephemeral=True)

            user_id = ctx.author.id
            user = self.get_user(user_id)

            coinpaprika = Client()
            coin = self.get_id(crypto)

            data = coinpaprika.ticker(coin)
            price = round(data["quotes"]["USD"]["price"])

            if user["balance"] < price * amount:
                embed = discord.Embed(
                    title="Error",
                    description="Insufficient Balance",
                    color=discord.Color.red(),
                )

                return await ctx.respond(embed=embed)

            user["balance"] -= price * amount
            user["crypto"] = user.get("crypto", {})

            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if coin in user["crypto"]:
                user["crypto"][coin]["amt"] += amount
                user["crypto"][coin]["buy_price"] = price

                transactions = user["transactions"]
                transactions.append(
                    f"{time} Bought {amount} {coin} For ${price * amount}"
                )

            else:
                user["crypto"][coin] = {
                    "amt": amount,
                    "buy_price": price,
                }

                # Discord Timestamp String
                discord_timestamp = f"<t:{int(datetime.now().timestamp())}:R>"

                user["transactions"].append(
                    f"{discord_timestamp} - Bought {amount} {coin} For ${price * amount}"
                )

            with open(f"Users/{user_id}.json", "w") as f:
                json.dump(user, f)

            coin = data["symbol"]

            embed = discord.Embed(
                title="Crypto Bought",
                description=f"You Have Bought {amount} {coin} For ${price * amount}",
                color=discord.Color.green(),
            )

            embed.add_field(name="Balance", value=f"${user['balance']}", inline=False)

            await ctx.respond(embed=embed)

        except Exception as e:
            print(f"Stock Market Error : {e}")

            embed = discord.Embed(
                title="Error",
                description="Please Enter A Symbol",
                color=discord.Color.red(),
            )
            embed.add_field(name="Format", value="**{ <symbol> }**", inline=False)
            embed.add_field(name="Example", value="**btc**", inline=False)

            await ctx.respond(embed=embed, ephemeral=True)

    @crypto.command(name="sell", description="Sell Crypto")
    async def sell(self, ctx, crypto: str = None, amount: float = None):

        try:

            if not crypto:
                embed = discord.Embed(
                    title="Error",
                    description="Please Enter A Symbol",
                    color=discord.Color.red(),
                )
                embed.add_field(name="Format", value="**{ <symbol> }**", inline=False)
                embed.add_field(name="Example", value="**btc**", inline=False)

                return await ctx.respond(embed=embed, ephemeral=True)

            if not amount:
                embed = discord.Embed(
                    title="Error",
                    description="Please Enter An Amount",
                    color=discord.Color.red(),
                )
                embed.add_field(name="Format", value="**{ <amount> }**", inline=False)
                embed.add_field(name="Example", value="**100**", inline=False)

                return await ctx.respond(embed=embed, ephemeral=True)

            user_id = ctx.author.id
            user = self.get_user(user_id)

            coinpaprika = Client()
            coin = self.get_id(crypto)

            data = coinpaprika.ticker(coin)
            price = round(data["quotes"]["USD"]["price"])

            if coin not in user["crypto"]:
                embed = discord.Embed(
                    title="Error",
                    description="You Do Not Own This Crypto",
                    color=discord.Color.red(),
                )

                return await ctx.respond(embed=embed)

            if user["crypto"][coin]["amt"] < amount:
                embed = discord.Embed(
                    title="Error",
                    description="You Do Not Have Enough Crypto",
                    color=discord.Color.red(),
                )

                return await ctx.respond(embed=embed)

            user["balance"] += price * amount
            user["crypto"] = user.get("crypto", {})

            time = f"<t:{int(datetime.now().timestamp())}:R>"

            user["crypto"][coin]["amt"] -= amount
            user["crypto"][coin]["sell_price"] = price

            transactions = user["transactions"]
            transactions.append(f"{time} Sold {amount} {coin} For ${price * amount}")

            with open(f"Users/{user_id}.json", "w") as f:
                json.dump(user, f)

            coin = data["symbol"]

            embed = discord.Embed(
                title="Crypto Sold",
                description=f"You Have Sold {amount} {coin} For ${price * amount}",
                color=discord.Color.green(),
            )

            embed.add_field(name="Balance", value=f"${user['balance']}", inline=False)

            await ctx.respond(embed=embed)

        except Exception as e:
            print(f"Stock Market Error : {e}")

            embed = discord.Embed(
                title="Error",
                description="Please Enter A Symbol",
                color=discord.Color.red(),
            )
            embed.add_field(name="Format", value="**{ <symbol> }**", inline=False)
            embed.add_field(name="Example", value="**btc**", inline=False)

            await ctx.respond(embed=embed, ephemeral=True)

    @crypto.command(name="transactions", description="View Crypto Transactions")
    async def transactions(self, ctx):

        user_id = ctx.author.id
        user = self.get_user(user_id)

        transactions = user.get("transactions", [])

        if not transactions:
            embed = discord.Embed(
                title="No Transactions",
                description="You Have No Transactions",
                color=discord.Color.red(),
            )

            return await ctx.respond(embed=embed)

        embed = discord.Embed(
            title="Transactions",
            color=discord.Color.green(),
        )

        for transaction in transactions:
            embed.add_field(name="Transaction", value=transaction, inline=False)

        await ctx.respond(embed=embed)

    @crypto.command(name="portfolio", description="View Crypto Portfolio")
    async def portfolio(self, ctx):
        user_id = ctx.author.id
        user = self.get_user(user_id)

        crypto = user.get("crypto", {})

        if not crypto:
            embed = discord.Embed(
                title="No Portfolio",
                description="You Have No Portfolio",
                color=discord.Color.red(),
            )

            return await ctx.respond(embed=embed)

        embed = discord.Embed(
            title="Portfolio",
            color=discord.Color.green(),
        )

        for coin, data in crypto.items():
            if coin == "transactions":
                continue

            coinpaprika = Client()
            coin_data = coinpaprika.ticker(coin)

            sell_price = coin_data["quotes"]["USD"]["price"]

            PNL = (data["amt"] * data["buy_price"]) - (data["amt"] * sell_price)

            previos_price = data.get("sell_price", 0)

            embed.add_field(
                name=f"{coin.upper()}",
                value=(
                    f"**Amount :** {data['amt']}\n\n"
                    f"**Buy Price :** $ {data['buy_price']}\n\n"
                    f"**Current Price :** $ {sell_price}\n"
                    f"**Profit / Loss :** $ {round(PNL,2)}\n\n"
                    f"**Previous Price :** $ {previos_price}\n"
                ),
                inline=False,
            )

        await ctx.respond(embed=embed)

    @crypto.command(name="send", description="Send Crypto To Another User")
    async def send(
        self, ctx, user: discord.User, crypto: str = None, amount: float = None
    ):
        try:
            if not crypto:
                embed = discord.Embed(
                    title="Error",
                    description="Please Enter A Symbol",
                    color=discord.Color.red(),
                )
                embed.add_field(name="Format", value="**{ <symbol> }**", inline=False)
                embed.add_field(name="Example", value="**btc**", inline=False)

                return await ctx.respond(embed=embed, ephemeral=True)

            if not amount:
                embed = discord.Embed(
                    title="Error",
                    description="Please Enter An Amount",
                    color=discord.Color.red(),
                )
                embed.add_field(name="Format", value="**{ <amount> }**", inline=False)
                embed.add_field(name="Example", value="**100**", inline=False)

                return await ctx.respond(embed=embed, ephemeral=True)

            user_id_1 = ctx.author.id
            user_1 = self.get_user(user_id_1)

            user_id_2 = user.id
            try: 
                user_2 = self.get_user(user_id_2)
            except:
                embed = discord.Embed(
                    title="Error",
                    description="User Not Found",
                    color=discord.Color.red(),
                )

                return await ctx.respond(embed=embed)

            coinpaprika = Client()
            coin = self.get_id(crypto)

            data = coinpaprika.ticker(coin)
            price = round(data["quotes"]["USD"]["price"])

            if coin not in user_1["crypto"]:
                embed = discord.Embed(
                    title="Error",
                    description="You Do Not Own This Crypto",
                    color=discord.Color.red(),
                )

                return await ctx.respond(embed=embed)

            if user_1["crypto"][coin]["amt"] < amount:
                embed = discord.Embed(
                    title="Error",
                    description="You Do Not Have Enough Crypto",
                    color=discord.Color.red(),
                )

                return await ctx.respond(embed=embed)

            user_1["crypto"] = user_1.get("crypto", {})

            time = f"<t:{int(datetime.now().timestamp())}:R>"

            network_charge = (price * amount) * 0.03
            user_1["balance"] -= network_charge  #

            user_1["crypto"][coin]["amt"] -= amount
            user_1["crypto"][coin]["sell_price"] = price

            transactions_1 = user_1["transactions"]
            transactions_1.append(
                f"{time} Deducted ${network_charge} As Network Charge"
            )
            transactions_1.append(
                f"{time} Gave {amount} {coin} For ${price * amount} To <@{user_id_2}>"
            )

            with open(f"Users/{user_id_1}.json", "w") as f:
                json.dump(user_1, f)

            user_2["crypto"] = user_2.get("crypto", {})
            user_2["crypto"][coin] = user_2["crypto"].get(coin, {"amt": 0})
            user_2["crypto"][coin]["amt"] += amount

            transactions_2 = user_2["transactions"]
            transactions_2.append(
                f"{time} Received {amount} {coin} For ${price * amount} From <@{user_id_1}>"
            )

            with open(f"Users/{user_id_2}.json", "w") as f:
                json.dump(user_2, f)

            coin_symbol = data["symbol"]
            balance = user_1["balance"]

            embed = discord.Embed(
                title="Crypto Sent",
                description=(
                    f"You Have Given {amount} {coin_symbol} For ${price * amount} To <@{user_id_2}>\n"
                    f"**Network Charge:** ${network_charge}"
                ),
                color=discord.Color.green(),
            )
            embed.add_field(name="Balance", value=f"${balance}", inline=False)

            await ctx.respond(embed=embed)

        except Exception as e:
            print(f"Crypto Transfer Error: {e}")

            embed = discord.Embed(
                title="Error",
                description="An Error Occurred While Doing The Transaction",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=embed, ephemeral=True)


class ViewChart(discord.ui.View):
    def __init__(self, currency):
        super().__init__()

        self.currency = currency

    @discord.ui.button(label="View Candle Chart", style=discord.ButtonStyle.secondary)
    async def candle_chart(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await interaction.response.send_message("Fetching Chart...", ephemeral=True)

        try:
            if self.currency:
                url = f"https://api.binance.com/api/v3/klines?symbol={self.currency.upper()}&interval=1d&limit=20"
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

                    await interaction.followup.send(embed=embed, ephemeral=True)
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

                embed = discord.Embed(
                    title=f"{self.currency.upper()} Chart",
                    description=f"**Interval :** 1 Day\n**Limit :** 20",
                    color=discord.Color.green(),
                )
                embed.set_image(url="attachment://Chart.png")
                embed.set_footer(
                    text="For Custom Interval And Limit Use `/crypto chart`"
                )

                message_id = interaction.message.id

                button.disabled = True
                await interaction.followup.edit_message(
                    message_id=message_id, view=self
                )

                await interaction.followup.send(file=file, embed=embed, ephemeral=True)

                buf.close()

            else:

                await interaction.followup.send(
                    "Please Provide A Valid Cryptocurrency Symbol", ephemeral=True
                )

        except Exception as e:
            print(f"An Error Occurred : {e}")


def setup(bot):
    bot.add_cog(Transactions())
