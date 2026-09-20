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

```
python scripts/roofline_detection_poc.py <image_path> [grabcut|dl]
```

車体シルエットのルーフライン（上端の曲線）を検出し、元画像にそのまま重ね描きするだけのPoC。
フーリエ近似（下記 `roofline_fourier_poc.py`）に進む前段として、まず検出結果そのものを確認するための
ステップとして分けている。ルーフライン抽出のロジックは `roofline_fourier_poc.py` の
`extract_roofline()` を再利用している。

```
python scripts/roofline_fourier_poc.py <image_path> [grabcut|dl] [harmonics_csv]
```

車体シルエットのルーフライン（上端の曲線）を1次元の `y = f(x)` として切り出し、フーリエ級数（sin/cos）
で近似・再構成するPoC。`harmonics_csv`（例: `1,3,5,10,20`）で、何項まで残して再構成するかを指定できる
（省略時は `1,3,5,10,20,50,100`）。項数ごとに元画像＋元曲線＋再構成曲線を重ねたパネルを分けて並べ（1枚に
全項数を重ねると線が重なって見分けづらいため）、下にパワースペクトラムを添えた1枚の画像として出力する。
車体セグメンテーションは `golden_ratio_poc.py` の実装を再利用している。

## 出力ファイルの運用ルール

各PoCスクリプトの出力画像は `output/YYYY-MM-DD/` に、実行した日付ごとのディレクトリに
分けて保存される（ファイル名は `<元画像名>_<method>_<種別>_<HHMM>.{jpg,png}`）。

これは [logs/YYYY-MM-DD.md](logs) の研究ログと日付で対応させるためのルール。
「いつの実行結果か」をログと突き合わせて追えるように、必ず `output/YYYY-MM-DD/` の形式を保つこと。
新しく出力ディレクトリを作るスクリプトを追加する場合も、このルールに合わせること。

研究ログ自体の書き方は [docs/research_log_rules.md](docs/research_log_rules.md) を参照。

`output/` はGitの追跡対象外（`.gitignore`参照）。生成物は再実行すればいつでも作り直せるため。
