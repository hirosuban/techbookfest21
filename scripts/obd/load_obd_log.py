"""
Car Scanner ELM OBD2で出力したCSVログをpandas DataFrameとして読み込むスクリプト。

使い方:
    python scripts/obd/load_obd_log.py "obd_log/2026-10-04 20-34-30.csv"
"""
import sys
from pathlib import Path

import pandas as pd


def load_obd_log(csv_path: Path) -> pd.DataFrame:
    return pd.read_csv(csv_path)


def main() -> None:
    csv_path = Path(sys.argv[1])
    df = load_obd_log(csv_path)
    print(f"読み込めました: {csv_path} (shape={df.shape})")


if __name__ == "__main__":
    main()
