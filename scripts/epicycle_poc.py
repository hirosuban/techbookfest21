"""
PoC: 車体シルエット全体(閉じた輪郭)を複素フーリエ級数(エピサイクル)で近似し、
回転する歯車(エピサイクル)が曲線を一筆書きしていくアニメーションを作るスクリプト。

roofline_fourier_poc.py はルーフライン(輪郭の上端)を y=f(x) の1価関数として扱っていたが、
車体全体のシルエットは同じxに対してyが複数ある閉曲線なので、その方法では扱えない。
代わりに輪郭上の各点を複素数 z(t) = x(t) + i*y(t) とみなし、複素フーリエ変換(np.fft.fft)で
分解する。各周波数kの項は「半径|c_k|・角速度kで回る歯車」に対応し、これらを鎖状につなげて
足し合わせると、先端が元の輪郭をなぞる(3Blue1Brownの"Fourier series"動画でおなじみの)
エピサイクル描画になる。

やっていること:
    1. golden_ratio_poc.py の車体セグメンテーションで前景マスクを取得
    2. マスクの外周輪郭(cv2.findContours)を弧長に沿って等間隔にM点へ再サンプリングし、
       複素数列 z = x + i*y を作る
    3. np.fft.fft(z) で複素フーリエ係数を求め、周波数の絶対値が小さい順
       (0, 1, -1, 2, -2, ...)にn_harmonics個だけ残す
    4. 各項を鎖状につないだ歯車(円)として、時刻tごとの位置をアニメーションさせ、
       先端が描いた軌跡を元画像に重ねてGIFとして保存する

使い方:
    python scripts/epicycle_poc.py images/13.jpeg
    python scripts/epicycle_poc.py images/13.jpeg dl 50 180
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
from matplotlib.animation import FuncAnimation, PillowWriter

from golden_ratio_poc import largest_contour, segment_car_dl, segment_car_grabcut

N_SAMPLES = 480  # 輪郭を弧長方向に何点へ再サンプリングするか
DEFAULT_N_HARMONICS = 50  # 使う歯車(円)の数
DEFAULT_N_FRAMES = 180  # アニメーションのコマ数(1周分)
MAX_BACKDROP_WIDTH = 900  # アニメ背景の最大幅(px)。元画像は4000px超あるため軽量化のため縮小する
FPS = 30


def resample_contour(contour: np.ndarray, n_points: int) -> np.ndarray:
    """輪郭点列(N,1,2)を弧長に沿ってn_points個の等間隔点に再サンプリングし、複素数列(x+iy)で返す。"""
    pts = contour.reshape(-1, 2).astype(np.float64)
    pts = np.vstack([pts, pts[0]])  # 閉曲線として始点-終点間の辺も弧長に含める
    deltas = np.diff(pts, axis=0)
    seg_lengths = np.hypot(deltas[:, 0], deltas[:, 1])
    arc_length = np.concatenate([[0.0], np.cumsum(seg_lengths)])
    total_length = arc_length[-1]

    sample_positions = np.linspace(0, total_length, n_points, endpoint=False)
    x = np.interp(sample_positions, arc_length, pts[:, 0])
    y = np.interp(sample_positions, arc_length, pts[:, 1])
    return x + 1j * y


def compute_epicycles(z: np.ndarray, n_harmonics: int) -> tuple[np.ndarray, np.ndarray]:
    """複素フーリエ係数を求め、周波数の絶対値が小さい順(0,1,-1,2,-2,...)にn_harmonics個返す。"""
    n = len(z)
    coeffs = np.fft.fft(z) / n
    freqs = np.fft.fftfreq(n, d=1.0 / n).astype(int)
    order = np.argsort(np.abs(freqs), kind="stable")  # 0,1,-1,2,-2,... の順に並ぶ
    keep = order[:n_harmonics]
    return freqs[keep], coeffs[keep]


def reconstruct(freqs: np.ndarray, coeffs: np.ndarray, t: np.ndarray) -> np.ndarray:
    """時刻t(配列可)における再構成後の点 z(t) を返す。"""
    # t: (T,), freqs/coeffs: (K,) -> (T, K)の外積を作って足し合わせる
    phase = np.outer(t, freqs)
    return (coeffs[np.newaxis, :] * np.exp(1j * phase)).sum(axis=1)


def main() -> None:
    if len(sys.argv) not in (2, 3, 4, 5):
        print("Usage: python scripts/epicycle_poc.py <image_path> [grabcut|dl] [n_harmonics] [n_frames]")
        sys.exit(1)

    src_path = Path(sys.argv[1])
    method = sys.argv[2] if len(sys.argv) >= 3 else "dl"
    if method not in ("grabcut", "dl"):
        print(f"未対応のmethodです: {method} (grabcut または dl を指定してください)")
        sys.exit(1)
    n_harmonics = int(sys.argv[3]) if len(sys.argv) >= 4 else DEFAULT_N_HARMONICS
    n_frames = int(sys.argv[4]) if len(sys.argv) == 5 else DEFAULT_N_FRAMES

    img = cv2.imread(str(src_path))
    if img is None:
        raise FileNotFoundError(f"画像を読み込めませんでした: {src_path}")

    car_mask = segment_car_dl(img) if method == "dl" else segment_car_grabcut(img)
    contour = largest_contour(car_mask)

    # アニメ背景は縮小して軽量化する(縮小率をそのまま輪郭座標にも掛けて整合を取る)
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    scale = min(1.0, MAX_BACKDROP_WIDTH / rgb_img.shape[1])
    if scale < 1.0:
        new_size = (int(rgb_img.shape[1] * scale), int(rgb_img.shape[0] * scale))
        rgb_img = cv2.resize(rgb_img, new_size, interpolation=cv2.INTER_AREA)
    contour_scaled = contour.astype(np.float64) * scale

    z = resample_contour(contour_scaled, N_SAMPLES)
    freqs, coeffs = compute_epicycles(z, n_harmonics)

    # n_harmonics個の歯車でどれだけ元の輪郭に近づけているかをRMSEで確認する
    t_samples = np.linspace(0, 2 * np.pi, N_SAMPLES, endpoint=False)
    recon_samples = reconstruct(freqs, coeffs, t_samples)
    rmse = np.sqrt(np.mean(np.abs(z - recon_samples) ** 2)) / scale  # 元画像のpxスケールに戻す

    fig, ax = plt.subplots(figsize=(8, 8 * rgb_img.shape[0] / rgb_img.shape[1]))
    ax.imshow(rgb_img)
    ax.axis("off")
    ax.set_title(f"{src_path.name} ({method}): epicycles (n={n_harmonics})")

    outline = [pe.Stroke(linewidth=4, foreground="black"), pe.Normal()]  # 車体の色に埋もれないよう黒縁取り
    orig_x = np.append(z.real, z.real[0])
    orig_y = np.append(z.imag, z.imag[0])
    ax.plot(orig_x, orig_y, color="yellow", linestyle="--", linewidth=1.3, alpha=0.7,
             path_effects=outline, zorder=2, label="original contour")

    circles = [
        plt.Circle((0, 0), 0, fill=False, edgecolor="deepskyblue", linewidth=0.8, alpha=0.6)
        for _ in range(n_harmonics)
    ]
    for circle in circles:
        ax.add_patch(circle)
    (arm_line,) = ax.plot([], [], color="deepskyblue", linewidth=1.0, alpha=0.9, zorder=4)
    (trail_line,) = ax.plot([], [], color="red", linewidth=2.5, path_effects=outline, zorder=5)
    (tip_dot,) = ax.plot([], [], marker="o", color="red", markersize=5, zorder=6)
    ax.legend(fontsize=8, loc="upper right", framealpha=0.9)

    trail_x: list[float] = []
    trail_y: list[float] = []
    radii = np.abs(coeffs)

    def update(frame: int):
        t = 2 * np.pi * frame / n_frames
        vectors = coeffs * np.exp(1j * freqs * t)
        positions = np.cumsum(vectors)
        centers = np.concatenate([[0j], positions[:-1]])

        for circle, center, r in zip(circles, centers, radii):
            circle.center = (center.real, center.imag)
            circle.set_radius(r)

        arm_x = np.append(centers.real, positions[-1].real)
        arm_y = np.append(centers.imag, positions[-1].imag)
        arm_line.set_data(arm_x, arm_y)

        tip = positions[-1]
        trail_x.append(tip.real)
        trail_y.append(tip.imag)
        trail_line.set_data(trail_x, trail_y)
        tip_dot.set_data([tip.real], [tip.imag])

        return [*circles, arm_line, trail_line, tip_dot]

    anim = FuncAnimation(fig, update, frames=n_frames, blit=False)

    now = datetime.now()
    # logs/YYYY-MM-DD.md と対応付けられるよう、出力先も日付ごとのディレクトリに分ける
    out_dir = Path("output") / now.strftime("%Y-%m-%d")
    out_dir.mkdir(parents=True, exist_ok=True)
    time_str = now.strftime("%H%M")
    out_path = out_dir / f"{src_path.stem}_{method}_epicycle_{time_str}.gif"
    anim.save(out_path, writer=PillowWriter(fps=FPS))
    plt.close(fig)

    print(f"輪郭点数(元): {len(contour)}, 再サンプリング後: {N_SAMPLES}")
    print(f"歯車の数: {n_harmonics}, フレーム数: {n_frames}")
    print(f"再構成RMSE: {rmse:.2f}px")
    print(f"出力: {out_path}")


if __name__ == "__main__":
    main()
