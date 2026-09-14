# スクリプト変更ログ運用ルール

`scripts/` 配下のスクリプトを変更したとき、後から（特に執筆期間中に）「その変更が
どんな意図で・何を変えたのか」を追えるようにするためのルール。

## 基本方針

スクリプトの変更履歴は git のコミット単位で追う。新しく変更ログ用のファイルは作らず、
コミットメッセージ自体を「後から読んで意図が分かる」粒度・フォーマットで書くことで、
`git log` / `git show` がそのままスクリプトの変更ログになるようにする。

## コミットの単位

- スクリプトの変更は、目的ごとにコミットを分ける（無関係な変更を1コミットに混ぜない）。
- 「修正」「コメント」のような、後から読んで意図が分からないコミットメッセージは禁止。

## コミットメッセージのフォーマット

リポジトリの commit template（[.gitmessage](../.gitmessage)、Conventional Commits
ベース）に従う。`git commit` 時にひな形が自動で挿入される（devcontainer では
postCreateCommand で `git config commit.template .gitmessage` が設定済み。手動で
設定する場合は `git config commit.template .gitmessage` を実行する）。

## 研究ログとの関係

その日にスクリプトを変更した場合、[docs/research_log_rules.md](research_log_rules.md)
に従って `logs/YYYY-MM-DD.md` にもその日の作業として記録する（何を試し、何が分かったか、
という物語としての記録）。コミットメッセージは個々の変更差分に対する「なぜ・何を」の
記録、研究ログはその日の作業全体の流れの記録、という役割分担にする。
