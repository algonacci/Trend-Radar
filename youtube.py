import os
from googleapiclient.discovery import build


def get_youtube_trends():
    api_key = os.getenv("YOUTUBE_API_KEY")
    youtube = build("youtube", "v3", developerKey=api_key)

    request = youtube.videos().list(
        part="snippet",
        chart="mostPopular",
        regionCode="ID",
        maxResults=20,
    )

    response = request.execute()

    trending_videos = []
    for item in response.get("items", []):
        video_title = item["snippet"]["title"]
        video_thumbnail = item["snippet"]["thumbnails"]["medium"]["url"]
        video_id = item["id"]
        trending_videos.append(
            {
                "title": video_title,
                "thumbnail": video_thumbnail,
                "id": video_id,
            }
        )

    return trending_videos
