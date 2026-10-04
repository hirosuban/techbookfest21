"""
PoC: 車体シルエットのルーフライン(上端の曲線)を検出し、元画像に重ね描きするだけのスクリプト。

フーリエ近似(roofline_fourier_poc.py)にいきなり進む前に、まず「曲線をちゃんと検出できているか」
だけを確認するための前段ステップ。ルーフライン抽出のロジックは roofline_fourier_poc.py の
extract_roofline() をそのまま再利用している。

使い方:
    python scripts/roofline_detection_poc.py images/3.jpeg
    python scripts/roofline_detection_poc.py images/3.jpeg grabcut
"""
import sys
from datetime import datetime
from pathlib import Path

import cv2
import matplotlib
import numpy as np

matplotlib.use("Agg")  # devcontainerはヘッドレスなのでファイル出力のみのバックエンドにする
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt

from golden_ratio_poc import largest_contour_bbox, segment_car_dl, segment_car_grabcut
from roofline_fourier_poc import extract_roofline


def main() -> None:
    if len(sys.argv) not in (2, 3):
        print("Usage: python scripts/roofline_detection_poc.py <image_path> [grabcut|dl]")
        sys.exit(1)

    src_path = Path(sys.argv[1])
    method = sys.argv[2] if len(sys.argv) == 3 else "dl"
    if method not in ("grabcut", "dl"):
        print(f"未対応のmethodです: {method} (grabcut または dl を指定してください)")
        sys.exit(1)

    img = cv2.imread(str(src_path))
    if img is None:
        raise FileNotFoundError(f"画像を読み込めませんでした: {src_path}")

    car_mask = segment_car_dl(img) if method == "dl" else segment_car_grabcut(img)
    bbox = largest_contour_bbox(car_mask)
    roofline = extract_roofline(car_mask, bbox)
    bbox_x, bbox_y, bbox_w, _ = bbox
    xs = bbox_x + np.arange(bbox_w)

    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    outline = [pe.Stroke(linewidth=5, foreground="black"), pe.Normal()]  # 車体の色に埋もれないよう黒縁取りを付ける

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.imshow(rgb_img)
    ax.plot(xs, bbox_y + roofline, color="yellow", linewidth=2.5, path_effects=outline, label="detected roofline")
    ax.set_title(f"{src_path.name} ({method}): detected roofline")
    ax.axis("off")
    ax.legend(fontsize=9, loc="upper right", framealpha=0.9)
    fig.tight_layout()

    now = datetime.now()
    # logs/YYYY-MM-DD.md と対応付けられるよう、出力先も日付ごとのディレクトリに分ける
    out_dir = Path("output") / now.strftime("%Y-%m-%d")
    out_dir.mkdir(parents=True, exist_ok=True)
    time_str = now.strftime("%H%M")
    out_path = out_dir / f"{src_path.stem}_{method}_roofline_detected_{time_str}.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"ルーフライン点数: {len(roofline)}")
    print(f"出力: {out_path}")


if __name__ == "__main__":
    main()
