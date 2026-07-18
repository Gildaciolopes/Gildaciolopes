#!/usr/bin/env python3
"""Hand-author a fastfetch-style info card SVG.

Looks like the output of `fastfetch`: a title bar, then colored key/value rows.
Each line fades + slides in on a short stagger so the panel looks like it is
printing next to the portrait.

STATIC=1 emits a frozen frame (no animation) for local Quick Look previews.

Output: info-card.svg
"""
import os

OUT = "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

# --- theme: same terminal chrome as avi-ascii.svg (gradient bg, rx=12 frame,
# divider-line titlebar, bottom status bar) so both panels read as one set ---
BG = "#0d1117"
BG2 = "#111722"     # gradient top (matches ascii)
FRAME = "#30363d"   # frame + divider lines
TITLE_TEXT = "#7d8590"  # titlebar/status muted text
KEY = "#39d353"     # green keys
VAL = "#c9d1d9"     # light gray values
ACCENT = "#58a6ff"  # blue section titles / links
DIM = "#8b949e"     # dim / dots
BULLET = "#39d353"

# H chosen so that, at the README widths (ascii 370 / card 490), both panels
# render the SAME height: avi-ascii is 840x907 -> 399.5px@370; card 620x506 -> 399.5px@490.
W, H = 620, 506
PAD = 20            # matches ascii PAD (traffic-light origin)
PAD_X = 26
LINE_H = 21
TITLEBAR_H = 30
STATUS_H = 30
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

# rows: ("kv", key, value) | ("sec", title, "") | ("bullet", text, "")
ROWS = [
    ("head", "Gildaciolopes@github", ""),
    ("sep", "", ""),
    ("kv", "Cargo", "Desenvolvedor Full-Stack Pleno"),
    ("kv", "Exp", "+4 anos"),
    ("kv", "Empresa", "Visao Coop"),
    ("kv", "Edu", "ADS (cursando) + Tecnico Eletronica"),
    ("gap", "", ""),
    ("sec", "Stack", ""),
    ("kv", "Front", "React, Next.js, React Native, Typescript"),
    ("kv", "Back", "Node.js, NestJS, Express, Python, Django"),
    ("kv", "Mobile", "Expo, React Native"),
    ("kv", "Database", "PostgreSQL, MongoDB, Prisma, TypeORM"),
    ("kv", "Infra", "Docker, Nginx, AWS"),
    ("gap", "", ""),
    ("sec", "Highlights", ""),
    ("bullet", "Foco em Web & Mobile de ponta a ponta", ""),
    ("bullet", "Portfolio: gildacio.com", ""),
    ("bullet", "Comunidade: Servidor dos Programadores", ""),
]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def anim(begin: float) -> str:
    if STATIC:
        return ""
    return (
        f'<animate attributeName="opacity" from="0" to="1" dur="0.35s" '
        f'begin="{begin:.2f}s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" '
        f'from="8 0" to="0 0" dur="0.35s" begin="{begin:.2f}s" fill="freeze"/>'
    )


def main() -> None:
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{FONT}" font-size="13">',
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/>'
        f'<stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
        f'<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>',
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" '
        f'fill="none" stroke="{FRAME}"/>',
        # title bar: divider line + traffic lights + centered prompt (no fill)
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
        f'<circle cx="{PAD}" cy="{TITLEBAR_H/2}" r="5" fill="#ff5f56"/>',
        f'<circle cx="{PAD+16}" cy="{TITLEBAR_H/2}" r="5" fill="#ffbd2e"/>',
        f'<circle cx="{PAD+32}" cy="{TITLEBAR_H/2}" r="5" fill="#27c93f"/>',
        f'<text x="{W/2:.0f}" y="{TITLEBAR_H/2 + 4:.0f}" fill="{TITLE_TEXT}" '
        f'text-anchor="middle" font-size="12">Gildaciolopes@github: ~$ fastfetch</text>',
    ]

    y = 58
    i = 0
    for kind, a, b in ROWS:
        begin = 0.15 * i
        if kind == "gap":
            y += 8
            continue
        if kind == "sep":
            out.append(
                f'<g opacity="{1 if STATIC else 0}"><text x="{PAD_X}" y="{y}" '
                f'fill="{DIM}">----------------</text>{anim(begin)}</g>'
            )
            y += LINE_H
            i += 1
            continue
        if kind == "head":
            out.append(
                f'<g opacity="{1 if STATIC else 0}"><text x="{PAD_X}" y="{y}" '
                f'fill="{ACCENT}" font-weight="bold">{esc(a)}</text>{anim(begin)}</g>'
            )
            y += LINE_H
            i += 1
            continue
        if kind == "sec":
            out.append(
                f'<g opacity="{1 if STATIC else 0}"><text x="{PAD_X}" y="{y}" '
                f'fill="{ACCENT}" font-weight="bold">{esc("~ " + a)}</text>'
                f'{anim(begin)}</g>'
            )
            y += LINE_H
            i += 1
            continue
        if kind == "bullet":
            out.append(
                f'<g opacity="{1 if STATIC else 0}">'
                f'<text x="{PAD_X}" y="{y}" fill="{BULLET}">&#8226;</text>'
                f'<text x="{PAD_X+16}" y="{y}" fill="{VAL}">{esc(a)}</text>'
                f'{anim(begin)}</g>'
            )
            y += LINE_H
            i += 1
            continue
        # kv
        out.append(
            f'<g opacity="{1 if STATIC else 0}">'
            f'<text x="{PAD_X}" y="{y}" fill="{KEY}" font-weight="bold">{esc(a)}</text>'
            f'<text x="{PAD_X+90}" y="{y}" fill="{VAL}">{esc(b)}</text>'
            f'{anim(begin)}</g>'
        )
        y += LINE_H
        i += 1

    # bottom status bar (mirrors avi-ascii.svg): divider + prompt + blinking cursor
    line_y = H - STATUS_H
    status_y = line_y + 19
    prefix = "Gildaciolopes@github:~$ fastfetch "  # up to the cursor
    cursor_x = PAD + len(prefix) * 13 * 0.6
    out.append(f'<line x1="0" y1="{line_y}" x2="{W}" y2="{line_y}" stroke="{FRAME}"/>')
    out.append(
        f'<text x="{PAD}" y="{status_y}" fill="{TITLE_TEXT}" font-size="13">'
        f'Gildaciolopes@github:~$ <tspan fill="{VAL}">fastfetch</tspan></text>'
    )
    blink = (
        '' if STATIC else
        '<animate attributeName="opacity" values="1;1;0;0" '
        'keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/>'
    )
    out.append(
        f'<rect x="{cursor_x:.0f}" y="{status_y-12}" width="8" height="14" '
        f'fill="{VAL}">{blink}</rect>'
    )

    out.append("</svg>")
    open(OUT, "w").write("\n".join(out))
    print(f"[card] wrote {OUT}{' (STATIC)' if STATIC else ''}")


if __name__ == "__main__":
    main()
