import time
import discord
import sqlite3
import datetime
from discord.ext import commands

LOG_CHANNEL_ID = 1284534867371233383

ADMINS = [727012870683885578, 437622938242514945, 509648898655256576]


class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def create_connection(self):
        return sqlite3.connect("User.db")

    def create_table(self):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY,
                user_balance INTEGER NOT NULL
            )
            """
        )

        print("[ + ] Table Created")

        conn.commit()
        conn.close()

    def insert_user(self, user_id: int):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Users (user_id, user_balance) VALUES (?, ?)
            """,
            (user_id, 10000),
        )
        conn.commit()
        conn.close()

    def get_user(self, user_id: int):
        conn = self.create_connection()

        self.create_table()

        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM Users WHERE user_id = ?
            """,
            (user_id,),
        )
        user = cursor.fetchone()
        conn.close()
        return user

    def update_user(self, user_id: int, user_balance: int):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE Users SET user_balance = ? WHERE user_id = ?
            """,
            (user_balance, user_id),
        )
        conn.commit()
        conn.close()

    def delete_user(self, user_id: int):
        conn = self.create_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM Users WHERE user_id = ?
            """,
            (user_id,),
        )
        conn.commit()
        conn.close()

    @commands.slash_command(name="register", description="Register Your Account")
    async def register(self, ctx):
        user = self.get_user(ctx.author.id)

        if user:
            embed = discord.Embed(
                title="Error",
                description="You Are Already Registered",
                color=discord.Color.red(),
            )

        else:
            self.create_table()
            self.insert_user(ctx.author.id)
            embed = discord.Embed(
                title="Success",
                description="You Have Successfully Registered\nYou Have Been Given 10000 $",
                color=discord.Color.green(),
            )

        await ctx.respond(embed=embed)

    @commands.slash_command(name="balance", description="Check Your Balance")
    async def balance(self, ctx):
        user = self.get_user(ctx.author.id)
        if user:

            time_now = datetime.datetime.now()
            time_iso = time_now.isoformat()

            discord_time_stamp = f"<t:{int(time_now.timestamp())}:F>"

            embed = discord.Embed(
                title="Balance",
                description=f"Your Balance : {user[1]}\nLast Updated : {discord_time_stamp}",
                color=discord.Color.blue(),
            )

        else:
            embed = discord.Embed(
                title="Error",
                description="You Are Not Registered",
                color=discord.Color.red(),
            )

        await ctx.respond(embed=embed)

    @commands.slash_command(name="add", description="Add Money To Your Account")
    async def add(self, ctx, amount: int):

        if ctx.author.id not in ADMINS:
            embed = discord.Embed(
                title="Error",
                description="You Do Not Have Permission To Use This Command",
                color=discord.Color.red(),
            )

            await ctx.respond(embed=embed)
            return

        user = self.get_user(ctx.author.id)
        if user:
            new_balance = user[1] + amount
            self.update_user(ctx.author.id, new_balance)

            embed = discord.Embed(
                title="Success",
                description=f"Added {amount} To Your Account",
                color=discord.Color.green(),
            )

        else:
            embed = discord.Embed(
                title="Error",
                description="You Are Not Registered",
                color=discord.Color.red(),
            )

        await ctx.respond(embed=embed)

    @commands.slash_command(name="remove", description="Remove Money From Your Account")
    async def remove(self, ctx, amount: int):

        if ctx.author.id not in ADMINS:
            embed = discord.Embed(
                title="Error",
                description="You Do Not Have Permission To Use This Command",
                color=discord.Color.red(),
            )

            await ctx.respond(embed=embed)
            return

        user = self.get_user(ctx.author.id)
        if user:
            new_balance = user[1] - amount
            self.update_user(ctx.author.id, new_balance)

            embed = discord.Embed(
                title="Success",
                description=f"Removed {amount} From Your Account",
                color=discord.Color.green(),
            )

        else:
            embed = discord.Embed(
                title="Error",
                description="You Are Not Registered",
                color=discord.Color.red(),
            )

        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Database(bot))
