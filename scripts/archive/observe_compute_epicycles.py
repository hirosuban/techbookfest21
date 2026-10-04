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

# --- 可視化: input(形・t断面・成分分解)とoutput(周波数選択の結果)を1枚にまとめる ---
# 滑らかな曲線として見せるための密なt(FFTには使わない、表示専用)
t_dense = np.linspace(0, 2 * np.pi, 400)
term1_dense = np.exp(1j * 1 * t_dense)        # k=1成分: cos(t) + i sin(t)
term4_dense = 0.4 * np.exp(1j * 4 * t_dense)  # k=4成分: 0.4cos(4t) + i*0.4sin(4t)
z_dense = term1_dense + term4_dense

fig, axes = plt.subplots(2, 2, figsize=(12, 9))
ax_shape, ax_freq, ax_x, ax_y = axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]

# [input] 複素平面上の形(花びら形)。n=16点(実際にFFTに使うサンプル)と、参考用の滑らかな輪郭を重ねる
ax_shape.plot(z_dense.real, z_dense.imag, "-", color="lightsteelblue", linewidth=1, label="連続曲線(参考)")
ax_shape.plot(np.append(z.real, z.real[0]), np.append(z.imag, z.imag[0]), "o-", color="tab:blue",
              label="n=16点(実際の入力)")
for i, zi in enumerate(z):
    ax_shape.annotate(str(i), (zi.real, zi.imag), textcoords="offset points", xytext=(4, 4), fontsize=7)
ax_shape.set_title("[input] z = x + iy (complex plane)")
ax_shape.set_xlabel("Re(z) = x")
ax_shape.set_ylabel("Im(z) = y")
ax_shape.set_aspect("equal")
ax_shape.axhline(0, color="gray", linewidth=0.5)
ax_shape.axvline(0, color="gray", linewidth=0.5)
ax_shape.legend(fontsize=7)

# [input] x(t)の成分分解: cos(t) + 0.4*cos(4t) = x(t)
ax_x.plot(t_dense, term1_dense.real, "--", color="tab:blue", linewidth=1.3, label="cos(t)")
ax_x.plot(t_dense, term4_dense.real, "--", color="tab:purple", linewidth=1.3, label="0.4cos(4t)")
ax_x.plot(t_dense, z_dense.real, "-", color="tab:orange", linewidth=2, label="和 = x(t)")
ax_x.plot(t, z.real, "o", color="tab:orange", markersize=4)
ax_x.set_title("[input] x(t) の成分分解 (横軸t)")
ax_x.set_xlabel("t")
ax_x.set_ylabel("value")
ax_x.axhline(0, color="gray", linewidth=0.5)
ax_x.legend(fontsize=8)

# [input] y(t)の成分分解: sin(t) + 0.4*sin(4t) = y(t)
ax_y.plot(t_dense, term1_dense.imag, "--", color="tab:blue", linewidth=1.3, label="sin(t)")
ax_y.plot(t_dense, term4_dense.imag, "--", color="tab:purple", linewidth=1.3, label="0.4sin(4t)")
ax_y.plot(t_dense, z_dense.imag, "-", color="tab:green", linewidth=2, label="和 = y(t)")
ax_y.plot(t, z.imag, "o", color="tab:green", markersize=4)
ax_y.set_title("[input] y(t) の成分分解 (横軸t)")
ax_y.set_xlabel("t")
ax_y.set_ylabel("value")
ax_y.axhline(0, color="gray", linewidth=0.5)
ax_y.legend(fontsize=8)

# [output] compute_epicycles()が選んだ周波数(周波数を数直線上に並べ、選ばれたものを強調表示)
colors = ["crimson" if i in keep else "lightgray" for i in range(n_)]
ax_freq.bar(freqs_all, np.abs(coeffs_all), color=colors, width=0.5)
ax_freq.set_xlabel("frequency (k)")
ax_freq.set_ylabel("|coeff|")
ax_freq.set_title(f"[output] compute_epicycles(n_harmonics={n_harmonics}): 選ばれた周波数(赤)")
ax_freq.axhline(0, color="black", linewidth=0.8)
for k, c in zip(freqs_all, coeffs_all):
    ax_freq.annotate(f"k={k}", (k, abs(c)), textcoords="offset points", xytext=(0, 5),
                      ha="center", fontsize=8)

fig.suptitle("input: z(t) = exp(it) + 0.4*exp(4it)  /  output: compute_epicycles()の選択結果")
fig.tight_layout()
out_path = out_dir / f"compute_epicycles_observed_{time_str}.png"
fig.savefig(out_path, dpi=150)
plt.close(fig)
print(f"\nプロットを保存しました: {out_path}")
