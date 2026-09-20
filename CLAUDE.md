# プロジェクト概要

技術書典向けの書籍「コードで読み解く愛車デミオの美学」制作リポジトリ。
Pythonの画像解析（OpenCV/Pillow）で愛車のサイドビュー写真からプロポーション
（黄金比・グリッド）を算出・可視化する。

書籍の目的・スケジュール・章立てなど企画全体は [docs/tech_book_plan.md](docs/tech_book_plan.md) に
まとまっている。タスクの優先順位や章立てに関わる判断をする際は必ずこれを参照すること。

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
