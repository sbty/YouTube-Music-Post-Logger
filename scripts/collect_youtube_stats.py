from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import requests

sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts.utils import ensure_directories, load_env, require_env, today_jst, upsert_csv_rows


YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
MAX_RESULTS = 50


def youtube_get(endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
    response = requests.get(f"{YOUTUBE_API_BASE}/{endpoint}", params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_latest_video_ids(api_key: str, channel_id: str) -> list[str]:
    data = youtube_get(
        "search",
        {
            "key": api_key,
            "channelId": channel_id,
            "part": "id",
            "order": "date",
            "type": "video",
            "maxResults": MAX_RESULTS,
        },
    )

    video_ids = []
    for item in data.get("items", []):
        video_id = item.get("id", {}).get("videoId")
        if video_id:
            video_ids.append(video_id)
    return video_ids


def fetch_video_details(api_key: str, video_ids: list[str]) -> list[dict[str, Any]]:
    if not video_ids:
        return []

    data = youtube_get(
        "videos",
        {
            "key": api_key,
            "id": ",".join(video_ids),
            "part": "snippet,statistics",
            "maxResults": MAX_RESULTS,
        },
    )
    return data.get("items", [])


def build_csv_rows(items: list[dict[str, Any]], snapshot_date: str) -> list[dict[str, str]]:
    rows = []
    for item in items:
        video_id = item.get("id", "")
        snippet = item.get("snippet", {})
        statistics = item.get("statistics", {})
        thumbnails = snippet.get("thumbnails", {})
        if not video_id:
            continue

        rows.append(
            {
                "snapshot_date": snapshot_date,
                "video_id": video_id,
                "title": snippet.get("title", ""),
                "published_at": snippet.get("publishedAt", ""),
                "views": statistics.get("viewCount", "0"),
                "likes": statistics.get("likeCount", "0"),
                "comments": statistics.get("commentCount", "0"),
                "thumbnail_url": get_thumbnail_url(thumbnails),
                "tags": ";".join(snippet.get("tags", [])),
                "description": snippet.get("description", ""),
                "url": f"https://www.youtube.com/watch?v={video_id}",
            }
        )
    return rows


def get_thumbnail_url(thumbnails: dict[str, Any]) -> str:
    for size in ("maxres", "standard", "high", "medium", "default"):
        thumbnail = thumbnails.get(size)
        if thumbnail and thumbnail.get("url"):
            return thumbnail["url"]
    return ""


def main() -> None:
    ensure_directories()
    load_env()

    api_key = require_env("YOUTUBE_API_KEY")
    channel_id = require_env("YOUTUBE_CHANNEL_ID")
    snapshot_date = today_jst()

    video_ids = fetch_latest_video_ids(api_key, channel_id)
    items = fetch_video_details(api_key, video_ids)
    rows = build_csv_rows(items, snapshot_date)
    saved_count = upsert_csv_rows(rows)

    print(f"Saved {saved_count} rows to data/youtube_log.csv for snapshot_date={snapshot_date}.")


if __name__ == "__main__":
    main()
