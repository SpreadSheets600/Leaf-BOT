import os
import asyncio
import discord
import crunpyroll
from discord.ext import pages
from dotenv import load_dotenv
from discord.ext import commands
from discord import SlashCommandGroup
from discord.ext.pages import Paginator, PaginatorButton

load_dotenv()



class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    anime = SlashCommandGroup(name="anime", description="Anime Commands")

    @anime.command(name="search", description="Search For An Anime")
    async def search(self, ctx: discord.ApplicationContext, name: str = None):
        await ctx.defer()

        try:

            
            email = os.getenv("CHRUNCHY_EMAIL")
            password = os.getenv("CHRUNCHY_PASSWORD")

            anime_client = crunpyroll.Client(email=email, password=password)

            anime_list = await anime_client.search(name)

            if not anime_list:
                return await ctx.send("No Anime Found")

            embeds = []

            for anime in anime_list:
                embed = discord.Embed(
                    title=anime.title,
                    description=anime.synopsis,
                    color=discord.Color.random(),
                )
                embed.add_field(name="ID", value=anime.id)
                embed.set_image(url=anime.poster)
                embed.add_field(name="Episodes", value=anime.episodes)
                embed.add_field(name="Rating", value=anime.rating)

                embeds.append(embed)

            paginator = Paginator(
                pages=embeds,
                show_indicator=True,
                custom_buttons=[
                    PaginatorButton(
                        "first", label="<<", style=discord.ButtonStyle.green, row=1
                    ),
                    PaginatorButton("prev", label="<", style=discord.ButtonStyle.green),
                    PaginatorButton(
                        "page_indicator",
                        style=discord.ButtonStyle.gray,
                        disabled=True,
                        row=0,
                    ),
                    PaginatorButton("next", label=">", style=discord.ButtonStyle.green),
                    PaginatorButton(
                        "last", label=">>", style=discord.ButtonStyle.green, row=1
                    ),
                ],
            )

            await paginator.respond(ctx.interaction)

        except crunpyroll.errors.ClientNotAuthorized as e:
            await ctx.send(
                "Error: Client not authorized. Please check your credentials."
            )
        except Exception as e:
            print(f"Error: {e}")
            await ctx.send(f"An error occurred: {e}")


def setup(bot):
    bot.add_cog(Anime(bot))
