"""
PoC: 車体シルエットのルーフライン(上端の曲線)をフーリエ級数(sin/cos)で近似するスクリプト試作。

やっていること:
    1. golden_ratio_poc.py の車体セグメンテーション(GrabCut / DeepLabV3)を再利用してマスクを取得
    2. 外接矩形内で列(x)ごとに一番上の前景画素を拾い、ルーフライン y(x) を作る
       (閉曲線のままだとx方向に1対1対応しないためFFTにかけられない。
        ルーフラインだけ切り出すことで y=f(x) の形にし、素直に1次元FFTを適用できるようにしている)
    3. numpy.fft.rfft で周波数成分に分解し、低次からN項だけ残して再構成(irfft)する
    4. 元の曲線と再構成曲線、パワースペクトラムを重ねて可視化する

使い方:
    python scripts/roofline_fourier_poc.py images/3.jpeg
    python scripts/roofline_fourier_poc.py images/3.jpeg grabcut 1,3,5,10,20
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

DEFAULT_HARMONICS = (1, 3, 5, 10, 20)


def extract_roofline(mask: np.ndarray, bbox: tuple[int, int, int, int]) -> np.ndarray:
    """外接矩形内で列(x)ごとに一番上(yが最小)の前景画素を拾い、ルーフライン y(x) を返す。"""
    x, y, w, h = bbox
    region = mask[y : y + h, x : x + w]

    roofline = np.full(w, np.nan)
    for col in range(w):
        rows = np.nonzero(region[:, col])[0]
        if rows.size > 0:
            roofline[col] = rows[0]

    valid = ~np.isnan(roofline)
    if valid.sum() < 2:
        raise RuntimeError("ルーフラインを十分に抽出できませんでした")
    # マスクが途切れて前景画素が無い列は、前後の値から線形補間して埋める
    roofline = np.interp(np.arange(w), np.flatnonzero(valid), roofline[valid])
    return roofline


def reconstruct_with_harmonics(signal: np.ndarray, n_harmonics: int) -> np.ndarray:
    """rfftで信号を変換し、直流成分+低次n_harmonics項だけ残してirfftで再構成する。"""
    spectrum = np.fft.rfft(signal)
    truncated = np.zeros_like(spectrum)
    keep = min(n_harmonics + 1, spectrum.size)  # +1は直流(0次)成分の分
    truncated[:keep] = spectrum[:keep]
    return np.fft.irfft(truncated, n=signal.size)


def main() -> None:
    if len(sys.argv) not in (2, 3, 4):
        print("Usage: python scripts/roofline_fourier_poc.py <image_path> [grabcut|dl] [harmonics_csv]")
        sys.exit(1)

    src_path = Path(sys.argv[1])
    method = sys.argv[2] if len(sys.argv) >= 3 else "dl"
    if method not in ("grabcut", "dl"):
        print(f"未対応のmethodです: {method} (grabcut または dl を指定してください)")
        sys.exit(1)
    harmonics_csv = sys.argv[3] if len(sys.argv) == 4 else ",".join(str(n) for n in DEFAULT_HARMONICS)
    harmonics = [int(n) for n in harmonics_csv.split(",")]

    img = cv2.imread(str(src_path))
    if img is None:
        raise FileNotFoundError(f"画像を読み込めませんでした: {src_path}")

    car_mask = segment_car_dl(img) if method == "dl" else segment_car_grabcut(img)
    bbox = largest_contour_bbox(car_mask)
    roofline = extract_roofline(car_mask, bbox)
    bbox_x, bbox_y, bbox_w, _ = bbox
    xs = bbox_x + np.arange(bbox_w)

    spectrum = np.fft.rfft(roofline - roofline.mean())
    power = np.abs(spectrum) ** 2
    total_energy = power.sum()

    # 元画像の上に、抽出したルーフラインと再構成曲線をそのまま重ねて描く
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    outline = [pe.Stroke(linewidth=5, foreground="black"), pe.Normal()]  # 車体の色に埋もれないよう黒縁取りを付ける

    # 項数ごとに別パネルに分ける(1枚に全項数を重ねると線が重なって見分けづらいため)
    ncols = min(len(harmonics), 3)
    nrows_curves = -(-len(harmonics) // ncols)  # 切り上げ除算
    fig = plt.figure(figsize=(5 * ncols, 4 * nrows_curves + 4))
    gs = fig.add_gridspec(nrows_curves + 1, ncols, height_ratios=[3] * nrows_curves + [2])

    for i, n in enumerate(harmonics):
        row, col = divmod(i, ncols)
        ax = fig.add_subplot(gs[row, col])
        ax.imshow(rgb_img)
        ax.plot(
            xs, bbox_y + roofline, color="yellow", linestyle="--", linewidth=2,
            path_effects=outline, label="original", zorder=5,
        )
        recon = reconstruct_with_harmonics(roofline, n)
        ax.plot(xs, bbox_y + recon, color="red", linewidth=2, path_effects=outline, label=f"{n} harmonics")
        ax.set_title(f"{n} harmonics")
        ax.axis("off")
        ax.legend(fontsize=7, loc="upper right", framealpha=0.9)

    ax_spectrum = fig.add_subplot(gs[nrows_curves, :])
    ax_spectrum.plot(power, color="black")
    ax_spectrum.set_yscale("log")
    ax_spectrum.set_title("power spectrum (energy per harmonic)")
    ax_spectrum.set_xlabel("harmonic index")
    ax_spectrum.set_ylabel("|coefficient|^2 (log)")

    fig.suptitle(f"{src_path.name} ({method}): roofline Fourier approximation")
    fig.tight_layout()

    now = datetime.now()
    # logs/YYYY-MM-DD.md と対応付けられるよう、出力先も日付ごとのディレクトリに分ける
    out_dir = Path("output") / now.strftime("%Y-%m-%d")
    out_dir.mkdir(parents=True, exist_ok=True)
    time_str = now.strftime("%H%M")
    out_path = out_dir / f"{src_path.stem}_{method}_roofline_fourier_{time_str}.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)

    print(f"ルーフライン点数: {len(roofline)}")
    for n in harmonics:
        recon = reconstruct_with_harmonics(roofline, n)
        rmse = np.sqrt(np.mean((roofline - recon) ** 2))
        energy_ratio = power[: n + 1].sum() / total_energy * 100
        print(f"  {n:>3}項: RMSE={rmse:6.2f}px, 累積エネルギー比={energy_ratio:5.1f}%")
    print(f"出力: {out_path}")


if __name__ == "__main__":
    main()
