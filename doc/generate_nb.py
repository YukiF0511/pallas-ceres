import json

notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# 技術メモ：Phase2 Step5 - メッセージングアプリ連携（Min環境）の構築\n",
    "\n",
    "## 結論とDoD（完了定義）\n",
    "\n",
    "- **結論**：Paperspace上で「メッセージングアプリのAPIを監視するブリッジスクリプト」を常駐させることで、スマホ等から送ったプロンプトをComfyUIに転送し、生成された画像をアプリへ返信する仕組みを構築する。\n",
    "- **DoD（完了定義）**：メッセージングアプリからテキストを送信し、数十秒後に生成された画像が同じチャット欄に自動で届くこと。\n",
    "\n",
    "## アーキテクチャ構成（Slack Socket Mode）\n",
    "\n",
    "```mermaid\n",
    "sequenceDiagram\n",
    "    participant User as ユーザー(スマホ/PC)\n",
    "    participant Slack as Slack Server\n",
    "    participant Bridge as Bridge Script\n",
    "    participant Comfy as ComfyUI API(localhost)\n",
    "    participant FS as 実行環境(outputフォルダ)\n",
    "\n",
    "    Note over Bridge,Slack: Socket Mode(WebSocket)による常時接続\n",
    "\n",
    "    User->>Slack: プロンプト送信(例: \"a cute cat\")\n",
    "    Slack-->>Bridge: イベント通知(Message Event)\n",
    "    \n",
    "    Bridge->>Bridge: ワークフローJSONの書き換え\n",
    "    Bridge->>Comfy: ジョブ投入(HTTP POST /prompt)\n",
    "    \n",
    "    Note over Comfy,FS: 画像生成プロセス\n",
    "    Comfy->>FS: 画像ファイル書き出し(.png)\n",
    "\n",
    "    Bridge->>FS: ファイル監視 / 生成完了検知\n",
    "    FS-->>Bridge: 画像データ取得\n",
    "    \n",
    "    Bridge->>Slack: 画像アップロード(files.upload)\n",
    "    Slack-->>User: 画像をチャットに表示\n",
    "```\n",
    "\n",
    "## コンポーネントの役割\n",
    "\n",
    "- **Slack Server**: メッセージの仲介および画像のホスティングを担当\n",
    "- **Bridge Script**:\n",
    "  - SlackからのWebSocket接続を維持（Socket Mode）\n",
    "  - 受信メッセージをComfyUI用JSONにパース\n",
    "  - 生成完了後の画像ファイルをSlackへアップロード\n",
    "- **ComfyUI API**: `main.py` 実行により起動するローカルサーバー（ポート6006）\n",
    "\n",
    "## アプリ別アーキテクチャ選定\n",
    "\n",
    "### 案A：Slack (Socket Mode) ★推奨\n",
    "- **メリット**: 外部URL（webhook）の設定が不要。企業のセキュリティポリシー下でも動きやすい。\n",
    "- **必要トークン**: `SLACK_BOT_TOKEN` (`xoxb-`), `SLACK_APP_TOKEN` (`xapp-`)\n",
    "- **主要ライブラリ**: `slack_bolt`\n",
    "\n",
    "### 案B：LINE (Messaging API)\n",
    "- **メリット**: 日本国内で最も普及しており、日常的に使いやすい。\n",
    "- **デメリット**: Webhook（外部からの接続）が必要なため、Paperspaceで ngrok や Cloudflare Tunnel を常駐させる必要がある。また、画像送信には静的なURLが必要。\n",
    "- **必要トークン**: `CHANNEL_ACCESS_TOKEN`, `CHANNEL_SECRET`\n",
    "\n",
    "## 実装のポイント（Slack Socket Modeの場合）\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 1. ライブラリのインポートとアプリの初期化"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "from slack_bolt import App\n",
    "from slack_bolt.adapter.socket_mode import SocketModeHandler\n",
    "\n",
    "# Bot Token (xoxb-) を指定してアプリを初期化\n",
    "app = App(token=\"xoxb-your-bot-token\")\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 2. メッセージイベントのハンドリング処理"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.message(\"\")  # 全メッセージに反応\n",
    "def handle_message(message, say):\n",
    "    prompt_text = message['text']\n",
    "    say(f\"🎨 生成を開始します: {prompt_text}\")\n",
    "    \n",
    "    # ここにComfyUIへのAPIリクエストを記述\n",
    "    # 例: image_path = run_comfyui(prompt_text)\n",
    "    image_path = \"path/to/your/generated/image.png\" # 仮のパス\n",
    "\n",
    "    # 画像をSlackにアップロード\n",
    "    app.client.files_upload_v2(\n",
    "        channel=message['channel'],\n",
    "        file=image_path,\n",
    "        title=\"Generated Image\"\n",
    "    )\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 3. アプリの起動（Socket Mode）"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "if __name__ == \"__main__\":\n",
    "    # App Token (xapp-) を指定してSocket Modeハンドラーを起動\n",
    "    handler = SocketModeHandler(app, \"xapp-your-app-token\")\n",
    "    handler.start()\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 構築のステップ\n",
    "\n",
    "1. **アプリ登録**:\n",
    "   - **Slackの場合**: [api.slack.com](https://api.slack.com/) でAppを作成し、Socket Modeを有効化、`message.channels` などの権限（Scopes）を付与する。\n",
    "   - **LINEの場合**: LINE Developersでチャネルを作成し、Messaging APIを有効化する。\n",
    "2. **ブリッジスクリプトの作成**:\n",
    "   - 本メモの雛形をベースに、ComfyUIのAPI連携部分（Step3で作成したJSON制御）を組み込む。\n",
    "3. **常駐実行**:\n",
    "   - ComfyUIサーバーを起動した状態で、別ターミナルでブリッジスクリプトを実行する。\n",
    "\n",
    "## 次のアクション\n",
    "\n",
    "- **Slack Appの作成**: 接続が容易なSlackでまずプロトタイプを作成することを推奨。\n",
    "- **ngrokの検討（LINEの場合のみ）**: LINEを選択する場合は、`apt install ngrok` 等でトンネリング環境を準備する。\n"
   ]
  }
 ],
 "metadata": {},
 "nbformat": 4,
 "nbformat_minor": 5
}

with open('c:/Work/pallas-ceres/doc/phase2-2.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)
