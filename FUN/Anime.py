import os
import asyncio
import discord
import aiohttp
import traceback
import crunpyroll
from discord import option
from discord.ext import pages
from dotenv import load_dotenv
from discord.ext.pages import *
from discord.ext import commands
from AnilistPython import Anilist
from AnilistPython import Anilist
from discord.ui import Button, View
from discord import SlashCommandGroup


load_dotenv()


async def swaifu(tag: str):
    url = "https://api.waifu.im/search"

    params = {"included_tags": [tag], "is_nsfw": "false"}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if "images" in data and len(data["images"]) > 0:
                    image_url = data["images"][0]["url"]

                    return image_url


async def nwaifu(tag: str):
    url = f"https://api.waifu.pics/nsfw/{tag}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()

                if "url" in data:
                    image_url = data["url"]

                    return image_url

class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.anilist = Anilist()

    anime = SlashCommandGroup(name="anime", description="Anime Commands")

    @anime.command(
        name="waifu",
        description="Get A Random Waifu Image",
    )
    @option(
        "tag",
        description="Choose The Category",
        choices=["maid", "waifu", "oppai", "selfies", "uniform"],
    )
    async def waifu(self, ctx, tag: str):
        await ctx.defer()

        try:
            image_url = await swaifu(tag)

            if image_url:
                embed = discord.Embed(
                    title="OniChan Here I Am <3",
                    color=discord.Color.blurple(),
                )
                embed.set_image(url=image_url)

                await ctx.respond(embed=embed)

            else:
                await ctx.respond("No Waifu Image Found For This Tag")

        except Exception as e:
            await ctx.respond(f"An Error Occurred : {e}")

    @anime.command(
        name="nwaifu", description="Get A Random NSFW Waifu Image", nsfw=True
    )
    @option(
        "tag",
        description="Choose The Category",
        choices=["waifu", "neko", "trap", "blowjob"],
    )
    async def nwaifu(self, ctx, tag: str):
        await ctx.defer()

        try:
            image_url = await nwaifu(tag)

            if image_url:
                embed = discord.Embed(
                    title="OniChan Here I Am <3",
                    color=discord.Color.blurple(),
                )
                embed.set_image(url=image_url)

                await ctx.respond(embed=embed)

            else:
                await ctx.respond("No Waifu Image Found For This Tag")

        except Exception as e:
            await ctx.respond(f"An Error Occurred : {e}")

    @anime.command(name="search", description="Get Information About An Anime")
    async def search(self, ctx, *, name: str):

        await ctx.defer()

        try:
            anime_dict = self.anilist.get_anime(anime_name=name, deepsearch=True)
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

    @anime.command(name="watch", description="Watch Anime")
    async def watch(self, ctx, *, name: str, episode: int = 1):
        await ctx.defer()

        try:
            season = None

            if name.split(" ")[-1] in [
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "0",
            ]:
                if name.split(" ")[-1] == "1":
                    season = "1st"
                elif name.split(" ")[-1] == "2":
                    season = "2nd"
                elif name.split(" ")[-1] == "3":
                    season = "3rd"
                else:
                    season = name.split(" ")[-1] + "th"

            anime_dict = self.anilist.get_anime(anime_name=name[:-1], deepsearch=True)
            anime_name = anime_dict["name_romaji"].replace(" ", "-").lower()
            eng_name = anime_dict["name_english"]

            cover_image = anime_dict["banner_image"]

            try:
                current_ep = anime_dict["next_airing_ep"]["episode"] - 1

                if episode > current_ep:
                    await ctx.respond("Episode Not Yet Aired")
                    return
            except:
                current_ep = None

            name = anime_dict["name_romaji"].replace(" ", "-").lower()

            if season:
                anime_name = f"{name}-{season}-season"

                print(anime_name)

            url = f"https://astrumanimeapi.vercel.app/anime/gogoanime/watch/{anime_name}-episode-{episode}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()

                        streaming_link = data.get("sources", {})
                        streaming_link = streaming_link[-1]
                        streaming_link = streaming_link.get("url", None)

                        if streaming_link:
                            anime_title = anime_name.replace("-", " ").capitalize()

                            flask_host = "http://192.168.0.105:5000"
                            watch_url = (
                                f"{flask_host}/watch?stream_link={streaming_link}"
                            )

                            embed = discord.Embed(
                                title=f"Anime: {eng_name} | Episode: {episode}",
                                color=discord.Color.blue(),
                            )

                            embed.add_field(
                                name="Watch Now",
                                value=f"[Click Here]({watch_url})",
                                inline=False,
                            )

                            embed.set_image(url=cover_image)

                            await ctx.respond(embed=embed)

                        else:
                            await ctx.respond(
                                "No Streaming Link Found For This Episode"
                            )
                    else:
                        await ctx.respond(
                            f"Failed To Fetch Streaming Link: {response.status}"
                        )
        except Exception as e:
            await ctx.respond(f"An Error Occurred : {e}")
            traceback.print_exc()


def setup(bot):
    bot.add_cog(Anime(bot))
