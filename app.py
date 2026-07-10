import streamlit as st

st.set_page_config(page_title="PokéVote Tracker")

st.title("🎮 PokéVote Tracker")

st.write("Paste a YouTube Shorts link below.")

video_url = st.text_input("YouTube URL")

if st.button("Analyze"):
    if video_url:
        st.success("Video received!")
        st.write(video_url)
    else:
        st.error("Please paste a YouTube link.")
