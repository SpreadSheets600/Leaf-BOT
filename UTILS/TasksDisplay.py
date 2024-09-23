import discord
import sqlite3
from datetime import datetime
from discord.ext import commands, tasks


conn = sqlite3.connect("DATA/Tasks.db")
c = conn.cursor()


class TasksDisplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.display_tasks.start()

    def cog_unload(self):
        self.display_tasks.cancel()

    @tasks.loop(seconds=30)
    async def display_tasks(self):

        leaf_user_id = 437622938242514945
        soham_user_id = 727012870683885578

        leaf_display_channel = self.bot.get_channel(1287805072658661477)
        soham_display_channel = self.bot.get_channel(1287770126376243200)

        c.execute(
            "SELECT id, description, completed FROM Tasks WHERE assigned_to = ?",
            (leaf_user_id,),
        )
        leaf_tasks = c.fetchall()
        c.execute(
            "SELECT id, description, completed FROM Tasks WHERE assigned_to = ?",
            (soham_user_id,),
        )
        soham_tasks = c.fetchall()

        leaf_embed = discord.Embed(title="Leaf's Tasks", color=discord.Color.green())
        for task in leaf_tasks:
            task_id, description, completed = task
            status = "✅ Completed" if completed else "❌ Pending"
            leaf_embed.add_field(
                name=f"Task {task_id}",
                value=f"{description}\nStatus: {status}",
                inline=False,
            )

        soham_embed = discord.Embed(title="Soham's Tasks", color=discord.Color.green())
        for task in soham_tasks:
            task_id, description, completed = task
            status = "✅ Completed" if completed else "❌ Pending"
            soham_embed.add_field(
                name=f"Task {task_id}",
                value=f"{description}\nStatus: {status}",
                inline=False,
            )

        await leaf_display_channel.purge(limit=1)
        await leaf_display_channel.send(embed=leaf_embed)

        await soham_display_channel.purge(limit=1)
        await soham_display_channel.send(embed=soham_embed)

    @display_tasks.before_loop
    async def before_display_tasks(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(TasksDisplay(bot))
