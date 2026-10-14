"""
OBD2ログから、エンジン回転数・加速・自動車速度・冷却水温度を1枚の画像に
縦に並べて出力するスクリプト（横軸=timeを共有する小さな多面グラフ）。

4項目は単位もスケールも異なるため、1つのグラフに重ねず(2軸グラフは作らない)、
パネルを縦に分けて横軸(time)だけ共有する構成にしている。
ログが途切れた区間はgap_utils.break_on_gaps()で線を分断する。

使い方:
    python scripts/obd/plot_multi_metric.py "obd_log/2026-10-04 20-34-30.csv"
"""
import sys
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # devcontainerはヘッドレスなのでファイル出力のみのバックエンドにする
import matplotlib.pyplot as plt
import pandas as pd

from gap_utils import break_on_gaps
from load_obd_log import load_obd_log
from mpl_ja import set_japanese_font

set_japanese_font()

# (列名, パネルのy軸ラベル, dataviz skillのcategorical色)
METRICS = [
    ("エンジン回転数 (rpm)", "rpm", "#2a78d6"),       # slot1 blue
    ("加速 (g)", "accel (g)", "#eb6834"),              # slot2 orange
    ("自動車速度 (km/h)", "speed (km/h)", "#1baf7a"),  # slot3 aqua
    ("冷却水温度 (℃)", "coolant (℃)", "#eda100"),      # slot4 yellow
]


def plot_multi_metric(df: pd.DataFrame, out_path: Path, title: str) -> None:
    metrics = [m for m in METRICS if m[0] in df.columns]

    fig, axes = plt.subplots(len(metrics), 1, figsize=(10, 2.2 * len(metrics)), sharex=True)
    for ax, (column, ylabel, color) in zip(axes, metrics):
        series_df = df[["time", column]].dropna(subset=[column]).copy()
        series_df["time"] = pd.to_datetime(series_df["time"], format="%H:%M:%S.%f")
        plot_df = break_on_gaps(series_df["time"], series_df[column])

        ax.plot(plot_df["time"], plot_df["value"], color=color, linewidth=2, solid_capstyle="round")
        ax.set_ylabel(ylabel)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    axes[-1].set_xlabel("time")
    fig.suptitle(title)
    fig.autofmt_xdate()
    fig.tight_layout()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)


def main() -> None:
    csv_path = Path(sys.argv[1])
    df = load_obd_log(csv_path)

    now = datetime.now()
    out_dir = Path("output") / now.strftime("%Y-%m-%d")
    out_path = out_dir / f"multi_metric_{csv_path.stem}_{now.strftime('%H%M')}.png"
    plot_multi_metric(df, out_path, title=csv_path.stem)

    print(f"出力: {out_path}")


if __name__ == "__main__":
    main()
