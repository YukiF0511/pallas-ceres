# 技術メモ：Phase2 Step5 - メッセージングアプリ連携（Min環境）の構築

## 結論とDoD（完了定義）

- **結論**：Paperspace上で「メッセージングアプリのAPIを監視するブリッジスクリプト」を常駐させることで、スマホ等から送ったプロンプトをComfyUIに転送し、生成された画像をアプリへ返信する仕組みを構築する。
- **DoD（完了定義）**：メッセージングアプリからテキストを送信し、数十秒後に生成された画像が同じチャット欄に自動で届くこと。

## アーキテクチャ構成（Slack Socket Mode）

```mermaid
sequenceDiagram
    participant User as ユーザー(スマホ/PC)
    participant Slack as Slack Server
    participant Bridge as Bridge Script
    participant Comfy as ComfyUI API(localhost)
    participant FS as 実行環境(outputフォルダ)

    Note over Bridge,Slack: Socket Mode(WebSocket)による常時接続

    User->>Slack: プロンプト送信(例: "a cute cat")
    Slack-->>Bridge: イベント通知(Message Event)
    
    Bridge->>Bridge: ワークフローJSONの書き換え
    Bridge->>Comfy: ジョブ投入(HTTP POST /prompt)
    
    Note over Comfy,FS: 画像生成プロセス
    Comfy->>FS: 画像ファイル書き出し(.png)

    Bridge->>FS: ファイル監視 / 生成完了検知
    FS-->>Bridge: 画像データ取得
    
    Bridge->>Slack: 画像アップロード(files.upload)
    Slack-->>User: 画像をチャットに表示
```

## コンポーネントの役割

- **Slack Server**: メッセージの仲介および画像のホスティングを担当
- **Bridge Script**:
  - SlackからのWebSocket接続を維持（Socket Mode）
  - 受信メッセージをComfyUI用JSONにパース
  - 生成完了後の画像ファイルをSlackへアップロード
- **ComfyUI API**: `main.py` 実行により起動するローカルサーバー（ポート6006）

## アプリ別アーキテクチャ選定

### 案A：Slack (Socket Mode) ★推奨
- **メリット**: 外部URL（webhook）の設定が不要。企業のセキュリティポリシー下でも動きやすい。
- **必要トークン**: `SLACK_BOT_TOKEN` (`xoxb-`), `SLACK_APP_TOKEN` (`xapp-`)
- **主要ライブラリ**: `slack_bolt`

### 案B：LINE (Messaging API)
- **メリット**: 日本国内で最も普及しており、日常的に使いやすい。
- **デメリット**: Webhook（外部からの接続）が必要なため、Paperspaceで ngrok や Cloudflare Tunnel を常駐させる必要がある。また、画像送信には静的なURLが必要。
- **必要トークン**: `CHANNEL_ACCESS_TOKEN`, `CHANNEL_SECRET`

## 実装のポイント（Slack Socket Modeの場合）

```python
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(token="xoxb-your-bot-token")

@app.message("")  # 全メッセージに反応
def handle_message(message, say):
    prompt_text = message['text']
    say(f"🎨 生成を開始します: {prompt_text}")
    
    # ここにComfyUIへのAPIリクエストを記述
    # image_path = run_comfyui(prompt_text)
    
    # 画像のアップロード
    app.client.files_upload_v2(
        channel=message['channel'],
        file=image_path,
        title="Generated Image"
    )

if __name__ == "__main__":
    handler = SocketModeHandler(app, "xapp-your-app-token")
    handler.start()
```

## 構築のステップ

1. **アプリ登録**:
   - **Slackの場合**: [api.slack.com](https://api.slack.com/) でAppを作成し、Socket Modeを有効化、`message.channels` などの権限（Scopes）を付与する。
     - **SLACK_BOT_TOKEN (`xoxb-`) の取得**: `OAuth & Permissions` ページで `Bot Token Scopes` に必要な権限（`chat:write`, `files:write`, `channels:history` など）を追加し、ワークスペースにインストールして発行。
     - **SLACK_APP_TOKEN (`xapp-`) の取得**: `Basic Information` ページ下部の `App-Level Tokens` 欄から `connections:write` 権限を付与してトークンを発行。
   - **LINEの場合**: [LINE Developers](https://developers.line.biz/ja/) でプロバイダーと「Messaging API」チャネルを作成する。
     - **CHANNEL_ACCESS_TOKEN の取得**: チャネル設定の `Messaging API設定` タブの一番下にある「チャネルアクセストークン (ロングターム)」から発行。
     - **CHANNEL_SECRET の取得**: `チャネル基本設定` タブの「チャネルシークレット」欄で確認。
2. **ブリッジスクリプトの作成**:
   - 本メモの雛形をベースに、ComfyUIのAPI連携部分（Step3で作成したJSON制御）を組み込む。
3. **常駐実行**:
   - ComfyUIサーバーを起動した状態で、別ターミナルでブリッジスクリプトを実行する。

## 次のアクション

- **Slack Appの作成**: 接続が容易なSlackでまずプロトタイプを作成することを推奨。
- **ngrokの検討（LINEの場合のみ）**: LINEを選択する場合は、`apt install ngrok` 等でトンネリング環境を準備する。

## 動作確認の手順

構築が完了したら、以下の手順で正しく連携できているかをテストします。

1. **ComfyUIサーバーの起動**
   - Paperspace上で `main.py` を実行し、ComfyUIサーバー（通常は `localhost:6006` などのポート）を起動させます。
2. **ブリッジスクリプトの実行**
   - 別のターミナルを開き、作成した連携スクリプト（例: `python bridge.py`）を実行します。
   - `Bolt app is running!` などの起動メッセージが表示され、待機状態になることを確認します。
3. **メッセージの送信**
   - スマホやPCのSlackアプリ（またはLINE）から、作成したBot宛にテスト用のプロンプト（例: `a cute dog`）を送信します。
4. **処理状況の確認**
   - ブリッジスクリプトのターミナルに「🎨 生成を開始します: a cute dog」といったログが出力され、直後にComfyUI側のターミナルでも生成処理（プログレスバー等）が走ることを確認します。
5. **画像の受信**
   - 画像生成が完了した後、Slackの同じチャット画面に生成された画像が自動でアップロード（返信）されればテスト成功です。
