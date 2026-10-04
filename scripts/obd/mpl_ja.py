"""
matplotlibで日本語ラベルを文字化けさせずに表示するための共通設定。

devcontainerにはデフォルトで日本語フォントが入っていないため、`fonts-noto-cjk`
（Noto Sans CJK JP）をインストールした上で、このモジュールのimportだけで
rcParamsのfont.familyを切り替えられるようにしている。
本の図を出すスクリプトでは、matplotlib.pyplotをimportした後に
`from mpl_ja import set_japanese_font; set_japanese_font()` を呼ぶ。
"""
import matplotlib.pyplot as plt

JAPANESE_FONT_FAMILY = "Noto Sans CJK JP"


def set_japanese_font() -> None:
    plt.rcParams["font.family"] = JAPANESE_FONT_FAMILY
