from googleapiclient.discovery import build
from rapidfuzz import process
from collections import Counter
import pandas as pd
import streamlit as st

st.set_page_config(page_title="PokéVote Tracker")

st.title("🎮 PokéVote Tracker")

api_key = st.secrets["YOUTUBE_API_KEY"]
youtube = build("youtube", "v3", developerKey=api_key)

pokemon = [
    "Bulbasaur","Ivysaur","Venusaur","Charmander","Charmeleon","Charizard",
    "Squirtle","Wartortle","Blastoise","Caterpie","Butterfree","Pikachu",
    "Raichu","Sandshrew","Vulpix","Jigglypuff","Zubat","Oddish","Diglett",
    "Psyduck","Growlithe","Abra","Machop","Machamp","Geodude","Slowpoke",
    "Magnemite","Gastly","Haunter","Gengar","Onix","Cubone","Hitmonlee",
    "Hitmonchan","Lickitung","Koffing","Rhyhorn","Chansey","Scyther",
    "Magikarp","Gyarados","Lapras","Ditto","Eevee","Vaporeon","Jolteon",
    "Flareon","Snorlax","Dragonite","Mew","Mewtwo","Mudkip","Treecko",
    "Torchic","Azurill","Spheal","Joltik","Mimikyu","Garchomp","Lucario",
    "Greninja","Infernape","Rayquaza","Dialga","Lugia","Hoopa"
]

video_url = st.text_input("YouTube Shorts URL")

def get_video_id(url):
    if "/shorts/" in url:
        return url.split("/shorts/")[1].split("?")[0]
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    return None

if st.button("Analyze"):

    video_id = get_video_id(video_url)

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100,
        textFormat="plainText"
    )

    comments=[]

    while request:
        response=request.execute()

        for item in response["items"]:
            comments.append(
                item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            )

        request=youtube.commentThreads().list_next(request,response)

    votes=[]

    for comment in comments:

        words=comment.replace(","," ").replace("."," ").split()

        for word in words:
            match,score,_=process.extractOne(word,pokemon)

            if score>=90:
                votes.append(match)

    leaderboard=Counter(votes)

    df=pd.DataFrame(
        leaderboard.items(),
        columns=["Pokemon","Votes"]
    ).sort_values("Votes",ascending=False)

    st.success(f"Downloaded {len(comments)} comments")

    st.dataframe(df,use_container_width=True)

    st.download_button(
        "Download CSV",
        df.to_csv(index=False),
        file_name="pokemon_votes.csv"
    )
