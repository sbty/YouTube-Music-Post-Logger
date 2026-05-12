# YouTube Music Post Logger

YouTube Data API から自分のチャンネルの最新動画情報と統計情報を取得し、日次スナップショットとして `data/youtube_log.csv` に保存するMVPツールです。

CSVから週次・月次のMarkdownレポートも生成できます。ローカル実行とGitHub Actionsでの毎日自動実行に対応しています。

## MVPで実装していること

- YouTube Data API からチャンネルの最新動画を取得
- 各動画の統計情報を取得
- JST基準の `snapshot_date` で `data/youtube_log.csv` に保存
- 重複キー `snapshot_date + video_id` の行は上書き
- `reports/weekly/` と `reports/monthly/` にMarkdownレポートを生成
- GitHub Actionsで毎日自動実行

## MVPで実装しないこと

- YouTube Analytics API
- Google Sheets連携
- Obsidian連携
- OpenAI API連携

## セットアップ

Python 3.11 以上を推奨します。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell の場合:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`.env.example` をコピーして `.env` を作成し、値を設定します。

```bash
cp .env.example .env
```

Windows PowerShell の場合:

```powershell
Copy-Item .env.example .env
```

`.env`:

```env
YOUTUBE_API_KEY=your_youtube_data_api_key
YOUTUBE_CHANNEL_ID=your_youtube_channel_id
```

## ローカル実行

最新動画情報と統計情報を取得してCSVに保存します。

```bash
python scripts/collect_youtube_stats.py
```

週次レポートを生成します。

```bash
python scripts/generate_weekly_report.py
```

月次レポートを生成します。

```bash
python scripts/generate_monthly_report.py
```

一通り実行する例:

```bash
python scripts/collect_youtube_stats.py
python scripts/generate_weekly_report.py
python scripts/generate_monthly_report.py
```

## CSV

保存先:

```text
data/youtube_log.csv
```

主な列:

- `snapshot_date`: JST基準の日付
- `video_id`: YouTube動画ID
- `title`: 動画タイトル
- `published_at`: 公開日時
- `url`: 動画URL
- `view_count`: 再生数
- `like_count`: 高評価数
- `comment_count`: コメント数

同じ `snapshot_date` と `video_id` の行がすでに存在する場合は、新しい取得結果で上書きします。

## GitHub Actions

`.github/workflows/collect-youtube-stats.yml` により、毎日JST 09:00に自動実行されます。

GitHubリポジトリの `Settings > Secrets and variables > Actions > Repository secrets` に以下を登録してください。

- `YOUTUBE_API_KEY`
- `YOUTUBE_CHANNEL_ID`

ActionsはCSVとレポートを更新した場合、自動でコミットします。
