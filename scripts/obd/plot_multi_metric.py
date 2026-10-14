"""
OBD2ログの全指標を1枚の画像に縦に並べて出力するスクリプト（横軸=timeを共有する
小さな多面グラフ）。

ログ全体で最も大きく途切れた箇所（Bluetooth切断等）を境に「欠損の前」「欠損の後」の
2つの区間に分け、それぞれ別画像として出力する。指標ごとに単位もスケールも異なるため、
1つのグラフに重ねず(2軸グラフは作らない)、パネルを縦に分けて横軸(time)だけ共有する
構成にしている。区間内に残る小さなログの途切れはgap_utils.break_on_gaps()で線を
分断する。

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

from gap_utils import break_on_gaps, find_largest_gap_midpoint
from load_obd_log import load_obd_log
from mpl_ja import set_japanese_font

set_japanese_font()

# dataviz skillのcategorical 8色(固定順)。指標ごとの識別用で、パネル数が8を超えたら
# 順に繰り返す(パネル同士を比較するための凡例ではないので、使い回しても識別の破綻は無い)。
CATEGORICAL_COLORS = [
    "#2a78d6",  # blue
    "#eb6834",  # orange
    "#1baf7a",  # aqua
    "#eda100",  # yellow
    "#e87ba4",  # magenta
    "#008300",  # green
    "#4a3aa7",  # violet
    "#e34948",  # red
]


def metric_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c != "time" and not c.startswith("Unnamed")]


def plot_segment(df: pd.DataFrame, columns: list[str], out_path: Path, title: str) -> None:
    fig, axes = plt.subplots(len(columns), 1, figsize=(10, 1.1 * len(columns)), sharex=True)
    for i, column in enumerate(columns):
        ax = axes[i]
        color = CATEGORICAL_COLORS[i % len(CATEGORICAL_COLORS)]

        series_df = df[["time", column]].dropna(subset=[column])
        if series_df.empty:
            ax.set_yticks([])
        else:
            plot_df = break_on_gaps(series_df["time"], series_df[column])
            ax.plot(plot_df["time"], plot_df["value"], color=color, linewidth=1.5, solid_capstyle="round")

        ax.set_ylabel(column, fontsize=7, rotation=0, ha="right", va="center")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="y", labelsize=6)

    axes[-1].set_xlabel("time")
    fig.suptitle(title)
    fig.autofmt_xdate()
    fig.tight_layout()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main() -> None:
    csv_path = Path(sys.argv[1])
    df = load_obd_log(csv_path)
    df["time"] = pd.to_datetime(df["time"], format="%H:%M:%S.%f")

    columns = metric_columns(df)
    split_at = find_largest_gap_midpoint(df["time"])
    before_df = df[df["time"] < split_at]
    after_df = df[df["time"] >= split_at]

    now = datetime.now()
    out_dir = Path("output") / now.strftime("%Y-%m-%d")

    for label, segment_df in [("before_gap", before_df), ("after_gap", after_df)]:
        out_path = out_dir / f"multi_metric_{csv_path.stem}_{label}_{now.strftime('%H%M')}.png"
        plot_segment(segment_df, columns, out_path, title=f"{csv_path.stem} ({label})")
        print(f"出力: {out_path} ({len(segment_df)}行)")


if __name__ == "__main__":
    main()
