"""Shared Pango markup builder for Waybar tooltips.

どのツールチップも同じ見た目にするための部品。構成は次の順に並べる。

    header(...)    大きなアイコンと題名、その下に小さな英字のステータス
    grid(rows)     ラベルと値の表。1行に2組まで並べられる
    section(...)   グラフなどの前に置く小見出し
    rule()         区切り線
    notes(...)     補足の文（操作方法など）

表は等幅フォントで組み、全角文字は2桁として桁を揃える。
"""

from __future__ import annotations

import html
import unicodedata
from typing import Iterable, Sequence

LABEL = "#7f849c"
VALUE = "#cdd6f4"
ACCENT = "#a6e3a1"
RULE = "#45475a"
WARN = "#f9e2af"
CRITICAL = "#f38ba8"

GUTTER = 3
RULE_WIDTH = 40

Cell = tuple[str, str]


def esc(text: object) -> str:
    return html.escape(str(text), quote=False)


def width(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)


def pad(text: str, size: int, right: bool = False) -> str:
    gap = " " * max(0, size - width(text))
    return gap + text if right else text + gap


def mono(text: str) -> str:
    return f'<span font_family="monospace">{text}</span>'


def header(icon: str, title: str, subtitle: str = "", accent: str = ACCENT) -> str:
    lines = [
        f'<span size="x-large" foreground="{VALUE}">{esc(icon)}</span>  '
        f'<span size="large" weight="bold" foreground="{VALUE}">{esc(title)}</span>'
    ]
    if subtitle:
        lines.append(
            f'<span font_family="monospace" size="small" letter_spacing="2048" '
            f'foreground="{accent}">{esc(subtitle.upper())}</span>'
        )
    return "\n".join(lines) + "\n"


def grid(rows: Iterable[Sequence[Cell]], colors: dict[str, str] | None = None) -> str:
    """Rows of one or two (label, value) cells; columns size to their widest entry.

    `colors` maps a label to a value color, e.g. to flag a high reading.
    """
    rows = [list(row) for row in rows]
    colors = colors or {}
    columns = max((len(row) for row in rows), default=0)
    label_w = [0] * columns
    value_w = [0] * columns
    for row in rows:
        for i, (label, value) in enumerate(row):
            label_w[i] = max(label_w[i], width(label))
            value_w[i] = max(value_w[i], width(value))
    out = []
    for row in rows:
        cells = []
        for i, (label, value) in enumerate(row):
            color = colors.get(label, VALUE)
            cells.append(
                f'<span foreground="{LABEL}">{esc(pad(label, label_w[i] + 2))}</span>'
                f'<span foreground="{color}">{esc(pad(value, value_w[i], right=True))}</span>'
            )
        out.append((" " * GUTTER).join(cells))
    return mono("\n".join(out))


def grid_width(rows: Iterable[Sequence[Cell]]) -> int:
    rows = [list(row) for row in rows]
    columns = max((len(row) for row in rows), default=0)
    total = 0
    for i in range(columns):
        cells = [row[i] for row in rows if len(row) > i]
        total += max(width(l) for l, _ in cells) + 2 + max(width(v) for _, v in cells)
    return total + GUTTER * max(0, columns - 1)


def rule(size: int = RULE_WIDTH) -> str:
    return mono(f'<span foreground="{RULE}">{"─" * size}</span>')


def section(title: str) -> str:
    return (
        f'<span font_family="monospace" size="small" letter_spacing="1024" '
        f'foreground="{LABEL}">{esc(title.upper())}</span>'
    )


def notes(*lines: str) -> str:
    return "\n".join(f'<span foreground="{LABEL}">{esc(line)}</span>' for line in lines)


def level_color(value: float | None, warn: float, critical: float) -> str:
    if value is None:
        return VALUE
    if value >= critical:
        return CRITICAL
    if value >= warn:
        return WARN
    return VALUE


def meter(fraction: float, size: int, color: str = ACCENT) -> str:
    """Horizontal bar in eighth-blocks; the unfilled part is drawn in the rule color."""
    eighths = round(max(0.0, min(1.0, fraction)) * size * 8)
    full, part = divmod(eighths, 8)
    filled = "█" * full + (" ▏▎▍▌▋▊▉"[part] if part else "")
    rest = "─" * (size - width(filled))
    return mono(f'<span foreground="{color}">{filled}</span><span foreground="{RULE}">{rest}</span>')


def join(*blocks: str | None) -> str:
    return "\n".join(block for block in blocks if block is not None)
