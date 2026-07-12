import os
from googleapiclient.discovery import build
from rapidfuzz import process
from collections import Counter
import pandas as pd
import re
import streamlit as st

st.set_page_config(page_title="PokéVote Tracker")

st.title("🎮 PokéVote Tracker")

api_key = st.secrets["YOUTUBE_API_KEY"]
youtube = build("youtube", developerKey=api_key, version="v3")

pokemon_df = pd.read_csv("pokemon.csv")
aliases_df = pd.read_csv("aliases.csv")
drawn_df = pd.read_csv("drawn.csv")

pokemon = pokemon_df["name"].tolist()
drawn = set(drawn_df["pokemon"].str.lower())

aliases = {}
for _, row in aliases_df.iterrows():
    aliases[row["alias"].lower()] = row["pokemon"]

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

        # aliases first
        for alias, real_name in aliases.items():
            if alias in text:
                votes.append(real_name)

        # exact matches
        for name in pokemon:
            if re.search(r"\b" + re.escape(name.lower()) + r"\b", text):
                votes.append(name)

        # fuzzy matching
        words = re.findall(r"[a-z]+", text)

        for word in words:

            if len(word) < 5:
                continue

            match = process.extractOne(word, pokemon)

            if match and match[1] >= 95:
                votes.append(match[0])

    leaderboard = Counter(votes)
# Load previous votes if they exist
if os.path.exists("votes.csv"):
    total_votes = pd.read_csv("votes.csv")
else:
    total_votes = pd.DataFrame(columns=["pokemon", "votes"])
    new_votes = pd.DataFrame(
    leaderboard.items(),
    columns=["pokemon", "votes"]
)

combined = pd.concat([total_votes, new_votes], ignore_index=True)

combined = (
    combined
    .groupby("pokemon", as_index=False)["votes"]
    .sum()
    .sort_values("votes", ascending=False)
)

combined.to_csv("votes.csv", index=False)

df = combined.rename(
    columns={
        "pokemon": "Pokemon",
        "votes": "Votes"
    }
)

    df["Drawn"] = df["Pokemon"].str.lower().isin(drawn)

    df = df.sort_values("Votes", ascending=False)

    st.success(f"Downloaded {len(comments)} comments")

    st.dataframe(df, use_container_width=True)

    remaining = df[df["Drawn"] == False]

    if len(remaining):
        winner = remaining.iloc[0]

        st.success(
            f"⭐ Recommended Next Pokémon: {winner['Pokemon']} ({winner['Votes']} votes)"
        )
