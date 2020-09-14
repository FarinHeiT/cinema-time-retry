import requests
from random import randint


def generate_room_name():
    link = "https://random-word-api.herokuapp.com/word?number=2&swear=0"
    first_word, second_word = requests.get(link).json()
    return first_word.title() + second_word.title() + str(randint(1, 100))