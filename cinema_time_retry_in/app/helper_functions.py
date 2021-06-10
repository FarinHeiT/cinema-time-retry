import random
import redis
import json
import requests
from bs4 import BeautifulSoup as BS


def random_color():
    return ["#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])]


def generate_room_name():
    words = ("Haphazard", "Hodgepodge", "Hogwash", "Hoodwink", "Hubbub", "Itty-Bitty"
             , "Pompous", "Rambunctious", "Ramshackle", "Shenanigans", "Shrubs", "Skedaddle"
             , "Squabble", "Squeegee", "Squelch", "Wishy-Washy", "Shrubbery", "Taradiddle"
             , "Snickersnee", "Widdershins", "Collywobbles", "Gubbins", "Bumfuzzle", "Cattywampus"
             , "Hatskers")

    first = random.choice(words)
    seconond = random.choice(words)
    word = first + seconond + str(random.randint(0, 9999))

    return word


# DELETES EVERYTING FROM REDIS!!!
def clear_redis_db():
    redis_db = redis.Redis(host='localhost', port=6379, db=0)

    for i in redis_db.scan_iter():
        redis_db.delete(i)


def get_youtube_title(url):
    web_url = requests.get(url)
    html = BS(web_url.content, 'html.parser')
    print(html.title.get_text())

