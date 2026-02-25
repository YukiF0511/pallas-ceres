import json

with open('c:/Work/pallas-ceres/doc/phase2-2.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Update markdown to mention .env
for cell in nb['cells']:
    if cell['cell_type'] == 'markdown' and '## 実装のポイント' in "".join(cell['source']):
        cell['source'] = [
            "## 実装のポイント（Slack Socket Modeの場合）\n",
            "\n",
            "> [!IMPORTANT]\n",
            "> セキュリティ上の観点から、トークン等の機密情報は直接コード内に記述せず、`.env` ファイルなどを使用して環境変数から読み込むことを推奨します。\n",
            "> 事前に `pip install python-dotenv` でライブラリをインストールし、同じ階層に以下の内容で `.env` ファイルを作成してください。\n",
            "> \n",
            "> ```ini\n",
            "> SLACK_BOT_TOKEN=xoxb-your-bot-token\n",
            "> SLACK_APP_TOKEN=xapp-your-app-token\n",
            "> ```"
        ]

# Update code cells
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        if "App(token=" in source:
            cell['source'] = [
                "import os\n",
                "from dotenv import load_dotenv\n",
                "from slack_bolt import App\n",
                "from slack_bolt.adapter.socket_mode import SocketModeHandler\n",
                "\n",
                "# .envファイルから環境変数を読み込む\n",
                "load_dotenv()\n",
                "\n",
                "# 環境変数のBot Tokenでアプリを初期化\n",
                "app = App(token=os.environ.get(\"SLACK_BOT_TOKEN\"))"
            ]
            cell['execution_count'] = None
        elif "SocketModeHandler(app" in source:
            cell['source'] = [
                "if __name__ == \"__main__\":\n",
                "    # 環境変数のApp TokenでSocket Modeハンドラーを起動\n",
                "    handler = SocketModeHandler(app, os.environ.get(\"SLACK_APP_TOKEN\"))\n",
                "    handler.start()"
            ]
            cell['execution_count'] = None

with open('c:/Work/pallas-ceres/doc/phase2-2.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)
