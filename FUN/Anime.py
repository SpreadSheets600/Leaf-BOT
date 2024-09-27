import os
import asyncio
import discord
import aiohttp
import traceback
import crunpyroll
from discord.ext import pages
from dotenv import load_dotenv
from discord.ext.pages import *
from discord.ext import commands
from AnilistPython import Anilist
from AnilistPython import Anilist
from discord.ui import Button, View
from discord import SlashCommandGroup


load_dotenv()


class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.anilist = Anilist()

    anime = SlashCommandGroup(name="anime", description="Anime Commands")

    @anime.command(name="search", description="Get Information About An Anime")
    async def search(self, ctx, *, anime_name: str):

        await ctx.defer()

        try:
            anime_dict = self.anilist.get_anime(anime_name=anime_name, deepsearch=True)
            anime_id = self.anilist.get_anime_id(anime_name)

            if not anime_dict or not anime_id:
                await ctx.respond("Sorry, Anime Not Found")
                return

            anime_name = anime_dict["name_english"]
            anime_desc = anime_dict.get("desc", None)
            starting_time = anime_dict.get("starting_time", None)
            next_airing_ep = anime_dict.get("next_airing_ep", None)
            season = anime_dict.get("season", None)
            genres = ", ".join(anime_dict.get("genres", []))
            anime_url = f"https://anilist.co/anime/{anime_id}/"
            anime_score = anime_dict.get("average_score", None)
            current_ep = None

            if next_airing_ep:
                current_ep = next_airing_ep["episode"] - 1

            if anime_desc:
                anime_desc = anime_desc.split("<br>")

            anime_embed = discord.Embed(title=anime_name, color=0xA0DB8E)
            anime_embed.set_image(url=anime_dict.get("banner_image", None))
            if anime_desc:
                anime_embed.add_field(
                    name="Synopsis", value=anime_desc[0], inline=False
                )
            if anime_id:
                anime_embed.add_field(name="Anime ID", value=anime_id, inline=True)
            if starting_time:
                anime_embed.add_field(
                    name="Start Date", value=starting_time, inline=True
                )
            if season:
                anime_embed.add_field(name="Season", value=season, inline=True)
            if genres:
                anime_embed.add_field(name="Genres", value=genres, inline=False)
            if anime_url:
                anime_embed.add_field(
                    name="More Info", value=f"[AniList Page]({anime_url})", inline=False
                )

            if next_airing_ep:
                anime_embed.set_footer(
                    text=f"Next Episode: {next_airing_ep['episode']} | Current Episode: {current_ep}"
                )
            else:
                anime_embed.set_footer(text="Anime Has Finished Airing")

            await ctx.respond(embed=anime_embed)

        except Exception as e:
            await ctx.respond("Anime Not Found")
            print(f"Error : {e}")


def setup(bot):
    bot.add_cog(Anime(bot))
