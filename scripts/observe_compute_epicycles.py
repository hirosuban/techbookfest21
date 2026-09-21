"""
epicycle_poc.py の compute_epicycles() の中身を、小さい合成データで1行ずつ観察するスクリプト。
書籍のパイプラインとは無関係な、理解用のデバッグツール(単体で動く、画像を必要としない)。

合成データは n=16 点の閉曲線で、基本周波数(k=1)に4倍の"花びら"成分(k=4)を意図的に混ぜてある。
compute_epicycles() は「周波数の絶対値が小さい順」に項を選ぶため、必ずしも「振幅が大きい順」には
ならない。このスクリプトはその挙動を具体的な数値・グラフで確認するためのもの。

使い方:
    python scripts/observe_compute_epicycles.py
"""
from datetime import datetime
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from epicycle_poc import compute_epicycles  # 本物の関数をそのまま使う

# --- 合成データ: 基本周波数1 + 4倍の花びら成分を混ぜた閉曲線 ---
n = 16
t = np.linspace(0, 2 * np.pi, n, endpoint=False)
z = np.exp(1j * t) + 0.4 * np.exp(1j * 4 * t)
n_harmonics = 5

print("=" * 60)
print("入力データ")
print("=" * 60)
print(f"n = {n}")
for i, (ti, zi) in enumerate(zip(t, z)):
    print(f"  z[{i:2d}] = {zi:.3f}  (t={ti:.3f})")

print()
print("=" * 60)
print("compute_epicycles() の中身を1行ずつ実況")
print("=" * 60)

# --- 1行目: n = len(z) ---
n_ = len(z)
print("\n[1] n = len(z)")
print(f"    n = {n_}  (type={type(n_).__name__})")

# --- 2行目: coeffs = np.fft.fft(z) / n ---
coeffs_all = np.fft.fft(z) / n_
print("\n[2] coeffs = np.fft.fft(z) / n")
print(f"    shape={coeffs_all.shape}, dtype={coeffs_all.dtype}")
for i, c in enumerate(coeffs_all):
    print(f"    coeffs[{i:2d}] = {c:.3f}   |coeffs|={abs(c):.3f}")

# --- 3行目: freqs = np.fft.fftfreq(n, d=1.0/n).astype(int) ---
freqs_all = np.fft.fftfreq(n_, d=1.0 / n_).astype(int)
print("\n[3] freqs = np.fft.fftfreq(n, d=1.0/n).astype(int)")
print(f"    shape={freqs_all.shape}, dtype={freqs_all.dtype}")
print(f"    freqs = {freqs_all.tolist()}")

# --- 4行目: order = np.argsort(np.abs(freqs), kind="stable") ---
abs_freqs = np.abs(freqs_all)
order = np.argsort(abs_freqs, kind="stable")
print("\n[4] order = np.argsort(np.abs(freqs), kind='stable')")
print(f"    |freqs| = {abs_freqs.tolist()}")
print(f"    order (インデックス) = {order.tolist()}")
print("    並べ替え後のfreqsの並び(=freqs[order]):")
print(f"      {freqs_all[order].tolist()}")

# --- 5行目: keep = order[:n_harmonics] ---
keep = order[:n_harmonics]
print(f"\n[5] keep = order[:n_harmonics]  (n_harmonics={n_harmonics})")
print(f"    keep = {keep.tolist()}")
print(f"    選ばれた周波数(freqs[keep]) = {freqs_all[keep].tolist()}")

# --- 6行目: return freqs[keep], coeffs[keep] ---
freqs_kept = freqs_all[keep]
coeffs_kept = coeffs_all[keep]
print("\n[6] return freqs[keep], coeffs[keep]")
for k, c in zip(freqs_kept, coeffs_kept):
    print(f"    freq={k:+2d}  coeff={c:.3f}  |coeff|={abs(c):.3f}")

# --- 本物の compute_epicycles() と結果が一致するか確認 ---
print()
print("=" * 60)
print("本物の compute_epicycles() との一致確認")
print("=" * 60)
real_freqs, real_coeffs = compute_epicycles(z, n_harmonics)
np.testing.assert_array_equal(real_freqs, freqs_kept)
np.testing.assert_array_almost_equal(real_coeffs, coeffs_kept)
print("一致しました。実況した内容は本物のロジックと同じです。")

now = datetime.now()
# logs/YYYY-MM-DD.md と対応付けられるよう、出力先も日付ごとのディレクトリに分ける(他スクリプトと同じ運用)
out_dir = Path(__file__).parent.parent / "output" / now.strftime("%Y-%m-%d")
out_dir.mkdir(parents=True, exist_ok=True)
time_str = now.strftime("%H%M")

# --- 可視化1: 入力データz(t)そのもの。複素平面上の形(花びら形)と、tに対する時間断面(実部/虚部) ---
fig1, (ax_shape, ax_time) = plt.subplots(1, 2, figsize=(11, 4.5))

ax_shape.plot(np.append(z.real, z.real[0]), np.append(z.imag, z.imag[0]), "o-", color="tab:blue")
for i, zi in enumerate(z):
    ax_shape.annotate(str(i), (zi.real, zi.imag), textcoords="offset points", xytext=(4, 4), fontsize=7)
ax_shape.set_title("z = x + iy (complex plane)")
ax_shape.set_xlabel("Re(z) = x")
ax_shape.set_ylabel("Im(z) = y")
ax_shape.set_aspect("equal")
ax_shape.axhline(0, color="gray", linewidth=0.5)
ax_shape.axvline(0, color="gray", linewidth=0.5)

ax_time.plot(t, z.real, "o-", label="Re(z(t)) = x(t)", color="tab:orange")
ax_time.plot(t, z.imag, "o-", label="Im(z(t)) = y(t)", color="tab:green")
ax_time.set_title("z(t) の時間断面(tに対するx, y)")
ax_time.set_xlabel("t")
ax_time.set_ylabel("value")
ax_time.legend(fontsize=8)
ax_time.axhline(0, color="gray", linewidth=0.5)

fig1.suptitle("入力データ: z(t) = exp(it) + 0.4*exp(4it)")
fig1.tight_layout()
input_path = out_dir / f"compute_epicycles_input_{time_str}.png"
fig1.savefig(input_path, dpi=150)
plt.close(fig1)
print(f"\n入力データのプロットを保存しました: {input_path}")

# --- 可視化2: 周波数を数直線上に並べ、選ばれたものを強調表示 ---
fig2, ax = plt.subplots(figsize=(9, 4))
colors = ["crimson" if i in keep else "lightgray" for i in range(n_)]
ax.bar(freqs_all, np.abs(coeffs_all), color=colors, width=0.5)
ax.set_xlabel("frequency (k)")
ax.set_ylabel("|coeff|")
ax.set_title(f"compute_epicycles(z, n_harmonics={n_harmonics}): selected frequencies (red)")
ax.axhline(0, color="black", linewidth=0.8)
for k, c in zip(freqs_all, coeffs_all):
    ax.annotate(f"k={k}", (k, abs(c)), textcoords="offset points", xytext=(0, 5),
                ha="center", fontsize=8)

freq_path = out_dir / f"compute_epicycles_observed_{time_str}.png"
fig2.tight_layout()
fig2.savefig(freq_path, dpi=150)
plt.close(fig2)
print(f"周波数プロットを保存しました: {freq_path}")
