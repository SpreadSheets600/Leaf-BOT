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
                embed = discord.Embed(
                    title=anime["title"], color=discord.Color.random()
                )
                embed.add_field(name="ID", value=anime["id"], inline=False)
                embed.add_field(name="Type", value=anime["type"], inline=False)
                embed.add_field(
                    name="Sub / Dub",
                    value=f"{anime['sub']} / {anime['dub']}",
                    inline=False,
                )

                embed.set_thumbnail(url=anime["image"])

                embeds.append(embed)

            view = AnimeNavigationButtons(embeds, page)
            await ctx.respond(embed=embeds[0], view=view)
        else:
            await ctx.respond("No Anime Found For The Search Query", ephemeral=True)


class AnimeNavigationButtons(discord.ui.View):
    def __init__(self, embeds, page):
        super().__init__(timeout=60)
        self.embeds = embeds
        self.page = page

    async def on_timeout(self):
        self.disable_all_items()
        await self.message.edit(view=self)

    @discord.ui.button(label="<", style=discord.ButtonStyle.primary)
    async def previous_page(self, button, interaction):
        if self.page > 0:
            self.page -= 1
            await self.update_anime_results(interaction)

    @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
    async def next_page(self, button, interaction):
        if self.page < len(self.embeds) - 1:
            self.page += 1
            await self.update_anime_results(interaction)

    @discord.ui.button(label="ℹ️", style=discord.ButtonStyle.primary)
    async def anime_info(self, button, interaction):

        await interaction.response.defer()

        data = await fetch_anime_info(self.embeds[self.page].fields[0].value)

        if data:
            embed = discord.Embed(
                title=data["title"],
                description=data["description"],
                color=discord.Color.blue(),
            )
            embed.add_field(name="MAL ID", value=data["malID"], inline=False)
            embed.add_field(name="Type", value=data["type"], inline=False)
            embed.add_field(name="Status", value=data["status"], inline=False)
            embed.add_field(name="Release", value=data["releaseDate"], inline=False)
            embed.add_field(
                name="Episodes", value=data["episodes"][-1]["number"], inline=False
            )

            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send("Anime Info Not Found", ephemeral=True)

    async def update_anime_results(self, interaction):
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)


def setup(bot):
    bot.add_cog(Anime(bot))
