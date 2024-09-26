import os
import time
import json
import discord
import datetime
import traceback
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

    def update_forum_channel(self, user_id, channel_id):
        with open("DATA/Forums.json", "r") as f:
            forum_channel = json.load(f)

        forum_channel[user_id] = channel_id

        with open("DATA/Forums.json", "w") as f:
            json.dump(forum_channel, f)

    def get_forum_channel(self, user_id):
        with open("DATA/Forums.json", "r") as f:
            data = json.load(f)

        return data[str(user_id)]

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

            const_iitm_role_id = 1286695720044200066
            const_iitm_role = ctx.guild.get_role(const_iitm_role_id)

            # Check Weather If The User Has The Role ID Or Not
            if const_iitm_role_id in [role.id for role in ctx.author.roles]:

                # Create A Forum Post In A Channel
                const_forum_channel = self.bot.get_channel(1287769763195519007)

                # Create A Forum Post
                if isinstance(const_forum_channel, discord.ForumChannel):
                    forum_post = await const_forum_channel.create_thread(
                        name=f"Tasks - {ctx.author.display_name}",
                        content="# Task List",
                    )

                    self.update_forum_channel(user_id, forum_post.id)

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

    @commands.slash_command(name="delete", description="Delete Your Account")
    async def delete(self, ctx):
        user_id = ctx.author.id
        if not f"{user_id}.json" in os.listdir(DIRECTORY):
            embed = discord.Embed(
                title="User Not Registered",
                description=f"You Are Not Registered",
                color=discord.Color.red(),
            )

            await ctx.respond(embed=embed)

        else:
            os.remove(f"Users/{user_id}.json")

            embed = discord.Embed(
                title="User Deleted",
                description=f"You Have Been Deleted Successfully",
                color=discord.Color.green(),
            )

            try:

                const_iitm_role_id = 1286695720044200066
                const_iitm_role = ctx.guild.get_role(const_iitm_role_id)

                # Check Weather If The User Has The Role ID Or Not
                if const_iitm_role_id in [role.id for role in ctx.author.roles]:

                    forum_channel = self.get_forum_channel(user_id)
                    forum_post = self.bot.get_channel(forum_channel)

                    if isinstance(forum_post, discord.Thread):
                        await forum_post.delete()
                        await ctx.respond(
                            "Forum Post Deleted Successfully", ephemeral=True
                        )

                    with open("DATA/Forums.json", "r") as f:
                        data = json.load(f)

                    # Remove The User From The Forums.json File
                    data.pop(str(user_id))

                    with open("DATA/Forums.json", "w") as f:
                        json.dump(data, f, indent=4)

            except Exception as e:
                print(f"Error : {e}")
                traceback.print_exc()

            await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Database(bot))
