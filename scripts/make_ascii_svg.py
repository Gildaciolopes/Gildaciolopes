#!/usr/bin/env python3
"""Convert source-prepped.png into a self-typing monochrome ASCII SVG.

The prepped image is downsampled to a character grid; each cell's brightness
picks a glyph from a density ramp (bright -> sparse, dark -> dense). Each row
is wrapped in a horizontal clip that wipes left-to-right (a block "cursor"
rides the wipe edge), staggered top to bottom. Prints once, then freezes.

Design choices that keep it clean, not noisy:
  * Monochrome one light-gray fill (rainbow per-char = static).
  * High contrast: the background washes out to the space glyph, so only
    the subject prints.

Output: avi-ascii.svg
"""
from PIL import Image

SRC = "source-prepped.png"
OUT = "avi-ascii.svg"

COLS = 100          # character grid width
ROWS = 53           # character grid height (chars are ~2x tall as wide)
CELL_W = 6.0        # px advance per glyph (matches monospace at font-size 10)
CELL_H = 10.5       # px line height
FONT_SIZE = 10
FILL = "#c9d1d9"    # light gray, GitHub-ish foreground
CURSOR = "#39d353"  # green block riding the wipe edge
BG = "#0d1117"      # terminal background

ROW_DUR = 0.10      # seconds to wipe one row
ROW_STAGGER = 0.045  # seconds between successive rows starting

# bright (sparse) -> dark (dense). Leading space clears background to nothing.
RAMP = " .`:-=+*cs#%@"


def esc(c: str) -> str:
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}.get(c, c)


def build_rows(img: Image.Image) -> list[str]:
    img = img.convert("L").resize((COLS, ROWS))
    px = img.load()
    n = len(RAMP) - 1
    rows = []
    for y in range(ROWS):
        line = []
        for x in range(COLS):
            b = px[x, y]                 # 0=dark .. 255=bright
            idx = int((255 - b) / 255 * n)  # bright -> 0 (space)
            line.append(RAMP[idx])
        rows.append("".join(line).rstrip())
    return rows


def main() -> None:
    rows = build_rows(Image.open(SRC))
    w = COLS * CELL_W
    h = ROWS * CELL_H + 12

    out = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{w:.0f}" height="{h:.0f}" viewBox="0 0 {w:.0f} {h:.0f}" '
        f'font-family="\'Fira Code\',\'Cascadia Code\',Consolas,monospace">'
    )
    out.append(f'<rect width="100%" height="100%" fill="{BG}"/>')
    out.append(
        '<style>text{white-space:pre;font-size:%dpx;}'
        '.cur{fill:%s;}</style>' % (FONT_SIZE, CURSOR)
    )

    for i, line in enumerate(rows):
        if not line:
            continue
        y = (i + 1) * CELL_H
        row_w = len(line) * CELL_W
        begin = i * ROW_STAGGER
        clip_id = f"c{i}"
        # clip wipes from 0 width to full row width
        out.append(
            f'<clipPath id="{clip_id}"><rect x="0" y="{y - CELL_H:.1f}" '
            f'height="{CELL_H:.1f}" width="0">'
            f'<animate attributeName="width" from="0" to="{row_w:.1f}" '
            f'dur="{ROW_DUR}s" begin="{begin:.3f}s" fill="freeze"/>'
            f'</rect></clipPath>'
        )
        safe = "".join(esc(c) for c in line)
        out.append(
            f'<text x="0" y="{y:.1f}" fill="{FILL}" '
            f'clip-path="url(#{clip_id})" xml:space="preserve">{safe}</text>'
        )
        # cursor block rides the wipe edge, then fades
        out.append(
            f'<rect class="cur" x="0" y="{y - CELL_H + 1.5:.1f}" '
            f'width="{CELL_W:.1f}" height="{CELL_H - 2:.1f}" opacity="0">'
            f'<animate attributeName="x" from="0" to="{row_w:.1f}" '
            f'dur="{ROW_DUR}s" begin="{begin:.3f}s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" '
            f'keyTimes="0;0.05;0.9;1" dur="{ROW_DUR}s" begin="{begin:.3f}s" '
            f'fill="freeze"/></rect>'
        )

    out.append("</svg>")
    open(OUT, "w").write("\n".join(out))
    print(f"[ascii] wrote {OUT} ({len([r for r in rows if r])} printed rows)")


if __name__ == "__main__":
    main()
