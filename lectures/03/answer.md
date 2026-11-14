# 第3回 解答

## 演習

- 第1回（素のLLM）とエージェントの回答の違い：
  一般的な推測や誤った情報を出力するのではなく、[glossary.json](../../data/glossary.json)を参照して回答を出力している。
- `--trace` で見えたツール呼び出し（ツール名と引数）：
  `make_quiz({'lecture': 3})`
- 1つの質問での LLM 呼び出し回数（`requests`）：
  `2`
- 追加したツールと、docstring に書いた説明：

  ```python
  def make_quiz(lecture: int) -> str:
    """指定した回の用語から1つ選び、
    確認問題と答えを返す。

    「第2回の確認問題を出して」のように、
    復習用の問題を求められたときに使う。"""
    terms = [t for t in load_glossary() if t["lecture"] == lecture]
    if not terms:
        available = sorted({t["lecture"] for t in load_glossary()})
        return f"第{lecture}回の用語はありません。用語がある回：{', '.join(map(str, available))}"
    choice = random.choice(terms)
    out = {
        "question": f"「{choice['term']}」の意味は？",
        "answer": choice["definition"],
    }
    return json.dumps(out, ensure_ascii=False)
    ```

## 宿題

### 基礎

- 取り組んだレベル：基礎
- やったこと：
  [agent.py](../../app/agent.py)の`INSTRUCTIONS`を編集し、`回答の最後に、関係する回（第N回）を示す。`から`回答の最後に、確認問題を1問出す。`に変更した。
- 結果：
  変更前は回答の最後に`（第N回）`と表示されていたが、変更後は`## 確認問題`というセクションが追加され、確認問題が出題された。
- 気づき・疑問：
  `reqests`が`2`から`3`に上がっていた。また、複数回質問したところ、確認問題に対して回答も併記する場合もあれば、ヒントを出す場合、何も併記しない場合など結果にばらつきがあった。

### 実装

- 取り組んだレベル：実装
- やったこと：
  [tools.py](../../app/tools.py)に`save_learning_log`関数を作り、[learning_log](../../learning_log/)ディレクトリに学習記録を Markdown 形式で保存できるようにした。

  ```python
  def save_learning_log(content: str) -> str:
    """利用者が学習内容の記録・保存を頼んだときに使う。
    学習の記録を learning_log/ フォルダに保存する。
    content には学んだ内容を Markdown で要約したものを格納する。
    実行前にシステムが利用者へ確認するので、モデル側で確認を取らずにそのまま呼んでよい。
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    path = LOG_DIR / f"{today}.md"
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"## {datetime.now():%H:%M}\n\n{content}\n\n")
    return f"{path}に学習記録を保存しました。"
    ```

    この関数を[agent.py](../../app/agent.py)の`agent`に登録し、`main()`関数に承認ループ処理を追加した。

    ```python
    def main() -> None:
        ...
        try:
            model = build_model()
            result = target.run_sync(args.question, model=model)
            while isinstance(result.output, DeferredToolRequests):
                results = DeferredToolResults()
                for call in result.output.approvals:
                    print(f"\n[承認待ち] {call.tool_name}")
                    print(call.args_as_dict().get("content", ""))
                    answer = input("実行してよいですか？ [y/N] ")
                    results.approvals[call.tool_call_id] = answer.strip().lower() == "y"
                result = target.run_sync(
                    message_history=result.all_messages(),
                    deferred_tool_results=results,
                    model=model,
                )
        except ModelHTTPError as e:
          ...
    ```

- 結果：
  `uv run python -m app.agent --trace "今日はAIエージェントの仕組みについて学びました。学習記録に保存してください。"`を実行すると、学習記録の内容が表示され、この内容で実行してよいかのインプット（`[y/N]`）を求められた。
  `y`を入力すると学習記録が`learning_log`ディレクトリに作成され、`N`を入力するとその操作は行われなかった。
- 気づき・疑問：
  `N`を入力したとき、`お手元のメモなどに今回の学びをまとめておいていただければ幸いです。`のような一言が添えられた。

### 発展

- 取り組んだレベル：発展
- やったこと：
  1. 以下の構成で [adk_agent](../../adk_agent/) ディレクトリを作成し、[agent.py](../../adk_agent/glossary_agent/agent.py) と [__init__.py](../../adk_agent/glossary_agent/__init__.py) を作成した。
  
  ```text
  adk_agent/
  └── glossary_agent/
      ├── __init__.py
      └── agent.py
  ```

  ```python: __init__.py
  from . import agent
  ```

  ```python: agent.py
  from app import tools
  from app.agent import INSTRUCTIONS
  from google.adk.agents import Agent

  root_agent = Agent(
      model="gemini-3.5-flash-lite",
      name="glossary_agent",
      instruction=INSTRUCTIONS,
      tools=[
          tools.search_glossary,
          tools.get_lecture_summary,
          tools.make_quiz,
      ],  # 演習で使ったツール
  )
  ```

  2. ADK を起動し2つの質問をして、Pydantic AI と回答を比較した。

- 結果：
  - `AIE2026の講座の宿題にある「3レベル」とは何ですか？`
      Pydantic Ai と変わらず、用語集をしっかり参照して回答を出力していた。
  - `第2回の内容から確認問題を1問出して`
      こちらも変わらず、用語集を参照して問題を出していた。
  
- 気づき・疑問：
  複数回質問して試したが、Pydantic AI とは違って確認問題に何か（ヒント、答え、コメントなど）を併記することはなかった。
