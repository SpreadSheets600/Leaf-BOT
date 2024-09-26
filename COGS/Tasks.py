import json
import asyncio
import discord
import sqlite3
from discord import SlashCommandGroup
from discord.ext import commands, tasks
from datetime import datetime, timedelta

conn = sqlite3.connect("DATA\Tasks.db")
c = conn.cursor()

c.execute(
    """CREATE TABLE IF NOT EXISTS Tasks (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          task TEXT NOT NULL,
          assigned_to INTEGER,
          remind_time INTEGER,
          message_id INTEGER DEFAULT 0
          )"""
)

conn.commit()


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.start()

    def cog_unload(self):
        self.check_reminders.cancel()

    def forum_channel(self, user_id):
        with open("DATA/Forums.json", "r") as f:
            forum_channel = json.load(f)

        return forum_channel[user_id]

    task = SlashCommandGroup(
        name="task",
        description="Task Related Commands",
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install,
        },
    )

    @task.command(
        name="add",
        description="Add A Task",
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install,
        },
    )
    async def add(
        self,
        ctx,
        task: str,
        assigned_to: discord.Member = None,
        remind_time: str = None,
    ):
        if assigned_to is None:
            assigned_to = ctx.author

        discord_timestamp = None
        if remind_time is not None:
            try:
                # Extract Time And Unit
                time_value = int(remind_time[:-1])
                unit = remind_time[-1].lower()
            except Exception as e:
                await ctx.respond(
                    "Invalid time format. Use a valid format like '10m', '2h', etc.",
                    ephemeral=True,
                )
                return

            # Determine The Timedelta Based On The Unit
            if unit == "s":
                delta = timedelta(seconds=time_value)
            elif unit == "m":
                delta = timedelta(minutes=time_value)
            elif unit == "h":
                delta = timedelta(hours=time_value)
            elif unit == "d":
                delta = timedelta(days=time_value)
            else:
                await ctx.respond(
                    "Invalid time unit. Use s, m, h, or d.", ephemeral=True
                )
                return

            # Calculate The Reminder Time And Discord Timestamp
            remind_time_obj = datetime.now() + delta
            remind_time = remind_time_obj.timestamp()
            discord_timestamp = f"<t:{int(remind_time)}:R>"

        forum_id = self.forum_channel(str(assigned_to.id))
        if not forum_id:
            await ctx.respond(
                "Forum Channel For The User Not Found ... Beep Boop \nDid You Even Register ?!",
                ephemeral=True,
            )
            return

        # Insert Task Into The Database
        c.execute(
            "INSERT INTO Tasks (task, assigned_to, remind_time) VALUES (?, ?, ?)",
            (task, assigned_to.id, remind_time),
        )
        conn.commit()

        task_number = c.lastrowid
        date = datetime.now().strftime("%d-%m-%Y")

        # Create An Embed For The Task
        embed = discord.Embed(
            title="Task Added To List",
            description=f"**DATE**: {date}\n**Task No**: {task_number}\n### {task}",
            color=discord.Color.green(),
        )

        if discord_timestamp:
            embed.add_field(name="Remind Time", value=discord_timestamp, inline=False)

        # Send The Message To The Forum Channel
        channel = self.bot.get_channel(forum_id)
        msg = await channel.send(embed=embed)

        # Update The Message ID In The Database
        c.execute("UPDATE Tasks SET message_id = ? WHERE id = ?", (msg.id, task_number))
        conn.commit()

        await ctx.respond("Task Added", ephemeral=True)
        print(f"Task Added: {task} - {assigned_to.id} - {remind_time} - {msg.id}")

    @task.command(
        name="complete",
        description="Complete A Task",
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install,
        },
    )
    async def complete(self, ctx, task_number: int):
        try:
            # Get The Task From The Database
            c.execute("SELECT * FROM Tasks WHERE id = ?", (task_number,))
            task = c.fetchone()

        except sqlite3.Error as e:
            # Handle Database Error
            await ctx.respond(
                "Database Error Occurred. Please Try Again Later.", ephemeral=True
            )
            print(f"Database error: {e}")
            return

        # If Task Not Found, Return
        if not task:
            await ctx.respond("Task Not Found ... Beep Booop", ephemeral=True)
            return

        # Get The Message ID And Assigned Member ID
        message_id = task[4]
        assigned_to = task[2]

        # Constant Mapping For Forum Channel
        forum_id = self.forum_channel(str(assigned_to))

        if not forum_id:
            await ctx.respond(
                "Forum Channel For The User Not Found .... Beep Boop\nDid You Even Register ?!",
                ephemeral=True,
            )
            return

        # Get The Forum Channel
        channel = self.bot.get_channel(forum_id)

        if not channel:
            await ctx.respond("Forum Channel Not Accessible", ephemeral=True)
            return

        try:
            # Get The Message
            message = await channel.fetch_message(message_id)
        except discord.NotFound:
            await ctx.respond(
                "An Error Occured While Performing The Task", ephemeral=True
            )
            return
        except discord.Forbidden:
            await ctx.respond(
                "An Error Occured While Performing The Task", ephemeral=True
            )
            return
        except discord.HTTPException as e:
            await ctx.respond(
                "An Error Occured While Performing The Task", ephemeral=True
            )
            print(f"HTTP Exception: {e}")
            return

        # Add A Reaction To The Message
        try:
            await message.add_reaction("✅")
        except discord.Forbidden:
            await ctx.respond(
                "I Don't Have Permission To Access The Message", ephemeral=True
            )
            return

        # Delete Task From The Database
        try:
            c.execute("DELETE FROM Tasks WHERE id = ?", (task_number,))
            conn.commit()
        except sqlite3.Error as e:
            await ctx.respond("Failed To Delete Filed From Database", ephemeral=True)
            print(f"Database Error On Deletion: {e}")
            return

        await ctx.respond(f"Task {task_number} Marked As Completed!", ephemeral=True)
        print(f"Task Completed: {task_number}")

    @task.command(
        name="list",
        description="List All Tasks",
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install,
        },
    )
    async def list(self, ctx):

        # Get All The Tasks From The Database
        c.execute("SELECT * FROM Tasks")
        tasks = c.fetchall()

        # Create An Embed
        embed = discord.Embed(title="Tasks", color=discord.Color.green())

        # Add The Tasks To The Embed ( Only 5 Tasks In One Embed )
        for task in tasks[:5]:
            task_number = task[0]
            task_text = task[1]
            assigned_to = task[2]
            remind_time = task[3]

            if remind_time:
                # Convert The Timestamp To Discord Timestamp
                remind_time = f"<t:{int(remind_time)}:R>"
            else:
                remind_time = "Not Set"

            embed.add_field(
                name=f"Task No : {task_number}",
                value=f"**Task** : {task_text}\n**Assigned To** : <@{assigned_to}>\n**Remind Time** : {remind_time}",
                inline=False,
            )

        # Send The Embed
        await ctx.respond(embed=embed, ephemeral=True)

    @task.command(
        name="remind",
        description="Remind A Task",
        integration_types={
            discord.IntegrationType.guild_install,
            discord.IntegrationType.user_install,
        },
    )
    async def remind(self, ctx, task_number: int, remind_time: str):

        forum_id = self.forum_channel(str(ctx.author.id))

        if not forum_id:
            await ctx.respond(
                "Forum Channel For The User Not Found ... Beep Boop \nDid You Even Register ?!",
                ephemeral=True,
            )
            return

        # Get The Task From The Database
        c.execute("SELECT * FROM Tasks WHERE id = ?", (task_number,))
        task = c.fetchone()

        # If Task Not Found, Return
        if not task:
            await ctx.respond("Task Not Found ... Beep Booop", ephemeral=True)
            return

        # Parse The Time And Unit
        try:
            time_value = int(remind_time[:-1])
            unit = remind_time[-1].lower()
        except Exception:
            await ctx.respond("Invalid Time Format", ephemeral=True)
            return

        # Calculate The Timedelta Based On The Unit
        if unit == "s":
            delta = timedelta(seconds=time_value)
        elif unit == "m":
            delta = timedelta(minutes=time_value)
        elif unit == "h":
            delta = timedelta(hours=time_value)
        elif unit == "d":
            delta = timedelta(days=time_value)
        else:
            await ctx.respond("Invalid time unit. Use s, m, h, or d.", ephemeral=True)
            return

        # Calculate The Reminder Time And Discord Timestamp
        remind_time_obj = datetime.now() + delta
        remind_time = remind_time_obj.timestamp()
        discord_timestamp = f"<t:{int(remind_time)}:R>"

        # Update The Reminder Time In The Database
        c.execute(
            "UPDATE Tasks SET remind_time = ? WHERE id = ?", (remind_time, task_number)
        )
        conn.commit()

        # Get The Assigned Member ID
        assigned_to = task[2]

        # Get The Forum Channel
        channel = self.bot.get_channel(forum_id)

        # Get The Message ID
        message_id = task[4]

        # Try Fetching The Message, If Not Found, Return
        try:
            message = await channel.fetch_message(message_id)
        except discord.NotFound:
            await ctx.respond("Message not found", ephemeral=True)
            return
        except discord.Forbidden:
            await ctx.respond("Missing permissions to fetch message", ephemeral=True)
            return

        # Create An Embed For The Task With Reminder Time
        embed = discord.Embed(
            title="Task Reminder Set",
            description=f"**Task No**: {task_number}\n### {task[1]}",
            color=discord.Color.green(),
        )
        embed.add_field(name="Remind Time", value=discord_timestamp, inline=False)

        # Edit The Message With The New Embed
        await message.edit(embed=embed)

        await ctx.respond("Reminder Set", ephemeral=True)
        print(f"Reminder Set: Task {task_number}")

    @tasks.loop(seconds=60)
    async def check_reminders(self):
        # Get All The Tasks With Reminder Time Set
        current_time = datetime.now().timestamp()
        c.execute(
            "SELECT * FROM Tasks WHERE remind_time IS NOT NULL AND remind_time <= ?",
            (current_time,),
        )
        tasks_due = c.fetchall()

        for task in tasks_due:
            task_id = task[0]
            task_description = task[1]

            assigned_to = task[2]
            forum_message_id = task[4]

            # Get The Forum Channel ID For That Memeber
            forum_id = self.forum_channel(str(assigned_to))

            if not forum_id:
                continue

            # Get The Channel And Message
            channel = self.bot.get_channel(forum_id)
            try:
                message = await channel.fetch_message(forum_message_id)
            except discord.NotFound:
                print(f"Message Not Found For {task_id}")
                continue
            except discord.Forbidden:
                print(f"Missing Permission For Accesing {task_id}")
                continue

            # Create An Embed For The Task Reminder
            embed = discord.Embed(
                title="Task Reminder",
                description=f"**Task No**: {task_id}\n### {task_description}",
                color=discord.Color.red(),
            )
            user = self.bot.get_user(assigned_to)
            await user.send(embed=embed)

            # Remove The Reminder Time From The Database
            c.execute("UPDATE Tasks SET remind_time = NULL WHERE id = ?", (task_id,))
            conn.commit()


class ReminderUsage(discord.ui.View):

    def __init__(self):
        super().__init__()

    @discord.ui.button(
        label="Check Usage", style=discord.ButtonStyle.secondary, emoji="❗"
    )
    async def check_usage(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        embed = discord.Embed(
            title="Error", description="Wrong Time Unit", color=0x2F3136
        )

        embed.add_field(
            name="Example : Adding Reminder", value="`/task remind 1 10s", inline=False
        )

        embed.add_field(
            name="Unit Format",
            value="`s` - Seconds \n`m` - Minutes\n`h` - Hours\n`d` - Days",
            inline=False,
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Tasks(bot))
