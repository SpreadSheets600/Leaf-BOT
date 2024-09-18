import os
import time
import json
import discord
import datetime
from discord.ext import commands

DIRECTORY = "Users"
LOG_CHANNEL_ID = 1284534867371233383
ADMINS = [727012870683885578, 437622938242514945, 509648898655256576]


class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_user(self, user_id):
        data = {}

        data["user_id"] = user_id
        data["balance"] = 1000000

        data["crypto"] = {}
        data["transactions"] = []

        with open(f"Users/{user_id}.json", "w") as f:
            json.dump(data, f)

    def get_user(self, user_id):
        with open(f"Users/{user_id}.json", "r") as f:
            data = json.load(f)

        return data

    def update_user(self, user_id, data):

        with open(f"Users/{user_id}.json", "w") as f:
            json.dump(data, f)

    @commands.slash_command(
        nmae="register", description="Register Yourself To Use The Bot"
    )
    async def register(self, ctx):
        user_id = ctx.author.id
        if not f"{user_id}.json" in os.listdir():
            self.create_user(user_id)

            embed = discord.Embed(
                title="User Registered",
                description=f"You Have Been Registered Successfully",
                color=discord.Color.green(),
            )

            await ctx.respond(embed=embed)

        else:
            embed = discord.Embed(
                title="User Already Registered",
                description=f"You Are Already Registered",
                color=discord.Color.red(),
            )

            await ctx.respond(embed=embed)

    @commands.slash_command(name="balance", description="Check Your Balance")
    async def balance(self, ctx):
        user_id = ctx.author.id
        if not f"{user_id}.json" in os.listdir(DIRECTORY):
            embed = discord.Embed(
                title="User Not Registered",
                description=f"You Are Not Registered",
                color=discord.Color.red(),
            )

            await ctx.respond(embed=embed)

        else:
            data = self.get_user(user_id)

            embed = discord.Embed(
                title="Balance",
                description=f"Your Balance Is {data['balance']}",
                color=discord.Color.green(),
            )

            await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Database(bot))
