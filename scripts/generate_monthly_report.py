from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts.utils import (
    MONTHLY_REPORTS_DIR,
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
        print("No CSV data found. Skipped monthly report.")
        return

    today = parse_date(today_jst())
    month_prefix = today.strftime("%Y-%m")
    period_rows = [row for row in rows if row.get("snapshot_date", "").startswith(month_prefix)]

    report_path = MONTHLY_REPORTS_DIR / f"{month_prefix}.md"
    report_path.write_text(build_report(period_rows, month_prefix), encoding="utf-8")
    print(f"Generated {report_path}")


def build_report(rows: list[dict[str, str]], month_prefix: str) -> str:
    latest_rows = latest_rows_by_video(rows)
    pairs = first_last_rows_by_video(rows)
    total_views = sum(int_value(row, "view_count") for row in latest_rows)
    total_likes = sum(int_value(row, "like_count") for row in latest_rows)
    total_comments = sum(int_value(row, "comment_count") for row in latest_rows)

    growth_rows = []
    for video_id, (first, last) in pairs.items():
        growth_rows.append(
            {
                "title": last.get("title", ""),
                "url": last.get("url", ""),
                "view_growth": int_value(last, "view_count") - int_value(first, "view_count"),
                "like_growth": int_value(last, "like_count") - int_value(first, "like_count"),
                "comment_growth": int_value(last, "comment_count") - int_value(first, "comment_count"),
            }
        )
    growth_rows.sort(key=lambda row: row["view_growth"], reverse=True)

    lines = [
        f"# Monthly YouTube Report ({month_prefix})",
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
