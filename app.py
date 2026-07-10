from googleapiclient.discovery import build
from urllib.parse import urlparse
import streamlit as st

st.set_page_config(page_title="PokéVote Tracker")

st.title("🎮 PokéVote Tracker")

api_key = st.secrets["YOUTUBE_API_KEY"]

youtube = build("youtube", "v3", developerKey=api_key)

video_url = st.text_input("YouTube Shorts URL")


def get_video_id(url):
    if "/shorts/" in url:
        return url.split("/shorts/")[1].split("?")[0]
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    return None


if st.button("Analyze"):

    video_id = get_video_id(video_url)

    if not video_id:
        st.error("Couldn't find a video ID.")
        st.stop()

    comments = []

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100,
        textFormat="plainText"
    )

    while request:
        response = request.execute()

        for item in response["items"]:
            comments.append(
                item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            )

        request = youtube.commentThreads().list_next(request, response)

    st.success(f"Downloaded {len(comments)} comments!")

    with st.expander("Show comments"):
        for c in comments:
            st.write(c)
