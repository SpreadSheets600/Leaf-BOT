from AnilistPython  import Anilist

Anilist = Anilist()


anime_dict = Anilist.get_anime("one piece", deepsearch=True)
print(anime_dict)