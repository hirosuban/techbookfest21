"""
OBD2ログの時系列プロットで、ログが途切れた区間を折れ線で繋いでしまわないための
共通ユーティリティ。

Car Scannerのログは、Bluetooth切断やアプリの一時停止などで記録そのものが数十秒〜
数十分単位で途切れることがある（詳細はlogs/2026-10-15.md参照）。単純にdropna()した
値をそのままプロットすると、途切れる前後の点が1本の直線で結ばれ、あたかも連続的に
変化したかのような誤った見た目になる。本モジュールは、時刻の間隔が閾値を超えた箇所に
NaNの点を1つ挿入することで、matplotlibがその区間の線を描かないようにする。
"""
import pandas as pd

GAP_THRESHOLD_SEC = 5.0  # 通常のPIDポーリング間隔(どのログでも1.3秒以内)より十分大きい値


def break_on_gaps(time: pd.Series, value: pd.Series, threshold_sec: float = GAP_THRESHOLD_SEC) -> pd.DataFrame:
    df = pd.DataFrame({"time": time, "value": value}).sort_values("time").reset_index(drop=True)
    gap_sec = df["time"].diff().dt.total_seconds()
    break_after = df.index[(gap_sec > threshold_sec).fillna(False)] - 1

    inserts = pd.DataFrame({
        "time": df.loc[break_after, "time"].values + pd.Timedelta(milliseconds=1),
        "value": float("nan"),
    })
    return pd.concat([df, inserts]).sort_values("time").reset_index(drop=True)
