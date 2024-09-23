import asyncio
import discord
import sqlite3
from discord.ext import commands, tasks
from datetime import datetime, timedelta

conn = sqlite3.connect("DATA\Tasks.db")
c = conn.cursor()

c.execute(
    """
          CREATE TABLE IF NOT EXISTS Tasks (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          description TEXT NOT NULL,
          assigned_tO INTEGER,
          reminder_time INTEGER,
          completed BOOLEAN NOT NULL CHECK(completed IN (0, 1))
          )
          """
)

conn.commit()


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.start()

    def cog_unload(self):
        self.check_reminders.cancel()

    @commands.slash_command(name="add_task", description="Add A Task To Do")
    async def create_task(self, ctx, member: discord.Member, *, description: str):

        c.execute(
            "INSERT INTO tasks (description, assigned_to, completed) VALUES (?, ?, ?)",
            (description, member.id, False),
        )
        conn.commit()

        task_id = c.lastrowid

        embed = discord.Embed(
            title="Task Created",
            description=f"Task ID: {task_id}\nDescription: {description}\nAssigned To: {member.mention}",
            color=discord.Color.green(),
        )

        await ctx.respond(embed=embed)

    @commands.slash_command(name="remind_task", description="Set A Reminder For A Task")
    async def set_reminder(self, ctx, task_id: int, reminder_time: str):

        c.execute(
            "UPDATE tasks SET reminder_time = ? WHERE id = ?", (reminder_time, task_id)
        )
        conn.commit()

        embed = discord.Embed(
            title="Reminder Set",
            description=f"Reminder Set For Task ID: {task_id} At {reminder_time}",
            color=discord.Color.green(),
        )

        await ctx.respond(embed=embed)

    @commands.slash_command(name="list_tasks", description="List All Tasks")
    async def list_tasks(self, ctx):

        c.execute("SELECT * FROM tasks")
        tasks = c.fetchall()

        embed = discord.Embed(title="Tasks", color=discord.Color.green())

        for task in tasks:
            task_id, description, assigned_to, reminder_time, completed = task
            member = ctx.guild.get_member(assigned_to)

            embed.add_field(
                name=f"Task ID: {task_id}",
                value=f"Description: {description}\nAssigned To: {member.mention}\nRemind Time: {reminder_time}",
                inline=False,
            )

        await ctx.respond(embed=embed)

    @commands.slash_command(name="complete_task", description="Complete A Task")
    async def complete_task(self, ctx, task_id: int):

        c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()

        embed = discord.Embed(
            title="Task Completed",
            description=f"Task ID: {task_id}",
            color=discord.Color.green(),
        )

        await ctx.respond(embed=embed)

    @tasks.loop(minutes=1)
    async def check_reminders(self):

        now = datetime.now()

        c.execute(
            "SELECT id, description, assigned_to, reminder_time FROM tasks WHERE reminder_time <= ? AND completed = 0",
            (now,),
        )
        tasks_due = c.fetchall()
        for task in tasks_due:
            task_id, description, assigned_to, reminder_time = task
            user = self.bot.get_user(assigned_to)
            if user:
                try:
                    embed = discord.Embed(
                        title="Task Reminder",
                        description=f"Task ID: {task_id}\nDescription: {description}",
                        color=discord.Color.green(),
                    )

                    await user.send(embed=embed)

                except discord.Forbidden:
                    pass

        c.execute(
            "UPDATE tasks SET reminder_time = NULL WHERE reminder_time <= ?", (now,)
        )
        conn.commit()

    @check_reminders.before_loop
    async def before_check_reminders(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Tasks(bot))
