import os
import discord
import traceback
from discord.ext import commands
from datetime import datetime, timedelta

from UTILS.KeepAlive import keep_alive

from dotenv import *

load_dotenv()

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)


@bot.event
async def on_ready():

    start_time = str(datetime.now().strftime("%H:%M:%S"))
    up_time = datetime.now()
    bot.start_time = start_time
    bot.up_time = up_time

    print()
    print("========== LEAF KA BOT ==========")
    print("Bot Name : ", bot.user.name)
    print("Bot ID : ", bot.user.id)
    print("=================================\n")

    commands = 0

    for command in bot.walk_application_commands():

        commands += 1
        print(f"[ + ] Loaded : {command.name}")

    print(f"\n[ + ] Loaded : {commands} Commands\n")

    await bot.change_presence(activity=discord.Game(name="With Leaf"))


@bot.event
async def on_slash_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.respond(
            f"This Command Is On Cooldown. Try Again In {error.retry_after:.2f} Seconds"
        )
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.respond("You Are Missing Required Arguments")
    elif isinstance(error, commands.errors.BadArgument):
        await ctx.respond("Bad Argument Provided")
    elif isinstance(error, commands.errors.CommandInvokeError):
        await ctx.respond("An Error Occurred While Executing The Command")
    elif isinstance(error, commands.errors.CommandNotFound):
        await ctx.respond("Command Not Found")
    elif isinstance(error, commands.errors.CheckFailure):
        await ctx.respond("You Do Not Have Permission To Use This Command")
    else:
        await ctx.respond("An Error Occurred")


@bot.slash_command(name="ping", description="Check The BOT's Response Time")
async def ping(ctx: discord.ApplicationContext):
    latency = bot.latency * 1000
    uptime = datetime.now() - bot.up_time

    uptime_seconds = uptime.total_seconds()
    uptime_str = str(timedelta(seconds=uptime_seconds)).split(".")[0]

    embed = discord.Embed(
        title=":ping_pong: _*Pong !*_",
        description=f"Uptime : {uptime_str}\nLatency : {latency:.2f} ms",
        color=0xFBF2EB,
    )

    await ctx.respond(embed=embed)


@bot.slash_command(
    name="info",
    description="Get Bot Information",
)
async def info(ctx: discord.ApplicationContext):
    embed = discord.Embed(
        title=":information_source: Application Info",
        description="Leaf Ka Bot\nMainly For Chamcha Giri",
        color=0xFBF2EB,
    )

    embed.add_field(
        name="Links",
        value=":link: [ Terms ](https://spreadsheets600.me)\n:link: [ GitHub ](https://spreadsheets600.me)",
        inline=True,
    )

    embed.add_field(
        name="Developer",
        value=":gear: `SpreeadSheets600`",
        inline=False,
    )

    embed.add_field(
        name="Created At",
        value=f":calendar: `{bot.user.created_at.strftime('%Y-%m-%d %H:%M:%S')}`",
        inline=True,
    )

    embed.set_thumbnail(url=bot.user.avatar.url)
    await ctx.respond(embed=embed)


try:
    bot.load_extension("COGS.CommandLogger")
    print("[ + ] Command Logger Loaded")
    bot.load_extension("ECONOMY.CryptoInfo")
    print("[ + ] Stock Market Loaded")
    bot.load_extension("COGS.Users")
    print("[ + ] Users Loaded")
    bot.load_extension("ECONOMY.Transactions")
    print("[ + ] CryptoBuy Loaded")
    bot.load_extension("COGS.Tasks")
    print("[ + ] Tasks Loaded")
    bot.load_extension("FUN.Anime")
    print("[ + ] Anime Loaded\n")
except Exception as e:
    print(f"[ - ] COG Not Loadded : {e}\n")
    traceback.print_exc()

keep_alive()
bot.run(os.getenv("TOKEN"))
