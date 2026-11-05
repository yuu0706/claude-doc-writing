# claude-doc-writing

| 項目 | 内容 |
| --- | --- |
| 対象 | 要件定義書・設計書・調査報告書・障害報告書・議事録・課題管理ツールへの投稿文など、人に読ませる業務資料 |
| 動作環境 | Claude Code。点検スクリプトに Python 3 |
| ライセンス | MIT（[LICENSE](LICENSE)） |

Claude Code に業務資料を書かせるときの決まりをまとめたスキル `doc-writing` を配布する。資料を作る・直す・レビューする依頼を受けると、Claude がこのスキルを読み込み、決まりに沿って書く。

## 1. このスキルでできること

| できること | 頼み方の例 |
| --- | --- |
| 要件定義書・設計書・調査報告書・障害報告書・議事録などを、資料の種類ごとの標準の構成で書く | 「要件定義書を書いて」「調査結果を報告書にまとめて」 |
| 会話の口調・絵文字を持ち込まず、常体の業務文書として書く | 「議事録を作って」 |
| 事実と推測を分け、根拠（コードのパスと行・データの取得日）を添えて書く | 「この調査を資料にまとめて」 |
| 書いた資料を提出前の点検項目で見直し、点検スクリプトで作り手側の事情（コミット番号・会話の語句など）の残りを数える | 「この資料をレビューして」 |
| 既存の資料に、その資料の文体・記号・章番号に合わせて書き足す | 「この設計書に追記して」 |
| Backlog などの課題管理ツールに貼る形に書き直す | 「Backlog に貼る形にして」 |

## 2. 使いどころの例

| 頼み方 | Claude が行うこと |
| --- | --- |
| 「この機能の要件定義書を書いて」 | 背景と目的・対象範囲（やらないこと）・前提と制約・機能要件・非機能要件・決定事項・未決事項の章立てで書き、未確定の点は一覧にまとめる |
| 「障害の調査結果を報告書にして」 | 結論を先に書き、根拠・検証の方法・未検証の範囲を分けて書く |
| 「この資料、提出前に見て」 | 点検項目に1つずつ答え、`scripts/deliverable-check.py` の当たりと合わせて、直す箇所を挙げる |

## 3. 扱わないこと

| 扱わないもの | 代わりに使うもの |
| --- | --- |
| 画面に表示する文言（ボタン・エラーメッセージ・サービスが利用者へ自動で送るメール） | [claude-ui-text](https://github.com/yuu0706/claude-ui-text) |
| GitHub の Issue からプルリクエストを作る流れのレビュー用の Design doc | [claude-design-and-ship](https://github.com/yuu0706/claude-design-and-ship) |

## 4. 入れ方

### 4.1 プラグインとして入れる

Claude Code の会話の中で、次を実行する。

```
/plugin marketplace add yuu0706/claude-doc-writing
/plugin install doc-writing@claude-doc-writing
```

シェルから入れる場合は次のとおり。

```sh
claude plugin marketplace add yuu0706/claude-doc-writing
claude plugin install doc-writing@claude-doc-writing
```

入れた後に新しい会話を始めると、スキルが読み込まれる。スキルの名前は `doc-writing:doc-writing` になる。

### 4.2 clone してリンクを張る

プラグインの仕組みを使わずに、スキル置き場へ直接置くこともできる。

```sh
git clone https://github.com/yuu0706/claude-doc-writing ~/claude-tools/claude-doc-writing
ln -s ~/claude-tools/claude-doc-writing/plugins/doc-writing/skills/doc-writing ~/.claude/skills/doc-writing
```

### 4.3 利用者ごとの上書きファイル

利用者ごとの運用や参照先は、`~/.config/claude-skills/doc-writing.local.md` に書く。ファイルがあれば Claude が読んで従い、無ければ本文の既定で進める。点検スクリプトで数えたい手元の語句の型は、`~/.config/claude-skills/doc-writing.local-patterns.txt` に1行に1つの正規表現で書く。

## 5. 更新・外し方

| 入れ方 | 更新 | 外し方 |
| --- | --- | --- |
| プラグイン | `/plugin marketplace update claude-doc-writing`。会話の中の `/plugin` の **Marketplaces** で自動更新も有効にできる | `/plugin uninstall doc-writing@claude-doc-writing` |
| clone とリンク | clone した場所で `git pull` | `rm ~/.claude/skills/doc-writing` |

プラグインの更新は、`plugins/doc-writing/.claude-plugin/plugin.json` の `version` が変わったときだけ届く。

## 6. 関係するスキル

| スキル | 関係 |
| --- | --- |
| [claude-ui-text](https://github.com/yuu0706/claude-ui-text) | 画面の文言を受け持つ。表記はどちらも JTF 日本語標準スタイルガイドに従う |
| [claude-design-and-ship](https://github.com/yuu0706/claude-design-and-ship) | レビュー用の短い Design doc を受け持つ |
| [yomiyasu](https://github.com/nanaism/yomiyasu)（外部） | 入れてあれば、文の組み立てに併用する。食い違う箇所は本スキルを優先する |

## 7. ライセンス

MIT License である。全文は [LICENSE](LICENSE) にある。
