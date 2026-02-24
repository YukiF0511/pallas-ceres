import json

with open('c:/Work/pallas-ceres/doc/phase2-2.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

for cell in notebook['cells']:
    if cell['cell_type'] == 'markdown' and len(cell['source']) > 0 and '## 構築のステップ' in cell['source'][0]:
        new_source = [
            '## 構築のステップ\n',
            '\n',
            '1. **アプリ登録**:\n',
            '   - **Slackの場合**: [api.slack.com](https://api.slack.com/) でAppを作成し、Socket Modeを有効化、`message.channels` などの権限（Scopes）を付与する。\n',
            '     - **SLACK_BOT_TOKEN (`xoxb-`) の取得**: `OAuth & Permissions` ページで `Bot Token Scopes` に必要な権限（`chat:write`, `files:write`, `channels:history` など）を追加し、ワークスペースにインストールして発行。\n',
            '     - **SLACK_APP_TOKEN (`xapp-`) の取得**: `Basic Information` ページ下部の `App-Level Tokens` 欄から `connections:write` 権限を付与してトークンを発行。\n',
            '   - **LINEの場合**: [LINE Developers](https://developers.line.biz/ja/) でプロバイダーと「Messaging API」チャネルを作成する。\n',
            '     - **CHANNEL_ACCESS_TOKEN の取得**: チャネル設定の `Messaging API設定` タブの一番下にある「チャネルアクセストークン (ロングターム)」から発行。\n',
            '     - **CHANNEL_SECRET の取得**: `チャネル基本設定` タブの「チャネルシークレット」欄で確認。\n',
            '2. **ブリッジスクリプトの作成**:\n',
            '   - 本メモの雛形をベースに、ComfyUIのAPI連携部分（Step3で作成したJSON制御）を組み込む。\n',
            '3. **常駐実行**:\n',
            '   - ComfyUIサーバーを起動した状態で、別ターミナルでブリッジスクリプトを実行する。\n',
            '\n',
            '## 次のアクション\n',
            '\n',
            '- **Slack Appの作成**: 接続が容易なSlackでまずプロトタイプを作成することを推奨。\n',
            '- **ngrokの検討（LINEの場合のみ）**: LINEを選択する場合は、`apt install ngrok` 等でトンネリング環境を準備する。\n'
        ]
        cell['source'] = new_source
        break

with open('c:/Work/pallas-ceres/doc/phase2-2.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, ensure_ascii=False, indent=1)
