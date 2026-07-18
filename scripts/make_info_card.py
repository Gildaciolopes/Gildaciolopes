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

# --- theme (GitHub dark terminal) ---
BG = "#0d1117"
BORDER = "#30363d"
HEADER = "#161b22"
KEY = "#39d353"     # green keys
VAL = "#c9d1d9"     # light gray values
ACCENT = "#58a6ff"  # blue section titles / links
DIM = "#8b949e"     # dim / dots
BULLET = "#39d353"

W, H = 620, 470
PAD_X = 26
LINE_H = 21
FONT = "'Fira Code','Cascadia Code',Consolas,monospace"

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
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" '
        f'fill="{BG}" stroke="{BORDER}"/>',
        # title bar with traffic lights
        f'<rect x="0.5" y="0.5" width="{W-1}" height="30" rx="10" fill="{HEADER}"/>',
        f'<rect x="0.5" y="16" width="{W-1}" height="15" fill="{HEADER}"/>',
        f'<circle cx="18" cy="16" r="5" fill="#ff5f56"/>',
        f'<circle cx="36" cy="16" r="5" fill="#ffbd2e"/>',
        f'<circle cx="54" cy="16" r="5" fill="#27c93f"/>',
        f'<text x="{W/2:.0f}" y="20" fill="{DIM}" text-anchor="middle" '
        f'font-size="12">Gildaciolopes@github: ~$ fastfetch</text>',
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

    out.append("</svg>")
    open(OUT, "w").write("\n".join(out))
    print(f"[card] wrote {OUT}{' (STATIC)' if STATIC else ''}")


if __name__ == "__main__":
    main()
