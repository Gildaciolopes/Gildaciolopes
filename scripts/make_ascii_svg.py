#!/usr/bin/env python3
"""Convert source-prepped.png into a self-typing monochrome ASCII SVG.

The prepped image (bg removed + CLAHE contrast, see prep_photo.py) is
downsampled to a character grid; each cell's brightness picks a glyph from a
density ramp (bright -> sparse, dark -> dense).

Reveal: each row is wiped left-to-right by a clip, and STAGGER == ROW_DUR so a
SINGLE block cursor rasters continuously top -> bottom, like a real terminal
typing the portrait out once, then it freezes. Wrapped in terminal chrome
(rounded frame, gradient bg, title bar, bottom status line with a blinking
cursor) so the panel reads as a live shell instead of a bare image.

Design: monochrome one light-gray ink (rainbow per-char = static); high
contrast so the background washes out to the space glyph and only the subject
prints. STATIC=1 emits a frozen frame for local previews.

Output: avi-ascii.svg
"""
import html
import os

from PIL import Image, ImageEnhance

SRC = "source-prepped.png"
OUT = "avi-ascii.svg"
STATIC = bool(os.environ.get("STATIC"))

COLS = 100
ROWS = 53
CELL_W = 8
CELL_H = 15
# bright (sparse) -> dark (dense). Leading space clears background to nothing.
RAMP = " .`:-=+*cs#%@"

# prepped image already has bg removed + CLAHE, so only light global tuning:
CONTRAST = 1.05
BRIGHTNESS = 1.0
GAMMA = 1.18          # >1 brightens mids -> face lands in sparser chars
WHITE_FLOOR = 0.80    # luminance above this is forced to blank (space)

PAD = 20
TITLEBAR_H = 30
STATUS_H = 30
ART_W = COLS * CELL_W
ART_H = ROWS * CELL_H
CANVAS_W = ART_W + PAD * 2
CANVAS_H = TITLEBAR_H + ART_H + STATUS_H + PAD

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
INK = "#c9d1d9"       # the single ascii color
CURSOR = "#c9d1d9"

# reveal timing (one-shot; a single cursor rasters top -> bottom)
ROW_DUR = 0.11
STAGGER = 0.11        # == ROW_DUR -> one continuous cursor sweeping down


def build_rows() -> list[str]:
    im = Image.open(SRC).convert("L")
    im = ImageEnhance.Brightness(im).enhance(BRIGHTNESS)
    im = ImageEnhance.Contrast(im).enhance(CONTRAST)
    im = im.resize((COLS, ROWS), Image.LANCZOS)
    px = im.load()
    rows = []
    for y in range(ROWS):
        chars = []
        for x in range(COLS):
            lum = pow(px[x, y] / 255.0, GAMMA)
            if lum >= WHITE_FLOOR:
                chars.append(" ")
                continue
            idx = int((1.0 - lum) * (len(RAMP) - 1) + 0.5)
            chars.append(RAMP[max(0, min(len(RAMP) - 1, idx))])
        rows.append("".join(chars))
    return rows


def main() -> None:
    rows_txt = build_rows()
    art_top = TITLEBAR_H + PAD * 0.35

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" '
        f'height="{CANVAS_H}" viewBox="0 0 {CANVAS_W} {CANVAS_H}" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/>'
        f'<stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
        f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg)"/>',
        f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="12" '
        f'fill="none" stroke="{FRAME}"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
    ]
    for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        p.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dot}"/>')
    p.append(
        f'<text x="{CANVAS_W/2}" y="{TITLEBAR_H/2 + 4}" fill="{TITLE_TEXT}" '
        f'font-size="12" text-anchor="middle">gildacio@github: ~$ ./portrait.sh</text>'
    )

    font_size = CELL_H * 0.86
    for ry, line in enumerate(rows_txt):
        y = art_top + ry * CELL_H + CELL_H * 0.74
        row_y = art_top + ry * CELL_H
        delay = ry * STAGGER
        safe = html.escape(line)
        text = (
            f'<text xml:space="preserve" x="{PAD}" y="{y:.1f}" fill="{INK}" '
            f'font-size="{font_size:.1f}" textLength="{ART_W}" '
            f'lengthAdjust="spacing">{safe}</text>'
        )
        if STATIC:
            p.append(text)
            continue
        p.append(
            f'<clipPath id="r{ry}"><rect x="{PAD}" y="{row_y:.1f}" '
            f'height="{CELL_H}" width="0"><animate attributeName="width" '
            f'from="0" to="{ART_W}" begin="{delay:.3f}s" dur="{ROW_DUR:.2f}s" '
            f'fill="freeze"/></rect></clipPath>'
        )
        p.append(f'<g clip-path="url(#r{ry})">{text}</g>')
        p.append(
            f'<rect y="{row_y+1:.1f}" width="{CELL_W}" height="{CELL_H-2}" '
            f'fill="{CURSOR}" opacity="0"><animate attributeName="x" '
            f'from="{PAD}" to="{PAD+ART_W}" begin="{delay:.3f}s" '
            f'dur="{ROW_DUR:.2f}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0.85" begin="{delay:.3f}s"/>'
            f'<set attributeName="opacity" to="0" begin="{delay+ROW_DUR:.3f}s"/></rect>'
        )

    # bottom status bar with a steady blinking cursor
    line_y = TITLEBAR_H + ART_H + PAD * 0.35
    status_y = line_y + 19
    p.append(f'<line x1="0" y1="{line_y:.1f}" x2="{CANVAS_W}" y2="{line_y:.1f}" stroke="{FRAME}"/>')
    p.append(
        f'<text x="{PAD}" y="{status_y:.1f}" fill="{TITLE_TEXT}" font-size="13">'
        f'gildacio@github:~$ whoami <tspan fill="{INK}">Gildacio Lopes</tspan></text>'
    )
    p.append(
        f'<rect x="{PAD+322}" y="{status_y-12:.1f}" width="8" height="14" fill="{INK}">'
        f'<animate attributeName="opacity" values="1;1;0;0" '
        f'keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/></rect>'
    )

    p.append("</svg>")
    open(OUT, "w").write("".join(p))
    print(f"[ascii] wrote {OUT}{' (STATIC)' if STATIC else ''} ({CANVAS_W}x{CANVAS_H})")


if __name__ == "__main__":
    main()
