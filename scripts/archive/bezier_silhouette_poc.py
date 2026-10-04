"""
PoC: 3次ベジェ曲線でマツダ的「ロングノーズ&ファストバック」シルエットを生成するスクリプト試作。
実写真の解析ではなく、制御点だけから理想形のシルエットを描く生成系のお試し。

使い方:
    python scripts/archive/bezier_silhouette_poc.py
"""
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def cubic_bezier(p0, p1, p2, p3, num_points=100):
    """
    3次ベジェ曲線の座標を計算する関数
    p0: 始点, p1: 制御点1, p2: 制御点2, p3: 終点
    """
    t = np.linspace(0, 1, num_points)[:, np.newaxis]
    # ベルヌーイ基底関数による計算
    curve = (
        (1 - t)**3 * p0 +
        3 * (1 - t)**2 * t * p1 +
        3 * (1 - t) * t**2 * p2 +
        t**3 * p3
    )
    return curve


def main() -> None:
    # マツダの「ロングノーズ＆ファストバック」のシルエットを模した制御点群
    # (x, y) 座標系を想定
    # 1. ボンネットからフロントノーズにかけての曲線
    bonnet_p0 = np.array([0.0, 0.5])   # フロント先端
    bonnet_p1 = np.array([0.2, 0.48])  # ノーズの沈み込みを抑える制御点
    bonnet_p2 = np.array([0.4, 0.7])   # 緩やかに持ち上がるフェンダーへの立ち上がり
    bonnet_p3 = np.array([0.6, 1.0])   # カウルトップ（フロントウインドウ下端）

    # 2. ルーフからリアへの流れ
    roof_p0 = bonnet_p3
    roof_p1 = np.array([0.8, 1.15])  # ルーフの頂点（キャビン）
    roof_p2 = np.array([1.2, 0.9])   # リアウインドウからトランクへの傾斜
    roof_p3 = np.array([1.5, 0.4])   # リアエンド

    # 曲線の生成
    curve_bonnet = cubic_bezier(bonnet_p0, bonnet_p1, bonnet_p2, bonnet_p3)
    curve_roof = cubic_bezier(roof_p0, roof_p1, roof_p2, roof_p3)

    # 描画
    fig = plt.figure(figsize=(10, 4))
    plt.plot(curve_bonnet[:, 0], curve_bonnet[:, 1], label='Bonnet Line (Long Nose)', color='crimson', linewidth=3)
    plt.plot(curve_roof[:, 0], curve_roof[:, 1], label='Cabin & Roof Line', color='darkslategray', linewidth=3)

    # 制御点の可視化（デザインの裏側にある「骨格」を示す）
    pts_b = np.array([bonnet_p0, bonnet_p1, bonnet_p2, bonnet_p3])
    plt.scatter(pts_b[:, 0], pts_b[:, 1], color='red', zorder=5)
    plt.plot(pts_b[:, 0], pts_b[:, 1], linestyle='--', color='lightcoral', alpha=0.7)

    plt.title("Generative Car Silhouette via Bezier Curves (Mazda-esque)")
    plt.xlabel("X (Length)")
    plt.ylabel("Y (Height)")
    plt.axhline(0, color='black', linewidth=1)
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.axis('equal')

    now = datetime.now()
    # logs/YYYY-MM-DD.md と対応付けられるよう、出力先も日付ごとのディレクトリに分ける
    out_dir = Path("output") / now.strftime("%Y-%m-%d")
    out_dir.mkdir(parents=True, exist_ok=True)
    time_str = now.strftime("%H%M")
    out_path = out_dir / f"bezier_silhouette_{time_str}.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"出力: {out_path}")


if __name__ == "__main__":
    main()
