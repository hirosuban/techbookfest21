"""
PoC: 車体シルエットの外接矩形と黄金比グリッドを描画するスクリプト試作。

使い方:
    python scripts/golden_ratio_poc.py images/3.jpeg
"""
import sys
from pathlib import Path

import cv2
import numpy as np

GOLDEN_RATIO = 1.618

BOX_COLOR = (0, 255, 0)       # 外接矩形（緑）
GRID_COLOR = (0, 215, 255)    # 黄金比グリッド（オレンジ寄り）
LINE_THICKNESS = 2


def segment_car(img: np.ndarray) -> np.ndarray:
    """GrabCutで背景と車体を分離し、車体部分のマスク(0/1)を返す。"""
    h, w = img.shape[:2]
    mask = np.zeros((h, w), np.uint8)

    # 画像の外周を除いた領域を「おそらく前景」として初期化する
    margin_x, margin_y = int(w * 0.05), int(h * 0.05)
    rect = (margin_x, margin_y, w - 2 * margin_x, h - 2 * margin_y)

    bgd_model = np.zeros((1, 65), np.float64)
    fgd_model = np.zeros((1, 65), np.float64)

    cv2.grabCut(img, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)

    car_mask = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 1, 0).astype("uint8")
    return car_mask


def largest_contour_bbox(mask: np.ndarray) -> tuple[int, int, int, int]:
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise RuntimeError("車体らしき輪郭が検出できませんでした")
    largest = max(contours, key=cv2.contourArea)
    return cv2.boundingRect(largest)  # x, y, w, h


def draw_golden_grid(img: np.ndarray, bbox: tuple[int, int, int, int]) -> None:
    x, y, w, h = bbox

    cv2.rectangle(img, (x, y), (x + w, y + h), BOX_COLOR, LINE_THICKNESS)

    # 短辺側からの黄金分割点（両端から1本ずつ）
    gx1 = x + int(w / GOLDEN_RATIO)
    gx2 = x + int(w - w / GOLDEN_RATIO)
    gy1 = y + int(h / GOLDEN_RATIO)
    gy2 = y + int(h - h / GOLDEN_RATIO)

    for gx in (gx1, gx2):
        cv2.line(img, (gx, y), (gx, y + h), GRID_COLOR, LINE_THICKNESS)
    for gy in (gy1, gy2):
        cv2.line(img, (x, gy), (x + w, gy), GRID_COLOR, LINE_THICKNESS)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/golden_ratio_poc.py <image_path>")
        sys.exit(1)

    src_path = Path(sys.argv[1])
    img = cv2.imread(str(src_path))
    if img is None:
        raise FileNotFoundError(f"画像を読み込めませんでした: {src_path}")

    car_mask = segment_car(img)
    x, y, w, h = largest_contour_bbox(car_mask)

    ratio = w / h
    deviation = (ratio - GOLDEN_RATIO) / GOLDEN_RATIO * 100

    annotated = img.copy()
    draw_golden_grid(annotated, (x, y, w, h))

    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{src_path.stem}_annotated.jpg"
    cv2.imwrite(str(out_path), annotated)

    print(f"外接矩形: x={x}, y={y}, w={w}, h={h}")
    print(f"幅/高さ比: {ratio:.3f} (黄金比 {GOLDEN_RATIO} との乖離: {deviation:+.1f}%)")
    print(f"出力: {out_path}")


if __name__ == "__main__":
    main()
