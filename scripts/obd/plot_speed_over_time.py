"""
OBD2ログ（Car Scanner ELM OBD2のCSV）から、横軸=time・縦軸=自動車速度(km/h)の
折れ線グラフを出力するスクリプト。

Car ScannerのCSVはPIDごとに更新タイミングが違うため、1行につき値が入っている列は
ごく一部で、他は空欄になっている（疎な構造）。本スクリプトでは速度列が入っている
行だけを抜き出してプロットする。また、ログ自体が途切れた区間（Bluetooth切断等）は
gap_utils.break_on_gaps()で線を分断し、斜め線で繋いでしまわないようにしている。

使い方:
    python scripts/obd/plot_speed_over_time.py "obd_log/2026-10-04 20-34-30.csv"
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

SPEED_COLUMN = "自動車速度 (km/h)"
LINE_COLOR = "#2a78d6"  # dataviz skillのcategorical slot1(blue)


def extract_speed_over_time(df: pd.DataFrame) -> pd.DataFrame:
    speed_df = df[["time", SPEED_COLUMN]].dropna(subset=[SPEED_COLUMN]).copy()
    speed_df["time"] = pd.to_datetime(speed_df["time"], format="%H:%M:%S.%f")
    return speed_df


def plot_speed_over_time(speed_df: pd.DataFrame, out_path: Path) -> None:
    plot_df = break_on_gaps(speed_df["time"], speed_df[SPEED_COLUMN])

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(
        plot_df["time"],
        plot_df["value"],
        color=LINE_COLOR,
        linewidth=2,
        solid_capstyle="round",
    )
    ax.set_xlabel("time")
    ax.set_ylabel("speed (km/h)")
    ax.set_title("自動車速度の推移")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.autofmt_xdate()
    fig.tight_layout()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)


def main() -> None:
    csv_path = Path(sys.argv[1])
    df = load_obd_log(csv_path)
    speed_df = extract_speed_over_time(df)

    now = datetime.now()
    out_dir = Path("output") / now.strftime("%Y-%m-%d")
    out_path = out_dir / f"speed_over_time_{now.strftime('%H%M')}.png"
    plot_speed_over_time(speed_df, out_path)

    print(f"出力: {out_path} ({len(speed_df)}点)")


if __name__ == "__main__":
    main()
