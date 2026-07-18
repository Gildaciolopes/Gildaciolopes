#!/usr/bin/env python3
"""Render data/contributions.json as an animated 53-week x 7-day heatmap SVG.

Rounded colored boxes on a GitHub-ish green ramp, revealed once with a
diagonal line-after-line slide-down (CSS keyframes that play on load then
freeze — no looping glow). Adds a Less->More legend and a stats footer.

Output: contrib-heatmap.svg
"""
import json
from datetime import datetime

SRC = "data/contributions.json"
OUT = "contrib-heatmap.svg"

# none -> brightest (level 5 is a neon top end, used for best days)
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL = 12          # box size
GAP = 3            # gap between boxes
RADIUS = 2.5
TOP = 34           # space for month labels
LEFT = 30          # space for weekday labels
FG = "#c9d1d9"
DIM = "#8b949e"
BG = "#0d1117"
FONT = "'Fira Code','Cascadia Code',Consolas,monospace"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
WEEKDAYS = {1: "Mon", 3: "Wed", 5: "Fri"}


def load() -> dict:
    return json.load(open(SRC))


def to_weeks(days: list[dict]) -> list[list[dict]]:
    """Group day list into columns (weeks), each 7 rows Sun..Sat."""
    weeks: list[list[dict]] = []
    col: list[dict] = []
    for d in days:
        wd = datetime.strptime(d["date"], "%Y-%m-%d").weekday()  # Mon=0..Sun=6
        wd = (wd + 1) % 7  # -> Sun=0..Sat=6
        if wd == 0 and col:
            weeks.append(col)
            col = []
        while len(col) < wd:
            col.append(None)
        col.append(d)
    if col:
        weeks.append(col)
    return weeks


def level_for(d: dict) -> int:
    lvl = d.get("level", 0)
    # promote a personal-best-scale day to the neon top end
    if d.get("count", 0) >= 12:
        lvl = 5
    return min(lvl, 5)


def main() -> None:
    data = load()
    days = data["days"]
    stats = data["stats"]
    weeks = to_weeks(days)
    n_weeks = len(weeks)

    grid_w = LEFT + n_weeks * (CELL + GAP)
    grid_h = TOP + 7 * (CELL + GAP)
    total_h = grid_h + 46  # legend + footer

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{grid_w}" '
        f'height="{total_h}" viewBox="0 0 {grid_w} {total_h}" font-family="{FONT}">',
        f'<rect width="100%" height="100%" fill="{BG}"/>',
    ]

    # keyframes: diagonal reveal. Each box delayed by (week + row) steps.
    out.append(
        '<style>'
        '.box{opacity:0;transform:translateY(-6px);'
        'animation:pop 0.4s ease-out forwards;}'
        '@keyframes pop{to{opacity:1;transform:translateY(0);}}'
        f'text{{font-size:9px;fill:{DIM};}}'
        '</style>'
    )

    # month labels
    last_month = None
    for wi, col in enumerate(weeks):
        first = next((d for d in col if d), None)
        if not first:
            continue
        m = int(first["date"][5:7])
        if m != last_month:
            x = LEFT + wi * (CELL + GAP)
            out.append(f'<text x="{x}" y="{TOP-16}">{MONTHS[m-1]}</text>')
            last_month = m

    # weekday labels
    for row, label in WEEKDAYS.items():
        y = TOP + row * (CELL + GAP) + CELL - 1
        out.append(f'<text x="0" y="{y}">{label}</text>')

    # boxes
    step = 0.012  # seconds per diagonal step
    for wi, col in enumerate(weeks):
        for row in range(7):
            d = col[row] if row < len(col) else None
            x = LEFT + wi * (CELL + GAP)
            y = TOP + row * (CELL + GAP)
            if d is None:
                continue
            lvl = level_for(d)
            delay = (wi + row) * step
            title = f'{d["count"]} on {d["date"]}'
            out.append(
                f'<rect class="box" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="{RADIUS}" fill="{PALETTE[lvl]}" '
                f'style="animation-delay:{delay:.3f}s">'
                f'<title>{title}</title></rect>'
            )

    # legend (Less -> More)
    ly = grid_h + 6
    lx = grid_w - (5 * (CELL + GAP)) - 44
    out.append(f'<text x="{lx-34}" y="{ly+CELL-2}">Less</text>')
    for i in range(5):
        out.append(
            f'<rect x="{lx + i*(CELL+GAP)}" y="{ly}" width="{CELL}" height="{CELL}" '
            f'rx="{RADIUS}" fill="{PALETTE[i]}"/>'
        )
    out.append(f'<text x="{lx + 5*(CELL+GAP)+4}" y="{ly+CELL-2}">More</text>')

    # footer stats
    fy = grid_h + 34
    total = stats["total"]
    cur = stats["current_streak"]
    longest = stats["longest_streak"]
    out.append(
        f'<text x="{LEFT}" y="{fy}" fill="{FG}" font-size="11" font-weight="bold">'
        f'{total:,} contributions in the last year</text>'
    )
    out.append(
        f'<text x="{grid_w-4}" y="{fy}" text-anchor="end" font-size="10">'
        f'streak atual {cur}d &#183; recorde {longest}d</text>'
    )

    out.append("</svg>")
    open(OUT, "w").write("\n".join(out))
    print(f"[heatmap] wrote {OUT} ({n_weeks} weeks, {total} contributions)")


if __name__ == "__main__":
    main()
