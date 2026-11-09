#!/usr/bin/env python3
"""人に渡す成果物（資料・スライドの原稿・投稿文）に、作り手側の事情が残っていないかを数える。

使い方: deliverable-check.py <ファイル>... [--phrases <語句のファイル>] [--allow-dates] [--max-parens <数>]
  - コミット番号らしい16進の文字列、PR 番号、日付、括弧の多さ、手元の禁止の型を数える。
  - 和文と半角英数の間の半角スペースを数える（`...` の中と URL は除く）。
  - --phrases には、利用者の発言のうち成果物に写してはならない語句を1行に1つ書いたファイルを渡す。
    見出し（# で始まる行・1行だけの短い行）に語句が残っていれば当たりにする。
  - --allow-dates は、取得日を書く資料（調査報告書など）で日付を当たりにしない。
  - --max-parens は、本文1,000文字あたりの括弧の数の上限（既定 5）。
  - 手元の禁止の型は ${XDG_CONFIG_HOME:-~/.config}/claude-skills/doc-writing.local-patterns.txt
    （1行に1つの正規表現。# で始まる行は注釈）から読む。
終了コード: 0 当たりなし / 1 当たりあり / 2 引数の誤り・ファイルを読めない
"""
import argparse
import os
import re
import sys

HASH_RE = re.compile(r"(?<![0-9A-Za-z])(?=[0-9a-f]*[a-f])(?=[0-9a-f]*[0-9])[0-9a-f]{7,40}(?![0-9A-Za-z])")
PR_RE = re.compile(r"(?:PR|プルリクエスト)\s*#?\d+|pull/\d+")
DATE_RE = re.compile(r"\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?")
VERSION_LINE_RE = re.compile(r"初版|版|更新|作成日")
PARENS_RE = re.compile(r"[（(]")
JA = r"[ぁ-んァ-ヶー一-龠々]"
SPACE_RE = re.compile(rf"(?<={JA}) +(?=[A-Za-z0-9])|(?<=[A-Za-z0-9]) +(?={JA})")
SKIP_RE = re.compile(r"`[^`]*`|https?://\S+")
LOCAL_PATTERNS = os.path.join(os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config"),
                              "claude-skills", "doc-writing.local-patterns.txt")


def read_lines(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.lstrip().startswith("#")]


def is_heading(line: str) -> bool:
    s = line.strip()
    return s.startswith("#") or (0 < len(s) <= 30 and not s.endswith("。") and not s.startswith(("-", "|", "*")))


def check(path: str, phrases: list, local: list, allow_dates: bool, max_parens: float) -> list:
    hits = []
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    in_code = False
    body_chars = 0
    parens = 0
    for no, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        body_chars += len(line)
        parens += len(PARENS_RE.findall(line))
        for m in HASH_RE.finditer(line):
            hits.append((no, "コミット番号らしい文字列", m.group(0)))
        for m in PR_RE.finditer(line):
            hits.append((no, "PR 番号", m.group(0)))
        if not allow_dates and not VERSION_LINE_RE.search(line):
            for m in DATE_RE.finditer(line):
                hits.append((no, "日付", m.group(0)))
        plain = SKIP_RE.sub(lambda m: "\0" * len(m.group(0)), line)
        for m in SPACE_RE.finditer(plain):
            hits.append((no, "和文と英字の間の空白", line[max(0, m.start() - 6):m.end() + 6]))
        for pat in local:
            for m in re.finditer(pat, line):
                hits.append((no, "手元の禁止の型", m.group(0)))
        if is_heading(line):
            for p in phrases:
                if p in line:
                    hits.append((no, "見出しに会話の語句", p))
    if body_chars >= 500:  # 短い文では1つの括弧で上限を超えるため数えない
        per = parens * 1000 / body_chars
        if per > max_parens:
            hits.append((0, "括弧が多い", f"{parens}個（1,000文字あたり {per:.1f}個。上限 {max_parens:g}個）"))
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--phrases")
    ap.add_argument("--allow-dates", action="store_true")
    ap.add_argument("--max-parens", type=float, default=5.0)
    try:
        args = ap.parse_args()
    except SystemExit:
        return 2
    try:
        phrases = read_lines(args.phrases) if args.phrases else []
        local = []
        if os.path.isfile(LOCAL_PATTERNS):
            for p in read_lines(LOCAL_PATTERNS):
                re.compile(p)
                local.append(p)
    except (OSError, re.error) as exc:
        print(f"語句か手元の禁止の型を読めませんでした: {exc}", file=sys.stderr)
        return 2
    total = 0
    for path in args.files:
        try:
            hits = check(path, phrases, local, args.allow_dates, args.max_parens)
        except OSError as exc:
            print(f"ファイルを読めませんでした: {path}: {exc}", file=sys.stderr)
            return 2
        for no, kind, text in hits:
            where = f"{path}:{no}" if no else path
            print(f"{where}\t{kind}\t{text}")
        total += len(hits)
    if total:
        print(f"当たりが {total}件 あります。成果物から外すか、残す理由を確かめてください。", file=sys.stderr)
        return 1
    print("当たりはありませんでした。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
