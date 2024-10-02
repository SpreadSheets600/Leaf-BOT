from threading import Thread
from UTILS.WatchAnime import run

def keep_alive():
    t = Thread(target=run)
    t.start()
