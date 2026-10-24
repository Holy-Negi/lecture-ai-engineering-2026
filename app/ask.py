"""第1回: 素のLLMに質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問をする
    uv run python -m app.ask "LoRAとは何ですか？" --temperature 0.5
    uv run python -m app.ask --chat     # 会話履歴を保ったまま続けて質問する

ツールを持たない「素の」呼び出し。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse

from google import genai
from google.genai import errors, types

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"

# 会話モードを終了する入力
EXIT_COMMANDS = {"exit", "quit"}


def print_usage(response: types.GenerateContentResponse) -> None:
    """応答の入力・出力トークン数を表示する。"""
    usage = response.usage_metadata
    input_tokens = usage.prompt_token_count if usage else "不明"
    output_tokens = usage.candidates_token_count if usage else "不明"
    print(f"[トークン] 入力: {input_tokens}, 出力: {output_tokens}")


def ask(question: str, temperature: float | None = None) -> str:
    client = genai.Client(api_key=get_api_key())
    # temperature=None のときはモデルの既定値が使われる
    response = client.models.generate_content(
        model=MODEL,
        contents=question,
        config=types.GenerateContentConfig(temperature=temperature),
    )
    print_usage(response)
    return response.text


def chat(temperature: float | None = None, first_question: str | None = None) -> None:
    """会話履歴を保ったまま、対話的に質問を続ける。"""
    client = genai.Client(api_key=get_api_key())
    # chats.create で作ったチャットは、送受信した内容を履歴として保持し、
    # send_message のたびに履歴全体をまとめて API に送る
    session = client.chats.create(
        model=MODEL,
        config=types.GenerateContentConfig(temperature=temperature),
    )
    print("会話モード（exit で終了）\n")

    question = first_question
    while True:
        if question is None:
            try:
                question = input("あなた> ").strip()
            except (EOFError, KeyboardInterrupt):  # Ctrl+Z / Ctrl+C
                print()
                break
        else:
            print(f"あなた> {question}")

        if question.lower() in EXIT_COMMANDS:
            break
        if question:
            try:
                response = session.send_message(question)
                print_usage(response)
                print(f"{response.text}\n")
            except errors.APIError as e:
                # 失敗したターンは履歴に残らないため、同じ質問を再送できる
                print(f"{api_error_message(e.code, e.message)}\n")
        question = None


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=None)
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="生成のランダムさ（0.0〜2.0）。省略時はモデルの既定値",
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="会話履歴を保ったまま続けて質問する",
    )
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    print(f"[temperature] {args.temperature if args.temperature is not None else '既定値'}")

    if args.chat:
        chat(args.temperature, args.question)
        return

    question = args.question or DEFAULT_QUESTION
    print(f"[質問] {question}\n")
    try:
        print(ask(question, args.temperature))
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
