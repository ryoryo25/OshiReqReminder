import os
import time
import json
from datetime import datetime
from typing import TypedDict

from dotenv import load_dotenv
load_dotenv()
import tweepy
import schedule

class Song(TypedDict):
    song_title: str
    release_date: str
    song_hash_tag: str
    song_id_usen: str

API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

auth = tweepy.OAuthHandler(
    consumer_key=API_KEY,
    consumer_secret=API_KEY_SECRET
)
auth.set_access_token(
    key=ACCESS_TOKEN,
    secret=ACCESS_TOKEN_SECRET
)
api = tweepy.API(auth)

twitter = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_KEY_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

GROUP_NAME = "日向坂46"
SONGS_PATH = os.getenv("SONGS_PATH")

BASE_TEXT = """USEN 推し活リクエストで{group}の{song_title}をリクエストしよう！
https://usen.oshireq.com/song/{id}
#USEN推し活リクエスト #推しリク #{group}
{hash_tag}"""

EXTRA_TEXTS = [
    """18時になりました！
今日も投票しちゃいましょう！""", # 18:00
    """もう今日の分の投票はお済みですか？
まだの方は今のうちに投票しちゃいましょう！""", # 21:00
    """もう今日の分の投票はお済みですか？
まだの方は寝る前に投票しちゃいましょう！""", # 23:00
    """昨日の分の投票はお済みですか？
まだの方は朝のうちに投票しちゃいましょう！""", # 8:00
    """昨日の分の投票はお済みですか？
まだの方はお昼のうちに投票しちゃいましょう！""", # 12:00
    """もうそろそろ投票回数がリセットされます！
昨日の分の投票はお済みですか？
まだの方は今のうちに投票しちゃいましょう！""" # 15:00
]

def construct_text(song: Song, index: int):
    extra_text = EXTRA_TEXTS[index]
    base_text = BASE_TEXT.format(
        group=GROUP_NAME,
        song_title=song["song_title"],
        hash_tag=song["song_hash_tag"],
        id=song["song_id_usen"],
    )

    return extra_text + "\n\n↓ ↓ ↓\n\n" + base_text

def post_reminder(song: Song, index: int):
    text = construct_text(song, index)
    twitter.create_tweet(text=text)

def setup_jobs(song: Song):
    schedule.every().day.at("08:00").do(post_reminder, song=song, index=3)
    schedule.every().day.at("12:00").do(post_reminder, song=song, index=4)
    schedule.every().day.at("15:00").do(post_reminder, song=song, index=5)
    schedule.every().day.at("18:00").do(post_reminder, song=song, index=0)
    schedule.every().day.at("21:00").do(post_reminder, song=song, index=1)
    schedule.every().day.at("23:00").do(post_reminder, song=song, index=2)

def main():
    with open(SONGS_PATH, "r") as f:
        songs: list[Song] = json.load(f)
        songs.sort(key=lambda e: datetime.strptime(e["release_date"], "%Y-%m-%d"))
    latest_song = songs[-1]

    setup_jobs(latest_song)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()