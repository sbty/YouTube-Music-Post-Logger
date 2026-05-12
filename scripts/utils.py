from __future__ import annotations

import csv
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

try:
    from dotenv import load_dotenv as dotenv_load
except ModuleNotFoundError:
    dotenv_load = None


JST = timezone(timedelta(hours=9))
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"
WEEKLY_REPORTS_DIR = REPORTS_DIR / "weekly"
MONTHLY_REPORTS_DIR = REPORTS_DIR / "monthly"
CSV_PATH = DATA_DIR / "youtube_log.csv"

CSV_FIELDS = [
    "snapshot_date",
    "video_id",
    "title",
    "published_at",
    "views",
    "likes",
    "comments",
    "thumbnail_url",
    "tags",
    "description",
    "url",
]


def ensure_directories() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    WEEKLY_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    MONTHLY_REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def load_env() -> None:
    if dotenv_load is not None:
        dotenv_load(PROJECT_ROOT / ".env")


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Environment variable {name} is required.")
    return value


def today_jst() -> str:
    return datetime.now(JST).date().isoformat()


def read_csv_rows(path: Path = CSV_PATH) -> list[dict[str, str]]:
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8", newline="") as f:
        return [normalize_row(row) for row in csv.DictReader(f)]


def normalize_row(row: dict[str, str]) -> dict[str, str]:
    normalized = dict(row)
    normalized["views"] = normalized.get("views") or normalized.get("view_count", "")
    normalized["likes"] = normalized.get("likes") or normalized.get("like_count", "")
    normalized["comments"] = normalized.get("comments") or normalized.get("comment_count", "")
    return normalized


def write_csv_rows(rows: Iterable[dict[str, str]], path: Path = CSV_PATH) -> None:
    ensure_directories()
    sorted_rows = sorted(
        rows,
        key=lambda row: (row.get("snapshot_date", ""), row.get("published_at", ""), row.get("video_id", "")),
    )

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in sorted_rows:
            writer.writerow({field: row.get(field, "") for field in CSV_FIELDS})


def upsert_csv_rows(new_rows: Iterable[dict[str, str]], path: Path = CSV_PATH) -> int:
    rows_by_key = {
        (row.get("snapshot_date", ""), row.get("video_id", "")): row
        for row in read_csv_rows(path)
        if row.get("snapshot_date") and row.get("video_id")
    }

    count = 0
    for row in new_rows:
        key = (row["snapshot_date"], row["video_id"])
        rows_by_key[key] = row
        count += 1

    write_csv_rows(rows_by_key.values(), path)
    return count


def parse_date(value: str):
    return datetime.strptime(value, "%Y-%m-%d").date()


def int_value(row: dict[str, str], key: str) -> int:
    value = row.get(key) or "0"
    try:
        return int(value)
    except ValueError:
        return 0


def latest_rows_by_video(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    latest: dict[str, dict[str, str]] = {}
    for row in rows:
        video_id = row.get("video_id")
        snapshot_date = row.get("snapshot_date")
        if not video_id or not snapshot_date:
            continue
        if video_id not in latest or snapshot_date > latest[video_id].get("snapshot_date", ""):
            latest[video_id] = row
    return list(latest.values())


def first_last_rows_by_video(rows: Iterable[dict[str, str]]) -> dict[str, tuple[dict[str, str], dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        video_id = row.get("video_id")
        if video_id:
            grouped[video_id].append(row)

    result = {}
    for video_id, video_rows in grouped.items():
        sorted_rows = sorted(video_rows, key=lambda row: row.get("snapshot_date", ""))
        result[video_id] = (sorted_rows[0], sorted_rows[-1])
    return result
