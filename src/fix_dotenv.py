import json

with open('c:/Work/pallas-ceres/doc/phase2-2.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

for cell in notebook['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        if "load_dotenv()" in source:
            cell['source'] = [
                "import os\n",
                "from dotenv import load_dotenv\n",
                "from slack_bolt import App\n",
                "from slack_bolt.adapter.socket_mode import SocketModeHandler\n",
                "\n",
                "# .envファイルから環境変数を読み込む（Jupyter Notebookの階層を明示）\n",
                "load_dotenv(dotenv_path='.env')\n",
                "\n",
                "# 環境変数のBot Tokenでアプリを初期化\n",
                "app = App(token=os.environ.get(\"SLACK_BOT_TOKEN\"))"
            ]

with open('c:/Work/pallas-ceres/doc/phase2-2.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)
