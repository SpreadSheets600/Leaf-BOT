import os
import asyncio
import discord
import aiohttp
import traceback
from discord import ui
from discord import option
from discord.ext import pages
from dotenv import load_dotenv
from discord.ext.pages import *
from discord.ext import commands
from AnilistPython import Anilist
from discord.ui import Button, View
from discord import SlashCommandGroup

anilist = Anilist()
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


async def fetch_anime_search(query, page):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://astrumanimeapi.vercel.app/anime/zoro/{query}"
        ) as response:
            if response.status == 200:
                return await response.json()
            return None


async def fetch_anime_info(anime_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://astrumanimeapi.vercel.app/anime/zoro/info?id={anime_id}"
        ) as response:
            if response.status == 200:
                return await response.json()
            return None

async def fetch_anime_episodes(episode_id):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://astrumanimeapi.vercel.app/anime/zoro/watch?episodeId={episode_id}"
        ) as response:
            if response.status == 200:
                return await response.json()
            return None


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

    @anime.command(name="search", description="Search For Anime")
    async def anime_search(self, ctx: discord.ApplicationContext, query: str):

        await ctx.defer()

        query = query.replace(" ", "-")

        page = 1
        data = await fetch_anime_search(query, page)

        embeds = []

        if data and data["results"]:
            for anime in data["results"]:
                embed = discord.Embed(title=anime["title"], color=0xFCEFC1)
                embed.add_field(name="Type", value=anime["type"], inline=False)
                embed.add_field(name="Duration", value=anime["duration"], inline=False)
                embed.add_field(
                    name="Sub / Dub",
                    value=f"{anime['sub']} / {anime['dub']}",
                    inline=False,
                )

                embed.set_footer(text=f"ID : {anime['id']}")
                embed.set_thumbnail(url=anime["image"])

                embeds.append(embed)

            view = AnimeSearchNavigationButtons(embeds, page)
            await ctx.respond(embed=embeds[0], view=view)
        else:
            await ctx.respond("No Anime Found For The Search Query", ephemeral=True)

    @anime.command(name="episodes", description="Get Anime Episodes")
    async def anime_episodes(self, ctx: discord.ApplicationContext, anime_id: str):

        await ctx.defer()

        data = await fetch_anime_info(anime_id)

        if data:

            al_id = data["alID"]

            anilist = Anilist()
            anime_dict = anilist.get_anime_with_id(al_id)

            cover_image = anime_dict.get("banner_image", None)

            episodes = data.get("episodes", [])
            if episodes:
                embeds = []

                for episode in episodes:
                    embed = discord.Embed(
                        title=episode["title"],
                        color=0xFCEFC1,
                    )

                    embed.add_field(name="Episode Number", value=episode["number"])
                    embed.add_field(name="Is Filler", value=episode["isFiller"])

                    if cover_image:
                        embed.set_image(url=cover_image)

                    embed.set_footer(text=f"ID : {episode["id"]}")

                    embeds.append(embed)

                view = AnimeEpisodeNavigationButtons(embeds, 0)
                await ctx.respond(embed=embeds[0], view=view)


class AnimeSearchNavigationButtons(discord.ui.View):
    def __init__(self, embeds, page):
        super().__init__(timeout=60)
        self.embeds = embeds
        self.page = page

    async def on_timeout(self):
        self.disable_all_items()
        await self.message.edit(view=self)

    @discord.ui.button(label="<", style=discord.ButtonStyle.primary)
    async def previous_page(self, button, interaction):
        self.page -= 1
        await self.update_anime_results(interaction)

    @discord.ui.button(label="ℹ️", style=discord.ButtonStyle.primary)
    async def anime_info(self, button, interaction):

        await interaction.response.defer()

        data = await fetch_anime_info(
            self.embeds[self.page].footer.text.split(":")[-1].strip()
        )

        if data:
            al_id = data["alID"]

            anilist = Anilist()
            anime_dict = anilist.get_anime_with_id(al_id)

            anime_desc = anime_dict.get("desc", None)

            if anime_desc:
                anime_desc.replace("<i>", "").replace("</i>", "")
                anime_desc = anime_desc.split("<br>")

            embed = discord.Embed(
                title=anime_dict["name_english"],
                color=0xFCEFC1,
            )

            if anime_desc:
                embed.add_field(name="Synopsis", value=anime_desc[0], inline=False)
            if anime_dict["genres"]:
                embed.add_field(
                    name="Genres", value=", ".join(anime_dict["genres"]), inline=False
                )
            if data["episodes"][-1]["number"]:
                embed.add_field(
                    name="Episodes", value=data["episodes"][-1]["number"], inline=True
                )
            if anime_dict["average_score"]:
                embed.add_field(
                    name="Average Score",
                    value=anime_dict["average_score"],
                    inline=True,
                )

            next_airing_ep = anime_dict.get("next_airing_ep", None)

            if next_airing_ep:
                current_ep = next_airing_ep["episode"] - 1

                embed.set_footer(
                    text=f"Next Airing Episode : {next_airing_ep['episode']} | Current Episode : {current_ep}"
                )
            else:
                embed.set_footer(text="Anime Has Finished Airing")

            if anime_dict["cover_image"]:
                embed.set_image(url=anime_dict["banner_image"])

            await interaction.followup.send(embed=embed)

        else:
            await interaction.followup.send("Anilist Data Not Found")

    @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
    async def next_page(self, button, interaction):
        self.page = 0
        self.page += 1
        await self.update_anime_results(interaction)

    async def update_anime_results(self, interaction):
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)


class AnimeEpisodeNavigationButtons(discord.ui.View):
    def __init__(self, embeds, page):
        super().__init__(timeout=60)
        self.embeds = embeds
        self.page = page

    async def on_timeout(self):
        self.disable_all_items()
        await self.message.edit(view=self)

    @discord.ui.button(label="<", style=discord.ButtonStyle.primary)
    async def previous_page(self, button, interaction):
        self.page -= 1
        await self.update_anime_results(interaction)

    @discord.ui.button(label="📺", style=discord.ButtonStyle.primary)
    async def watch_episode(self, button, interaction):

        await interaction.response.defer()

        data = await fetch_anime_episodes(
            self.embeds[self.page].footer.text.split(":")[-1].strip()
        )

        if data:
            url = data["sources"][0]["url"]

            flask_host = "http://192.168.0.105:5000"
            watch_url = (
                f"{flask_host}/watch?stream_link={url}"
            )

            embed = discord.Embed(
                title="Watch Episode",
                description=f"[Click Here To Watch]({watch_url})",
                color=0xFCEFC1,
            )

            embed.

    @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
    async def next_page(self, button, interaction):
        self.page += 1
        await self.update_anime_results(interaction)

    async def update_anime_results(self, interaction):
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)


def setup(bot):
    bot.add_cog(Anime(bot))
