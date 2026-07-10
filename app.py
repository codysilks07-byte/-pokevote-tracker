from googleapiclientfrom googleapiclient.discovery import build
from rapidfuzz import process
from collections import Counter
import pandas as pd
import re
import streamlit as st

st.set_page_config(page_title="PokéVote Tracker")

st.title("🎮 PokéVote Tracker")

api_key = st.secrets["YOUTUBE_API_KEY"]
youtube = build("youtube", "v3", developerKey=api_key)

pokemon = [
    "Bulbasaur","Ivysaur","Venusaur","Charmander","Charmeleon","Charizard",
    "Squirtle","Wartortle","Blastoise","Pikachu","Raichu","Psyduck",
    "Machamp","Gengar","Ditto","Eevee","Snorlax","Dragonite","Mew",
    "Mewtwo","Mudkip","Azurill","Spheal","Joltik","Mimikyu",
    "Garchomp","Greninja","Infernape","Rayquaza","Dialga",
    "Lugia","Hoopa","Ceruledge","Falinks"
]

pokemon_lower = {p.lower(): p for p in pokemon}

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

    comments = []

    while request:
        response = request.execute()

        for item in response["items"]:
            comments.append(
                item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            )

        request = youtube.commentThreads().list_next(request, response)

    votes = []

    for comment in comments:

        text = comment.lower()

        # Exact matches first
        for name in pokemon_lower:
            if re.search(r"\b" + re.escape(name) + r"\b", text):
                votes.append(pokemon_lower[name])

        # Fuzzy match only longer words
        words = re.findall(r"[a-z]+", text)

        for word in words:

            if len(word) < 5:
                continue

            if word in pokemon_lower:
                continue

            match = process.extractOne(word, pokemon)

            if match and match[1] >= 95:
                votes.append(match[0])

    leaderboard = Counter(votes)

    df = (
        pd.DataFrame(
            leaderboard.items(),
            columns=["Pokemon", "Votes"]
        )
        .sort_values("Votes", ascending=False)
    )

    st.success(f"Downloaded {len(comments)} comments")

    st.dataframe(df, use_container_width=True)
        df.to_csv(index=False),
        file_name="pokemon_votes.csv"
    )
