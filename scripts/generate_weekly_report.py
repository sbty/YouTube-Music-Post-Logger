from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts.utils import (
    WEEKLY_REPORTS_DIR,
    ensure_directories,
    first_last_rows_by_video,
    int_value,
    latest_rows_by_video,
    parse_date,
    read_csv_rows,
    today_jst,
)


def main() -> None:
    ensure_directories()
    rows = read_csv_rows()
    if not rows:
        print("No CSV data found. Skipped weekly report.")
        return

    end_date = parse_date(today_jst())
    start_date = end_date - timedelta(days=6)
    period_rows = [
        row
        for row in rows
        if row.get("snapshot_date") and start_date <= parse_date(row["snapshot_date"]) <= end_date
    ]

    report_path = WEEKLY_REPORTS_DIR / f"{start_date.isoformat()}_{end_date.isoformat()}.md"
    report_path.write_text(build_report(period_rows, start_date.isoformat(), end_date.isoformat()), encoding="utf-8")
    print(f"Generated {report_path}")


def build_report(rows: list[dict[str, str]], start_date: str, end_date: str) -> str:
    latest_rows = latest_rows_by_video(rows)
    pairs = first_last_rows_by_video(rows)
    total_views = sum(int_value(row, "views") for row in latest_rows)
    total_likes = sum(int_value(row, "likes") for row in latest_rows)
    total_comments = sum(int_value(row, "comments") for row in latest_rows)

    growth_rows = []
    for video_id, (first, last) in pairs.items():
        growth_rows.append(
            {
                "title": last.get("title", ""),
                "url": last.get("url", ""),
                "view_growth": int_value(last, "views") - int_value(first, "views"),
                "like_growth": int_value(last, "likes") - int_value(first, "likes"),
                "comment_growth": int_value(last, "comments") - int_value(first, "comments"),
            }
        )
    growth_rows.sort(key=lambda row: row["view_growth"], reverse=True)

    lines = [
        f"# Weekly YouTube Report ({start_date} to {end_date})",
        "",
        "## Summary",
        "",
        f"- Videos tracked: {len(latest_rows)}",
        f"- Total latest views: {total_views}",
        f"- Total latest likes: {total_likes}",
        f"- Total latest comments: {total_comments}",
        "",
        "## Top View Growth",
        "",
        "| Rank | Title | View Growth | Like Growth | Comment Growth |",
        "|---:|---|---:|---:|---:|",
    ]

    for index, row in enumerate(growth_rows[:10], start=1):
        title = row["title"].replace("|", "\\|")
        lines.append(
            f"| {index} | [{title}]({row['url']}) | {row['view_growth']} | {row['like_growth']} | {row['comment_growth']} |"
        )

    if not growth_rows:
        lines.append("| - | No data | - | - | - |")

    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
