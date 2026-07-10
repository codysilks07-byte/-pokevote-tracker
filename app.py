from googleapiclient.discovery import build
import streamlit as st

st.set_page_config(page_title="PokéVote Tracker")

st.title("🎮 PokéVote Tracker")

api_key = st.secrets["YOUTUBE_API_KEY"]

video_url = st.text_input("YouTube Shorts URL")

if st.button("Analyze"):

    if not video_url:
        st.error("Paste a YouTube Shorts URL.")
        st.stop()

    youtube = build("youtube", "v3", developerKey=api_key)

    st.success("✅ Connected to YouTube!")

    st.write("Next step: Pulling comments...")
