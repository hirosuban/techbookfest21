# プロジェクト概要

技術書典向けの書籍「デミオを買ったので、カーライフをPythonで分析してみた」制作リポジトリ。
中古で購入したマツダ デミオの給油・走行距離・維持費を記録し、pandas・SQL（SQLite/DuckDB）・
matplotlibで分析・可視化する。

本は著者3人の合同誌で、このリポジトリで作っているのはそのうちユーザー（著者の一人）が担当する
デミオのパートだけ。他の2人のパートはこのリポジトリの対象外。

（2026-10-04に、画像解析でサイドビュー写真のプロポーションを分析する旧企画「コードで読み解く
愛車デミオの美学」から全面的に乗り換えた。旧企画のPoCスクリプトはアーカイブとしてリポジトリに
残っている。経緯は[docs/tech_book_plan.md](docs/tech_book_plan.md)冒頭と
[logs/2026-10-04.md](logs/2026-10-04.md)を参照。）

書籍の目的・スケジュール・章立てなど企画全体は [docs/tech_book_plan.md](docs/tech_book_plan.md) に
まとまっている。タスクの優先順位や章立てに関わる判断をする際は必ずこれを参照すること。

## 参考資料

宣伝・告知・タイトル・表紙・書籍ページ・頒布準備など「本を届ける」側の判断をする際は、
[docs/ref_todokeru_kufuu.md](docs/ref_todokeru_kufuu.md)（「届ける工夫」改訂第2版の要約と、
本書への当てはめメモ）を参照すること。原本のPDFは `参考/` にある。

## 宣伝（研究用ではない）

`promo/` は合同誌の宣伝用で、本の研究用コード（`scripts/`）とは別物。`promo/x_autopost/` は
Googleスプレッドシートに書いた投稿を@hirosubanから自動投稿するApps Scriptで、仕組み・セットアップ・
運用は [promo/x_autopost/README.md](promo/x_autopost/README.md) を参照。宣伝の作業は研究ログには書かない。

## 研究ログ

作業ログの運用ルール（フォーマット・書き方・粒度）は [docs/research_log_rules.md](docs/research_log_rules.md)
にまとめてある。実質的な作業をした日は、このルールに従って `logs/YYYY-MM-DD.md` にログを残すこと。

スクリプトの出力ファイルは日付ごとのディレクトリ（`output/YYYY-MM-DD/`）に分け、その日のログと
対応付けること。詳細・命名規則は [README.md](README.md) を参照。

## スクリプト変更ログ

`scripts/` 配下のスクリプトを変更したときは、後から（特に執筆期間中に）変更の意図・内容を
追えるように、コミットメッセージに背景と変更内容を書くこと。ルールの詳細・フォーマットは
[docs/script_change_log_rules.md](docs/script_change_log_rules.md) を参照。

## Claudeの作業方針

研究ログへの追記のような低リスクな作業は、ユーザーに確認を取らずそのまま進めること。
詳細・対象範囲は [docs/agent_working_rules.md](docs/agent_working_rules.md) を参照。
