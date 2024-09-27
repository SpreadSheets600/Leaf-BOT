import os
import json
import asyncio
import aiohttp
import requests

from AnilistPython import Anilist

Anilist = Anilist()

anime_dict = Anilist.get_anime(anime_name="one piece", deepsearch=True)
print()
anime_id = Anilist.get_anime_id("one piece")
print(anime_dict)
print()
print(anime_id)