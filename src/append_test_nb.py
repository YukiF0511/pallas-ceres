import json

with open('c:/Work/pallas-ceres/doc/phase2-2.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

new_cell = {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 動作確認の手順\n",
    "\n",
    "構築が完了したら、以下の手順で正しく連携できているかをテストします。\n",
    "\n",
    "1. **ComfyUIサーバーの起動**\n",
    "   - Paperspace上で `main.py` を実行し、ComfyUIサーバー（通常は `localhost:6006` などのポート）を起動させます。\n",
    "2. **ブリッジスクリプトの実行**\n",
    "   - 別のターミナルを開き、作成した連携スクリプト（例: `python bridge.py`）を実行します。\n",
    "   - `Bolt app is running!` などの起動メッセージが表示され、待機状態になることを確認します。\n",
    "3. **メッセージの送信**\n",
    "   - スマホやPCのSlackアプリ（またはLINE）から、作成したBot宛にテスト用のプロンプト（例: `a cute dog`）を送信します。\n",
    "4. **処理状況の確認**\n",
    "   - ブリッジスクリプトのターミナルに「🎨 生成を開始します: a cute dog」といったログが出力され、直後にComfyUI側のターミナルでも生成処理（プログレスバー等）が走ることを確認します。\n",
    "5. **画像の受信**\n",
    "   - 画像生成が完了した後、Slackの同じチャット画面に生成された画像が自動でアップロード（返信）されればテスト成功です。\n"
   ]
}

notebook['cells'].append(new_cell)

with open('c:/Work/pallas-ceres/doc/phase2-2.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)
