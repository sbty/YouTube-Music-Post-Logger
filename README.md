# YouTube Music Post Logger

Suno AIで毎日YouTube投稿している曲のパフォーマンスを自動記録するためのMVPツールです。

YouTube Data APIから最新動画50件の動画情報と統計情報を取得し、JST基準の日次スナップショットとして `data/youtube_log.csv` に保存します。CSVから週次・月次のMarkdownレポートも生成し、後からChatGPTで分析しやすいログを残します。

## MVP範囲

- YouTube Data APIから最新50件の動画情報を取得
- `data/youtube_log.csv` に日次スナップショットを保存
- 重複キー `snapshot_date + video_id` の行は上書き
- 週次Markdownレポートを生成
- 月次Markdownレポートを生成
- GitHub Actionsで毎日自動実行

## MVPでは実装しないこと

- YouTube Analytics API
- Google Sheets連携
- Obsidian連携
- OpenAI API連携

## CSVカラム

保存先:

```text
data/youtube_log.csv
```

カラム:

```text
snapshot_date,video_id,title,published_at,views,likes,comments,thumbnail_url,tags,description,url
```

説明:

- `snapshot_date`: JST基準の取得日
- `video_id`: YouTube動画ID
- `title`: 動画タイトル
- `published_at`: YouTube上の公開日時
- `views`: 再生数
- `likes`: 高評価数
- `comments`: コメント数
- `thumbnail_url`: サムネイルURL
- `tags`: YouTubeタグ。複数タグは `;` 区切り
- `description`: 動画説明文
- `url`: 動画URL

同じ日に同じ動画を再取得した場合は、`snapshot_date + video_id` をキーにして既存行を上書きします。

## セットアップ

Python 3.11以上を推奨します。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`.env.example` をコピーして `.env` を作成します。

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

`.env` にYouTube Data APIキーとチャンネルIDを設定します。

```env
YOUTUBE_API_KEY=your_youtube_data_api_key
YOUTUBE_CHANNEL_ID=your_youtube_channel_id
```

## ローカル実行

YouTube Data APIから最新50件を取得し、CSVに保存します。

```bash
python scripts/collect_youtube_stats.py
```

直近7日間の再生数増加ランキングを含む週次レポートを生成します。

```bash
python scripts/generate_weekly_report.py
```

当月の再生数増加ランキングを含む月次レポートを生成します。

```bash
python scripts/generate_monthly_report.py
```

一通り実行する例:

```bash
python scripts/collect_youtube_stats.py
python scripts/generate_weekly_report.py
python scripts/generate_monthly_report.py
```

## GitHub Actions

`.github/workflows/collect-youtube-stats.yml` により、毎日JST 09:00に自動実行されます。

GitHubリポジトリの `Settings > Secrets and variables > Actions > Repository secrets` に以下を登録してください。

- `YOUTUBE_API_KEY`
- `YOUTUBE_CHANNEL_ID`

ActionsはCSVとMarkdownレポートを更新した場合、自動でコミットします。
