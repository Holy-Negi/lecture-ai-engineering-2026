# 第6回 解答

## 演習

<!-- [tool call] の行は、表示された行をそのまま貼り付けてください。終わらなかった STEP は、空欄のままでかまいません。 -->

- STEP 1 のツールの名前：`glossary`
- STEP 2 の [tool call]：`glossary_search_glossary({'query': '3レベル'})`
- STEP 3 の [tool call]：`fetch_fetch({'url': 'https://modelcontextprotocol.io/'})`
- STEP 4 の [tool call]：`aws_aws___search_documentation({'search_phrase': 'Amazon S3 versioning overview', 'topics': ['general']})`
- 気づき・疑問：外部で動くサーバーに接続すると、しっかり外部サーバーのツール名画表示されていた。

## 宿題

### 基礎

- 取り組んだレベル：基礎
- やったこと：サーバー側の [`mcp_server.py`](../../app/mcp_server.py) に `server.tool()(tools.get_lecture_summary)` の 1 行を書き足し、`get_lecture_summary` を公開した。
- 結果：`uv run python -m app.mcp_agent --trace "第2回では何を学びますか？"` を実行し、書き足したツールが呼ばれることを確認した。
  - [tool call]：`glossary_get_lecture_summary({'lecture': 2})`
  - [tool return]：`data/lectures/02.md` の要点（「# 第2回 ファインチューニングとLoRA」から始まる本文）が返った
  - [usage]：入力 5,942 tokens / 出力 226 tokens / モデル応答 2 回
  - 回答は、事前学習とファインチューニングの違い、SFT、PEFT と LoRA、QLoRA、演習の内容を箇条書きでまとめ、末尾に「関係する回：第2回」が付いていた
  - `uv run pytest -q` は 21 件すべて通った
- 気づき・疑問：

### 実装

<!-- 基礎・実装・発展のどれか1つに取り組めば完了です。 -->

- 取り組んだレベル：実装
- やったこと：第3回講義で作成した関数 `tools.make_quiz` を [`tools.py`](../../app/tools.py) に追加し、サーバー側の [`mcp_server.py`](../../app/mcp_server.py) に登録した。
- 結果：`uv run python -m app.mcp_agent --list-tools` で `[glossary_make_quiz]` が表示されることを確認した。また、`uv run python -m app.mcp_agent --trace "第99回のクイズを作って"` を実行して範囲外の講義回を指定されたときに、それが存在しないことが表示されることを確認した。
- 気づき・疑問：

### 発展

- 取り組んだレベル：発展
- やったこと：Claude Code の MCP サーバーの設定方法を、公式ドキュメントを参照して調べた。
- 結果：

  - ターミナルで `claude mcp add ...` を実行して、外部公開されている MCP サーバーを追加できる。
  - 引数 `--scope` を指定することで、どの範囲で適用するかを決められる。
  - プロジェクトスコープの場合はルートディレクトリの `./.mcp.json` に、それ以外は `~/.claude.json` に mcpServers 設定を記述できる。
  - 書き方とした配下の通り。HTTP による接続のため [`mcp_servers.json`](../../app/mcp_servers.json) とは形式が異なった。

  ```JSON
  {
    "mcpServers": {
      "api-server": {
        "type": "http",
        "url": "${API_BASE_URL:-https://api.example.com}/mcp",
        "headers": { "Authorization": "Bearer ${API_KEY}" }
      }
    }
  }
  ```
