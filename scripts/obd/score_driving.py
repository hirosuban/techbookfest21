"""
OBD2ログを2つの区間（例: 街中と峠）に分け、運転の「採点」に使える指標を比べるスクリプト。

採点の指標は次の2つ。
- 急加速・急ブレーキの回数: 加速(g)が閾値を超えた回数。
- エンジン回転数の分布: 走行中(速度>0km/h)のrpmのヒストグラム。

Car Scannerの「加速 (g)」はiPhoneの加速度センサーではなく車速の変化から計算された値で、
自分で車速を微分した値との相関は0.98だった（logs/2026-10-18.md参照）。生の値は
約0.08g刻みで段々になっていてノイズが大きいため、1秒平均してから閾値と比べる。
閾値を一つに決める根拠はまだ無いので、複数の閾値（EVENT_THRESHOLDS_G）で回数を数える。
閾値を連続して超えている間は1回と数える。

区間の境目は、ユーザーの走行メモ（例: 09:55以降は峠）を--splitで渡す。ログ開始直後の
大きな欠損より前（アイドリングのみ）は対象から外す。

使い方:
    python scripts/obd/score_driving.py "obd_log/2026-10-17 09-24-07.csv" --split 09:55 \
        --labels 街中 峠
"""
import argparse
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # devcontainerはヘッドレスなのでファイル出力のみのバックエンドにする
import matplotlib.pyplot as plt
import pandas as pd

from gap_utils import find_largest_gap_midpoint
from load_obd_log import load_obd_log
from mpl_ja import set_japanese_font

set_japanese_font()

SPEED_COLUMN = "自動車速度 (km/h)"
ACCEL_COLUMN = "加速 (g)"
RPM_COLUMN = "エンジン回転数 (rpm)"

EVENT_THRESHOLDS_G = [0.10, 0.15, 0.20, 0.30]
RPM_BINS = list(range(500, 3100, 100))
SEGMENT_COLORS = ["#2a78d6", "#eb6834"]  # dataviz skillのcategorical 8色の先頭2色


def count_events(accel_1s: pd.Series, threshold: float) -> tuple[int, int]:
    """閾値を超えた区間（連続した秒）の数を、加速側・減速側それぞれ数える。"""
    def runs(mask: pd.Series) -> int:
        return int((mask & ~mask.shift(fill_value=False)).sum())

    return runs(accel_1s >= threshold), runs(accel_1s <= -threshold)


def summarize(df: pd.DataFrame) -> dict:
    accel_1s = df.set_index("time")[ACCEL_COLUMN].dropna().resample("1s").mean().dropna()
    speed = df[["time", SPEED_COLUMN]].dropna()
    moving_minutes = (speed[SPEED_COLUMN] > 0).mean() * (speed["time"].iloc[-1] - speed["time"].iloc[0]).total_seconds() / 60
    rpm_moving = df.loc[df[SPEED_COLUMN] > 0, RPM_COLUMN].dropna()

    summary = {
        "時間(分)": (df["time"].iloc[-1] - df["time"].iloc[0]).total_seconds() / 60,
        "走行中(分)": moving_minutes,
        "最大加速(g,1秒平均)": accel_1s.max(),
        "最大減速(g,1秒平均)": accel_1s.min(),
        "走行中rpm中央値": rpm_moving.median(),
        "走行中rpm 90%点": rpm_moving.quantile(0.9),
    }
    for threshold in EVENT_THRESHOLDS_G:
        accel_n, brake_n = count_events(accel_1s, threshold)
        summary[f"急加速 ≥{threshold:.2f}g"] = accel_n
        summary[f"急ブレーキ ≤-{threshold:.2f}g"] = brake_n
    return summary, rpm_moving


def plot_rpm(rpm_by_label: dict[str, pd.Series], out_path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    for (label, rpm), color in zip(rpm_by_label.items(), SEGMENT_COLORS):
        # 区間の長さが違うので、回数ではなく割合(%)で比べる
        weights = [100 / len(rpm)] * len(rpm)
        ax.hist(rpm, bins=RPM_BINS, weights=weights, histtype="step", linewidth=2, color=color,
                label=f"{label}（中央値 {rpm.median():.0f}rpm）")
    ax.set_xlabel("エンジン回転数 (rpm)")
    ax.set_ylabel("走行中の時間の割合 (%)")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False)
    ax.set_title(title)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--split", required=True, help="区間の境目の時刻 (HH:MM)")
    parser.add_argument("--labels", nargs=2, default=["前半", "後半"])
    args = parser.parse_args()

    df = load_obd_log(args.csv_path)
    df["time"] = pd.to_datetime(df["time"], format="%H:%M:%S.%f")
    df = df[df["time"] >= find_largest_gap_midpoint(df["time"])]
    split_at = pd.to_datetime(args.split, format="%H:%M")

    rpm_by_label = {}
    rows = {}
    for label, segment_df in zip(args.labels, [df[df["time"] < split_at], df[df["time"] >= split_at]]):
        rows[label], rpm_by_label[label] = summarize(segment_df)

    table = pd.DataFrame(rows)
    print(table.to_string(float_format=lambda x: f"{x:.2f}"))

    now = datetime.now()
    out_dir = Path("output") / now.strftime("%Y-%m-%d")
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"score_driving_{args.csv_path.stem}_{now.strftime('%H%M')}"
    table.to_csv(out_dir / f"{stem}.csv")
    plot_rpm(rpm_by_label, out_dir / f"{stem}_rpm.png",
             title=f"走行中のエンジン回転数の分布（{args.csv_path.stem}）")
    print(f"出力: {out_dir / stem}.csv, {out_dir / stem}_rpm.png")


if __name__ == "__main__":
    main()
