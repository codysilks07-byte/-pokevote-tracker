from googleapiclient.discovery import build
import streamlit as st

st.set_page_config(page_title="PokéVote Tracker")

st.title("🎮 PokéVote Tracker")

api_key = st.text_input("YouTube API Key", type="password")

video_url = st.text_input("YouTube Shorts URL")

if st.button("Analyze"):

    if not api_key:
        st.error("Enter your YouTube API key.")
        st.stop()

    youtube = build("youtube", "v3", developerKey=api_key)

    st.success("Connected to YouTube!")

    st.write("Next step will pull every comment automatically.")
