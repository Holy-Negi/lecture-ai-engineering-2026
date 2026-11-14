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

- 取り組んだレベル：基礎 / 実装 / 発展
- やったこと：
- 結果：
- 気づき・疑問：
