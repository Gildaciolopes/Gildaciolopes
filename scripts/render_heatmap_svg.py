#!/usr/bin/env python3
"""Render data/contributions.json as an animated 53-week x 7-day heatmap SVG.

Classic GitHub calendar of rounded, colored boxes on a green ramp, wrapped in
terminal chrome (rounded frame, gradient bg, title bar with traffic lights).
Revealed once with a DIAGONAL cascade: each box's delay = col*COL_T + row*ROW_T
with cubic-bezier easing, so the grid sweeps in top-left -> bottom-right, then
freezes (no looping glow). Below: a Less->More legend and a two-row stats
footer (total + date range; current/longest streak + best day).

Output: contrib-heatmap.svg
"""
import datetime
import json

SRC = "data/contributions.json"
OUT = "contrib-heatmap.svg"

# empty -> brightest. Level 5 is a neon top end for personal-best days.
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL = 12
GAP = 3
STEP = CELL + GAP
PAD = 22
LEFT_LABEL_W = 30
TOP_LABEL_H = 20
TITLEBAR_H = 30

BG = "#0a0e14"
BG2 = "#0d1420"
FRAME = "#1f6feb"
MUTED = "#7d8590"
TEXT = "#e6edf3"
ACCENT = "#22d3ee"
GREEN = "#39d353"
GOLD = "#f2cc60"

# reveal timing (one-shot diagonal cascade)
COL_T = 0.018   # per-column delay (left -> right sweep)
ROW_T = 0.045   # per-row delay (top -> bottom cascade)
CELL_DUR = 0.42

MONTHS_PT = ["jan", "fev", "mar", "abr", "mai", "jun",
             "jul", "ago", "set", "out", "nov", "dez"]


def level_for(count: int) -> int:
    if count == 0:
        return 0
    if count <= 5:
        return 1
    if count <= 15:
        return 2
    if count <= 30:
        return 3
    if count <= 50:
        return 4
    return 5


def build_grid(days: list[dict]) -> list[list]:
    first = datetime.date.fromisoformat(days[0]["date"])
    lead_pad = (first.weekday() + 1) % 7  # sunday=0
    grid, col = [], [None] * lead_pad
    for d in days:
        date = datetime.date.fromisoformat(d["date"])
        weekday = (date.weekday() + 1) % 7
        while len(col) < weekday:
            col.append(None)
        col.append((d["date"], d["count"], level_for(d["count"])))
        if len(col) == 7:
            grid.append(col)
            col = []
    if col:
        while len(col) < 7:
            col.append(None)
        grid.append(col)
    return grid


def main() -> None:
    data = json.load(open(SRC))
    days = data["days"]
    stats = data["stats"]
    grid = build_grid(days)
    n_cols = len(grid)
    art_w = n_cols * STEP
    art_h = 7 * STEP

    # month labels: first column where a new month starts within its first week
    month_labels, seen = [], set()
    for ci, column in enumerate(grid):
        for cell in column:
            if cell is None:
                continue
            date = datetime.date.fromisoformat(cell[0])
            key = (date.year, date.month)
            if key not in seen and date.day <= 7:
                seen.add(key)
                month_labels.append((ci, MONTHS_PT[date.month - 1]))
            break

    canvas_w = PAD + LEFT_LABEL_W + art_w + PAD
    stats_h = 88
    canvas_h = TITLEBAR_H + TOP_LABEL_H + art_h + stats_h + PAD

    css = (
        "@keyframes cell{0%{opacity:0;transform:translateY(-6px);}"
        "100%{opacity:1;transform:translateY(0);}}"
        f".c{{opacity:0;animation:cell {CELL_DUR:.2f}s cubic-bezier(.2,.8,.2,1) both;}}"
    )

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" '
        f'height="{canvas_h}" viewBox="0 0 {canvas_w} {canvas_h}" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
        f'<style>{css}</style>',
        '<defs><linearGradient id="hbg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/>'
        f'<stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
        f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#hbg)"/>',
        f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" '
        f'fill="none" stroke="{FRAME}" stroke-opacity="0.55"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{canvas_w}" y2="{TITLEBAR_H}" '
        f'stroke="{FRAME}" stroke-opacity="0.35"/>',
    ]
    for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        p.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dot}"/>')
    p.append(
        f'<text x="{canvas_w/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" '
        f'font-size="12" text-anchor="middle">gildacio@github: ~/contributions --graph</text>'
    )

    grid_top = TITLEBAR_H + TOP_LABEL_H
    grid_left = PAD + LEFT_LABEL_W

    for ci, label in month_labels:
        x = grid_left + ci * STEP
        p.append(f'<text x="{x}" y="{TITLEBAR_H + 14}" fill="{MUTED}" font-size="10">{label}</text>')

    for wi, wname in [(1, "Seg"), (3, "Qua"), (5, "Sex")]:
        y = grid_top + wi * STEP + CELL * 0.78
        p.append(f'<text x="{PAD}" y="{y:.1f}" fill="{MUTED}" font-size="9">{wname}</text>')

    # boxes -- diagonal slide-down reveal (once, freeze)
    for ci, column in enumerate(grid):
        gx = grid_left + ci * STEP
        for ri, cell in enumerate(column):
            if cell is None:
                continue
            date_s, count, lvl = cell
            gy = grid_top + ri * STEP
            delay = ci * COL_T + ri * ROW_T
            plural = "" if count == 1 else "s"
            p.append(
                f'<rect class="c" x="{gx}" y="{gy}" width="{CELL}" height="{CELL}" '
                f'rx="2.5" fill="{PALETTE[lvl]}" style="animation-delay:{delay:.3f}s">'
                f'<title>{date_s}: {count} contribuicão{plural}</title></rect>'
            )

    # legend: Less [][][][][] More
    leg_y = grid_top + art_h + 6
    leg_x = canvas_w - PAD - (len(PALETTE) * (CELL - 1) + 70)
    p.append(f'<text x="{leg_x}" y="{leg_y + CELL*0.8:.1f}" fill="{MUTED}" '
             f'font-size="10" text-anchor="end">Menos</text>')
    lx = leg_x + 8
    for color in PALETTE:
        p.append(f'<rect x="{lx}" y="{leg_y}" width="{CELL-1}" height="{CELL-1}" rx="2.2" fill="{color}"/>')
        lx += CELL
    p.append(f'<text x="{lx + 4}" y="{leg_y + CELL*0.8:.1f}" fill="{MUTED}" font-size="10">Mais</text>')

    sep_y = leg_y + CELL + 14
    p.append(f'<line x1="0" y1="{sep_y}" x2="{canvas_w}" y2="{sep_y}" '
             f'stroke="{FRAME}" stroke-opacity="0.25"/>')

    total = stats["total"]
    cs = stats["current_streak"]
    ls = stats["longest_streak"]
    best = stats["best_day"]
    rng_start, rng_end = days[0]["date"], days[-1]["date"]

    ly = sep_y + 24
    p.append(f'<text x="{PAD}" y="{ly}" font-size="13" fill="{GREEN}" xml:space="preserve">'
             f'<tspan font-weight="700">{total:,}</tspan>'
             f'<tspan fill="{MUTED}"> contribuições no último ano</tspan></text>')
    p.append(f'<text x="{canvas_w - PAD}" y="{ly}" font-size="12" fill="{MUTED}" '
             f'text-anchor="end">{rng_start} &#8594; {rng_end}</text>')
    ly += 24
    p.append(f'<text x="{PAD}" y="{ly}" font-size="13" fill="{MUTED}" xml:space="preserve">streak atual '
             f'<tspan fill="{ACCENT}" font-weight="700">{cs} dias</tspan>'
             f'<tspan fill="{MUTED}">   &#183;   recorde </tspan>'
             f'<tspan fill="{ACCENT}" font-weight="700">{ls} dias</tspan></text>')
    p.append(f'<text x="{canvas_w - PAD}" y="{ly}" font-size="12" fill="{MUTED}" '
             f'text-anchor="end">melhor dia <tspan fill="{GOLD}" font-weight="700">'
             f'{best["count"]}</tspan> em {best["date"]}</text>')

    p.append("</svg>")
    open(OUT, "w").write("".join(p))
    print(f"[heatmap] wrote {OUT} ({n_cols} weeks, {total} contributions)")


if __name__ == "__main__":
    main()
