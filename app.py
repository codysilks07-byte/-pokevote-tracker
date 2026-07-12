from supabase import create_client
from googleapiclient.discovery import build
from rapidfuzz import process
from collections import Counter
import pandas as pd
import re
import streamlit as st

st.set_page_config(page_title="PokéVote Tracker")

st.title("🎮 PokéVote Tracker")

# ------------------------
# API SETUP
# ------------------------

youtube = build(
    "youtube",
    "v3",
    developerKey=st.secrets["YOUTUBE_API_KEY"]
)

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# ------------------------
# LOAD FILES
# ------------------------

pokemon_df = pd.read_csv("pokemon.csv")
aliases_df = pd.read_csv("aliases.csv")
drawn_df = pd.read_csv("drawn.csv")

pokemon = pokemon_df["name"].tolist()
drawn = set(drawn_df["pokemon"].str.lower())

aliases = {}

for _, row in aliases_df.iterrows():
    aliases[row["alias"].lower()] = row["pokemon"]

video_url = st.text_input("YouTube Shorts URL")


# ------------------------
# HELPERS
# ------------------------

def get_video_id(url):
    if "/shorts/" in url:
        return url.split("/shorts/")[1].split("?")[0]

    if "v=" in url:
        return url.split("v=")[1].split("&")[0]

    return None


# ------------------------
# MAIN
# ------------------------

if st.button("Analyze"):

    video_id = get_video_id(video_url)

    if not video_id:
        st.error("Invalid YouTube URL")
        st.stop()

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

        # aliases
        for alias, real_name in aliases.items():

            if alias in text:
                votes.append(real_name)

        # exact matches
        for name in pokemon:

            if re.search(r"\b" + re.escape(name.lower()) + r"\b", text):
                votes.append(name)

        # fuzzy matches
        words = re.findall(r"[a-z]+", text)

        for word in words:

            if len(word) < 5:
                continue

            match = process.extractOne(word, pokemon)

            if match and match[1] >= 95:
                votes.append(match[0])

    leaderboard = Counter(votes)

    # ----------------------------------
    # CHECK IF VIDEO ALREADY PROCESSED
    # ----------------------------------

    processed = (
        supabase
        .table("processed_videos")
        .select("video_id")
        .eq("video_id", video_id)
        .execute()
    )

    if len(processed.data) == 0:

        for pokemon_name, vote_count in leaderboard.items():

            existing = (
                supabase
                .table("leaderboard")
                .select("*")
                .eq("Pokemon", pokemon_name)
                .execute()
            )

            if existing.data:

                current_votes = existing.data[0]["Votes"]

                (
                    supabase
                    .table("leaderboard")
                    .update({
                        "Votes": current_votes + vote_count
                    })
                    .eq("Pokemon", pokemon_name)
                    .execute()
                )

            else:

                (
                    supabase
                    .table("leaderboard")
                    .insert({
                        "Pokemon": pokemon_name,
                        "Votes": vote_count
                    })
                    .execute()
                )

        (
            supabase
            .table("processed_videos")
            .insert({
                "video_id": video_id
            })
            .execute()
        )

        st.success("Added votes from this video!")

    else:

        st.info("This video has already been counted.")

    # ----------------------------------
    # LOAD LEADERBOARD
    # ----------------------------------

    rows = (
        supabase
        .table("leaderboard")
        .select("*")
        .execute()
    )

    df = pd.DataFrame(rows.data)

    if not df.empty:

        df["Drawn"] = df["Pokemon"].str.lower().isin(drawn)

        df = df.sort_values(
            "Votes",
            ascending=False
        )

        st.success(f"Downloaded {len(comments)} comments")

        st.dataframe(
            df,
            use_container_width=True
        )

        remaining = df[df["Drawn"] == False]

        if len(remaining):

            winner = remaining.iloc[0]

            st.success(
                f"⭐ Recommended Next Pokémon: {winner['Pokemon']} ({winner['Votes']} votes)"
            )
