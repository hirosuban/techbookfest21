"""
observe_compute_epicycles.py の派生実験: xとyの位相をずらした入力を与えると、
負の周波数(k=-1)の係数がどう変わるかを観察するスクリプト。

通常(observe_compute_epicycles.pyの例)は z(t) = e^(it) なので x=cos(t), y=sin(t) が
"同じ角度tで揃って"回っており、複素フーリエ変換すると k=+1 の項だけで説明できる(k=-1は0)。

ここでは y だけ90度位相をずらす: x(t)=cos(t), y(t)=sin(t+90°)=cos(t)。
xとyが同じ関数になり、z(t)は円運動ではなく「右上⇄左下」の直線往復になる。
これは cos(t) = (e^(it) + e^(-it)) / 2 の教科書通りの形なので、
k=+1 と k=-1 の係数が同じ大きさで両方出てくるはず、という予想を確認する。

使い方:
    python scripts/observe_compute_epicycles_phase_shift.py
"""
from datetime import datetime
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from epicycle_poc import compute_epicycles  # 本物の関数をそのまま使う

# --- 合成データ: yの位相を90度(pi/2)ずらす。x(t)=cos(t), y(t)=sin(t+pi/2)=cos(t) ---
n = 16
t = np.linspace(0, 2 * np.pi, n, endpoint=False)
phase_shift = np.pi / 2
z = np.cos(t) + 1j * np.sin(t + phase_shift)
n_harmonics = 5

print("=" * 60)
print(f"入力データ (yの位相を{np.degrees(phase_shift):.0f}度ずらした版)")
print("=" * 60)
print("x(t) = cos(t),  y(t) = sin(t + 90°) = cos(t)")
for i, (ti, zi) in enumerate(zip(t, z)):
    print(f"  z[{i:2d}] = {zi:.3f}  (t={ti:.3f})")

n_ = len(z)
coeffs_all = np.fft.fft(z) / n_
freqs_all = np.fft.fftfreq(n_, d=1.0 / n_).astype(int)
order = np.argsort(np.abs(freqs_all), kind="stable")
keep = order[:n_harmonics]
freqs_kept = freqs_all[keep]
coeffs_kept = coeffs_all[keep]

print()
print("=" * 60)
print(f"上位{n_harmonics}項の係数 (freq, coeff, |coeff|)")
print("=" * 60)
for k, c in zip(freqs_kept, coeffs_kept):
    print(f"  freq={k:+2d}  coeff={c:.3f}  |coeff|={abs(c):.3f}")

real_freqs, real_coeffs = compute_epicycles(z, n_harmonics)
np.testing.assert_array_equal(real_freqs, freqs_kept)
np.testing.assert_array_almost_equal(real_coeffs, coeffs_kept)
print("\n(本物のcompute_epicycles()と一致確認OK)")

# 比較用: 位相ずらし無し(元の例, k=1成分のみ)の係数も並べて見せる
z_original = np.exp(1j * t)
coeffs_original = np.fft.fft(z_original) / n_
print()
print("=" * 60)
print("比較: 位相ずらし無し(x=cos(t), y=sin(t))の場合の k=+1, k=-1")
print("=" * 60)
idx_plus1 = np.where(freqs_all == 1)[0][0]
idx_minus1 = np.where(freqs_all == -1)[0][0]
print(f"  freq=+1  coeff={coeffs_original[idx_plus1]:.3f}  |coeff|={abs(coeffs_original[idx_plus1]):.3f}")
print(f"  freq=-1  coeff={coeffs_original[idx_minus1]:.3f}  |coeff|={abs(coeffs_original[idx_minus1]):.3f}")
print()
print("--- 今回(位相ずらしあり)の k=+1, k=-1 ---")
print(f"  freq=+1  coeff={coeffs_all[idx_plus1]:.3f}  |coeff|={abs(coeffs_all[idx_plus1]):.3f}")
print(f"  freq=-1  coeff={coeffs_all[idx_minus1]:.3f}  |coeff|={abs(coeffs_all[idx_minus1]):.3f}")

# --- 可視化 ---
t_dense = np.linspace(0, 2 * np.pi, 400)
z_dense = np.cos(t_dense) + 1j * np.sin(t_dense + phase_shift)
term_plus1_dense = coeffs_all[idx_plus1] * np.exp(1j * 1 * t_dense)
term_minus1_dense = coeffs_all[idx_minus1] * np.exp(1j * -1 * t_dense)
sum_dense = term_plus1_dense + term_minus1_dense  # k=+-1だけの和(他は無視できるほど小さい)

fig, axes = plt.subplots(2, 2, figsize=(12, 9))
ax_shape, ax_freq, ax_x, ax_y = axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]

ax_shape.plot(z_dense.real, z_dense.imag, "-", color="lightsteelblue", linewidth=1, label="連続曲線(参考)")
ax_shape.plot(np.append(z.real, z.real[0]), np.append(z.imag, z.imag[0]), "o-", color="tab:blue",
              label="n=16点(実際の入力)")
for i, zi in enumerate(z):
    ax_shape.annotate(str(i), (zi.real, zi.imag), textcoords="offset points", xytext=(4, 4), fontsize=7)
ax_shape.set_title("[input] z = x + iy (円ではなく直線往復になる)")
ax_shape.set_xlabel("Re(z) = x")
ax_shape.set_ylabel("Im(z) = y")
ax_shape.set_aspect("equal")
ax_shape.axhline(0, color="gray", linewidth=0.5)
ax_shape.axvline(0, color="gray", linewidth=0.5)
ax_shape.legend(fontsize=7)

ax_x.plot(t_dense, term_plus1_dense.real, "--", color="tab:blue", linewidth=1.3,
          label=f"k=+1成分 (coeff={coeffs_all[idx_plus1]:.2f})")
ax_x.plot(t_dense, term_minus1_dense.real, "--", color="tab:red", linewidth=1.3,
          label=f"k=-1成分 (coeff={coeffs_all[idx_minus1]:.2f})")
ax_x.plot(t_dense, sum_dense.real, "-", color="tab:orange", linewidth=2, label="和 ≈ x(t)")
ax_x.plot(t, z.real, "o", color="tab:orange", markersize=4)
ax_x.set_title("[input] x(t) の成分分解 (k=+1とk=-1の和)")
ax_x.set_xlabel("t")
ax_x.set_ylabel("value")
ax_x.axhline(0, color="gray", linewidth=0.5)
ax_x.legend(fontsize=8)

ax_y.plot(t_dense, term_plus1_dense.imag, "--", color="tab:blue", linewidth=1.3,
          label=f"k=+1成分 (coeff={coeffs_all[idx_plus1]:.2f})")
ax_y.plot(t_dense, term_minus1_dense.imag, "--", color="tab:red", linewidth=1.3,
          label=f"k=-1成分 (coeff={coeffs_all[idx_minus1]:.2f})")
ax_y.plot(t_dense, sum_dense.imag, "-", color="tab:green", linewidth=2, label="和 ≈ y(t)")
ax_y.plot(t, z.imag, "o", color="tab:green", markersize=4)
ax_y.set_title("[input] y(t) の成分分解 (k=+1とk=-1の和)")
ax_y.set_xlabel("t")
ax_y.set_ylabel("value")
ax_y.axhline(0, color="gray", linewidth=0.5)
ax_y.legend(fontsize=8)

colors = ["crimson" if i in keep else "lightgray" for i in range(n_)]
ax_freq.bar(freqs_all, np.abs(coeffs_all), color=colors, width=0.5)
ax_freq.set_xlabel("frequency (k)")
ax_freq.set_ylabel("|coeff|")
ax_freq.set_title(f"[output] compute_epicycles(n_harmonics={n_harmonics}): k=+1とk=-1が同じ大きさに")
ax_freq.axhline(0, color="black", linewidth=0.8)
for k, c in zip(freqs_all, coeffs_all):
    ax_freq.annotate(f"k={k}", (k, abs(c)), textcoords="offset points", xytext=(0, 5),
                      ha="center", fontsize=8)

fig.suptitle("位相ずらし版: x(t)=cos(t), y(t)=sin(t+90°)=cos(t)  →  円が直線に潰れる")
fig.tight_layout()

now = datetime.now()
out_dir = Path(__file__).parent.parent / "output" / now.strftime("%Y-%m-%d")
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / f"compute_epicycles_phase_shift_{now.strftime('%H%M')}.png"
fig.savefig(out_path, dpi=150)
plt.close(fig)
print(f"\nプロットを保存しました: {out_path}")
