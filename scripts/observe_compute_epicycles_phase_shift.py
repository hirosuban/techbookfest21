"""
observe_compute_epicycles.py の派生実験: 元の入力(z = e^(it) + 0.4*e^(4it), つまり
x(t)=cos(t)+0.4cos(4t), y(t)=sin(t)+0.4sin(4t))の周波数・振幅はそのままに、
y(t)の位相だけをずらすと、負の周波数(k=-1, k=-4)の係数がどう変わるかを観察する。

x(t)は完全に元のまま、y(t)だけ各項の角度にphase_shiftを足す
(y(t) = sin(t+shift) + 0.4*sin(4t+shift))。周波数(1と4)・振幅(1と0.4)は
一切変えていない。

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

# --- 合成データ: 元の例(k=1, k=4)そのままに、yの位相だけをずらす ---
n = 16
t = np.linspace(0, 2 * np.pi, n, endpoint=False)
phase_shift = np.pi / 2

x = np.cos(t) + 0.4 * np.cos(4 * t)                          # xは元のまま(周波数1と4、振幅1と0.4)
y = np.sin(t + phase_shift) + 0.4 * np.sin(4 * t + phase_shift)  # yだけ各項の位相をずらす
z = x + 1j * y
n_harmonics = 9  # k=0,±1,±2,±3,±4まで見えるようにする(元のn_harmonics=5だとk=±4が入らないため)

print("=" * 60)
print(f"入力データ (yの位相を{np.degrees(phase_shift):.0f}度ずらした版、周波数・振幅は元のまま)")
print("=" * 60)
print("x(t) = cos(t) + 0.4cos(4t)                (元のまま)")
print("y(t) = sin(t+90°) + 0.4sin(4t+90°)         (位相だけ+90°)")
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

# 比較用: 位相ずらし無し(元の例)の係数
z_original = np.exp(1j * t) + 0.4 * np.exp(1j * 4 * t)
coeffs_original = np.fft.fft(z_original) / n_

print()
print("=" * 60)
print("比較: 位相ずらし無し(元の例) vs 位相ずらしあり(今回)")
print("=" * 60)
for k_target in (1, -1, 4, -4):
    idx = np.where(freqs_all == k_target)[0][0]
    c_orig = coeffs_original[idx]
    c_new = coeffs_all[idx]
    print(f"  k={k_target:+2d}:  元={c_orig:.3f} (|c|={abs(c_orig):.3f})   "
          f"位相ずらし後={c_new:.3f} (|c|={abs(c_new):.3f})")

print()
print("→ 個々の|coeff|(+k側の振幅)はむしろ減っている(1.000→0.707, 0.400→0.283)。")
print("  ただし +k と -k を合わせたエネルギー(|coeff|の2乗の和)は保存されている:")
for k_target in (1, 4):
    idx_plus = np.where(freqs_all == k_target)[0][0]
    idx_minus = np.where(freqs_all == -k_target)[0][0]
    energy_orig = abs(coeffs_original[idx_plus]) ** 2 + abs(coeffs_original[idx_minus]) ** 2
    energy_new = abs(coeffs_all[idx_plus]) ** 2 + abs(coeffs_all[idx_minus]) ** 2
    print(f"    |k|={k_target}: 元のエネルギー={energy_orig:.3f}  位相ずらし後のエネルギー={energy_new:.3f}")
print("  つまり位相ずらしは、+kと-kの間でエネルギーを配分し直しているだけで、")
print("  ±kペア全体の強さ(=その周波数がどれだけ形に効いているか)は変えていない。")

# --- 可視化 ---
t_dense = np.linspace(0, 2 * np.pi, 400)
x_dense = np.cos(t_dense) + 0.4 * np.cos(4 * t_dense)
y_dense = np.sin(t_dense + phase_shift) + 0.4 * np.sin(4 * t_dense + phase_shift)
z_dense = x_dense + 1j * y_dense

# 表示用に、選ばれた項(keep)それぞれのReal/Imag成分を密なtで計算しておく
component_terms_dense = [coeffs_all[i] * np.exp(1j * freqs_all[i] * t_dense) for i in keep]
sum_dense = sum(component_terms_dense)

fig, axes = plt.subplots(2, 2, figsize=(13, 9.5))
ax_shape, ax_freq, ax_x, ax_y = axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]

ax_shape.plot(z_dense.real, z_dense.imag, "-", color="lightsteelblue", linewidth=1, label="連続曲線(参考)")
ax_shape.plot(np.append(z.real, z.real[0]), np.append(z.imag, z.imag[0]), "o-", color="tab:blue",
              label="n=16点(実際の入力)")
for i, zi in enumerate(z):
    ax_shape.annotate(str(i), (zi.real, zi.imag), textcoords="offset points", xytext=(4, 4), fontsize=7)
ax_shape.set_title("[input] z = x + iy (yの位相だけ+90°)")
ax_shape.set_xlabel("Re(z) = x")
ax_shape.set_ylabel("Im(z) = y")
ax_shape.set_aspect("equal")
ax_shape.axhline(0, color="gray", linewidth=0.5)
ax_shape.axvline(0, color="gray", linewidth=0.5)
ax_shape.legend(fontsize=7)

colors_line = ["tab:blue", "tab:red", "tab:purple", "tab:brown", "gray", "gray", "gray", "gray", "gray"]
for (k, term_dense), color in zip(zip(freqs_kept, component_terms_dense), colors_line):
    if abs(coeffs_all[np.where(freqs_all == k)[0][0]]) < 1e-6:
        continue  # ほぼ0の成分(k=0, ±2, ±3)は凡例が煩雑になるので省略
    ax_x.plot(t_dense, term_dense.real, "--", linewidth=1.2, color=color, label=f"k={k:+d}成分")
    ax_y.plot(t_dense, term_dense.imag, "--", linewidth=1.2, color=color, label=f"k={k:+d}成分")

ax_x.plot(t_dense, sum_dense.real, "-", color="tab:orange", linewidth=2, label="和 ≈ x(t)")
ax_x.plot(t, z.real, "o", color="tab:orange", markersize=4)
ax_x.set_title("[input] x(t) の成分分解 (横軸t)")
ax_x.set_xlabel("t")
ax_x.set_ylabel("value")
ax_x.axhline(0, color="gray", linewidth=0.5)
ax_x.legend(fontsize=7)

ax_y.plot(t_dense, sum_dense.imag, "-", color="tab:green", linewidth=2, label="和 ≈ y(t)")
ax_y.plot(t, z.imag, "o", color="tab:green", markersize=4)
ax_y.set_title("[input] y(t) の成分分解 (横軸t)")
ax_y.set_xlabel("t")
ax_y.set_ylabel("value")
ax_y.axhline(0, color="gray", linewidth=0.5)
ax_y.legend(fontsize=7)

bar_colors = ["crimson" if i in keep else "lightgray" for i in range(n_)]
ax_freq.bar(freqs_all, np.abs(coeffs_all), color=bar_colors, width=0.5)
ax_freq.set_xlabel("frequency (k)")
ax_freq.set_ylabel("|coeff|")
ax_freq.set_title(f"[output] compute_epicycles(n_harmonics={n_harmonics}): 負の周波数にも係数が乗る")
ax_freq.axhline(0, color="black", linewidth=0.8)
for k, c in zip(freqs_all, coeffs_all):
    ax_freq.annotate(f"k={k}", (k, abs(c)), textcoords="offset points", xytext=(0, 5),
                      ha="center", fontsize=8)

fig.suptitle("位相ずらし版(周波数・振幅は元のまま): x(t)=cos(t)+0.4cos(4t), y(t)=sin(t+90°)+0.4sin(4t+90°)")
fig.tight_layout()

now = datetime.now()
out_dir = Path(__file__).parent.parent / "output" / now.strftime("%Y-%m-%d")
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / f"compute_epicycles_phase_shift_{now.strftime('%H%M')}.png"
fig.savefig(out_path, dpi=150)
plt.close(fig)
print(f"\nプロットを保存しました: {out_path}")
