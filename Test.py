from AnilistPython  import Anilist

Anilist = Anilist()


anime_dict = Anilist.get_anime("my hero academia", deepsearch=True)
print(anime_dict)