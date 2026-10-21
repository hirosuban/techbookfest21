# techbookfest21

技術書典向けの書籍「デミオを買ったので、カーライフをPythonで分析してみた」制作リポジトリ。
中古で購入したマツダ デミオの給油・走行距離・維持費を記録し、pandas・SQL（SQLite/DuckDB）・
matplotlibで分析・可視化する。

企画全体（目的・スケジュール・章立て）は [docs/tech_book_plan.md](docs/tech_book_plan.md) を参照。

> 2026-10-04に企画を全面的に乗り換えた。以前は画像解析（OpenCV/Pillow/torchvision）で
> サイドビュー写真のプロポーションをフーリエ変換・エピサイクル分解する本「コードで読み解く
> 愛車デミオの美学」を進めていた。以下の「旧企画（画像解析）のPoCスクリプト」は当時の
> 成果物としてリポジトリに残してあるが、現行企画とは独立したアーカイブ。経緯は
> [docs/tech_book_plan.md](docs/tech_book_plan.md)冒頭と[logs/2026-10-04.md](logs/2026-10-04.md)を参照。

## 現行企画：OBD2ログ関連スクリプト（`scripts/obd/`）

OBD2アダプター（Veepeak OBDCheck BLE + Car Scanner ELM OBD2）で取得したログ
（`obd_log/`、個人の走行データのためgitignore対象）を扱うスクリプト群。手順は
[docs/obd2_csv.md](docs/obd2_csv.md)参照。

```
python scripts/obd/load_obd_log.py "obd_log/<ログファイル名>.csv"
```

Car ScannerのCSVをpandas DataFrameとして読み込めることを確認するだけの最小スクリプト。

```
python scripts/obd/plot_speed_over_time.py "obd_log/<ログファイル名>.csv"
```

ログから時刻と車速の列を抜き出し、横軸=time・縦軸=speedの折れ線グラフを
`output/YYYY-MM-DD/`に出力する。日本語ラベルの文字化け対策（`scripts/obd/mpl_ja.py`）を
利用している。

## 旧企画（画像解析）のPoCスクリプト（`scripts/archive/`）

現行企画（カーライフ分析）とは無関係な、過去の企画「コードで読み解く愛車デミオの美学」の
PoC。経緯は[docs/tech_book_plan.md](docs/tech_book_plan.md)冒頭と
[logs/2026-10-04.md](logs/2026-10-04.md)を参照。

```
python scripts/archive/golden_ratio_poc.py <image_path> [grabcut|dl]
```

- `dl`（デフォルト）: 学習済みセグメンテーションモデル（DeepLabV3）で車体を抽出
- `grabcut`: OpenCVのGrabCutのみで車体を抽出（比較用に残している旧実装）

```
python scripts/archive/roofline_detection_poc.py <image_path> [grabcut|dl]
```

車体シルエットのルーフライン（上端の曲線）を検出し、元画像にそのまま重ね描きするだけのPoC。
フーリエ近似（下記 `roofline_fourier_poc.py`）に進む前段として、まず検出結果そのものを確認するための
ステップとして分けている。ルーフライン抽出のロジックは `roofline_fourier_poc.py` の
`extract_roofline()` を再利用している。

```
python scripts/archive/roofline_fourier_poc.py <image_path> [grabcut|dl] [harmonics_csv]
```

車体シルエットのルーフライン（上端の曲線）を1次元の `y = f(x)` として切り出し、フーリエ級数（sin/cos）
で近似・再構成するPoC。`harmonics_csv`（例: `1,3,5,10,20`）で、何項まで残して再構成するかを指定できる
（省略時は `1,3,5,10,20,50,100`）。項数ごとに元画像＋元曲線＋再構成曲線を重ねたパネルを分けて並べ（1枚に
全項数を重ねると線が重なって見分けづらいため）、下にパワースペクトラムと、項数ごとのRMSE・累積エネルギー比
の表を添えた1枚の画像として出力する（数値もすべて画像内に残るので、後から見返しても数字が追える）。
車体セグメンテーションは `golden_ratio_poc.py` の実装を再利用している。

## 宣伝用：X自動投稿（`promo/x_autopost/`）

合同誌の宣伝用のGoogle Apps Script。研究用のコードではなく、Pythonの環境とも関係しない。
詳細は[promo/x_autopost/README.md](promo/x_autopost/README.md)を参照。

## 出力ファイルの運用ルール

各PoCスクリプトの出力画像は `output/YYYY-MM-DD/` に、実行した日付ごとのディレクトリに
分けて保存される（ファイル名は `<元画像名>_<method>_<種別>_<HHMM>.{jpg,png}`）。

これは [logs/YYYY-MM-DD.md](logs) の研究ログと日付で対応させるためのルール。
「いつの実行結果か」をログと突き合わせて追えるように、必ず `output/YYYY-MM-DD/` の形式を保つこと。
新しく出力ディレクトリを作るスクリプトを追加する場合も、このルールに合わせること。

研究ログ自体の書き方は [docs/research_log_rules.md](docs/research_log_rules.md) を参照。

`output/` はGitの追跡対象外（`.gitignore`参照）。生成物は再実行すればいつでも作り直せるため。
