# techbookfest21

技術書典向けの書籍「コードで読み解く愛車デミオの美学」制作リポジトリ。
Pythonの画像解析（OpenCV/Pillow/torchvision）で愛車のサイドビュー写真からプロポーション
（黄金比・グリッド）を算出・可視化する。

企画全体（目的・スケジュール・章立て）は [docs/tech_book_plan.md](docs/tech_book_plan.md) を参照。

## PoCスクリプト

```
python scripts/golden_ratio_poc.py <image_path> [grabcut|dl]
```

- `dl`（デフォルト）: 学習済みセグメンテーションモデル（DeepLabV3）で車体を抽出
- `grabcut`: OpenCVのGrabCutのみで車体を抽出（比較用に残している旧実装）

## 出力ファイルの運用ルール

`scripts/golden_ratio_poc.py` の出力画像は `output/YYYY-MM-DD/` に、実行した日付ごとのディレクトリに
分けて保存される（ファイル名は `<元画像名>_<method>_annotated_<HHMM>.jpg`）。

これは [logs/YYYY-MM-DD.md](logs) の研究ログと日付で対応させるためのルール。
「いつの実行結果か」をログと突き合わせて追えるように、必ず `output/YYYY-MM-DD/` の形式を保つこと。
新しく出力ディレクトリを作るスクリプトを追加する場合も、このルールに合わせること。

研究ログ自体の書き方は [docs/research_log_rules.md](docs/research_log_rules.md) を参照。

`output/` はGitの追跡対象外（`.gitignore`参照）。生成物は再実行すればいつでも作り直せるため。
