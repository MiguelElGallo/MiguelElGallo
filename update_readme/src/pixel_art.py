"""Generate the 8-bit SVG artwork used by the profile README and GitHub Pages site.

Text is drawn with a built-in bitmap font so the SVGs render identically everywhere
(GitHub strips external fonts from images). Run from ``update_readme/``::

    uv run python -m src.pixel_art
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets" / "8bit"

GLYPH_HEIGHT = 7

# 5x7 bitmap font (narrow glyphs are allowed). "#" = lit pixel.
FONT: dict[str, tuple[str, ...]] = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "Ü": (".#.#.", ".....", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    " ": ("...", "...", "...", "...", "...", "...", "..."),
    ".": (".", ".", ".", ".", ".", ".", "#"),
    ",": ("..", "..", "..", "..", "..", ".#", "#."),
    ":": (".", "#", ".", ".", ".", "#", "."),
    "·": ("...", "...", "...", ".#.", "...", "...", "..."),
    "-": ("....", "....", "....", "####", "....", "....", "...."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "!": ("#", "#", "#", "#", "#", ".", "#"),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    ">": ("#...", ".#..", "..#.", "...#", "..#.", ".#..", "#..."),
    "▶": ("#...", "##..", "###.", "####", "###.", "##..", "#..."),
    "♥": (".....", ".#.#.", "#####", "#####", ".###.", "..#..", "....."),
}

# 16x16 rooster ("El Gallo"), facing right. Outlines are added automatically.
ROOSTER: tuple[str, ...] = (
    "..........RR....",
    ".........RRRR...",
    "........RRRR....",
    "........WWWWW...",
    ".......WWWKWWY..",
    ".GG....WWWWWYYY.",
    "GGGG...WWWWWR...",
    "GBGGG.WWWWWWR...",
    ".GBGGWWWWWWW....",
    "..GBWWWWOWWW....",
    "...WWWWOOWWW....",
    "...WWWWWWWWW....",
    "....WWWWWWW.....",
    "......L..L......",
    "......L..L......",
    ".....LL.LL......",
)

ROOSTER_COLORS = {
    "R": "#e23b3b",
    "W": "#fff6e0",
    "K": "#1b1b2f",
    "Y": "#ffb627",
    "O": "#f28c28",
    "G": "#2a9d8f",
    "B": "#1d6f65",
    "L": "#f28c28",
}

CLOUD: tuple[str, ...] = (
    "....####......",
    "..########....",
    ".###########..",
    "##############",
    ".############.",
)

MOON: tuple[str, ...] = (
    "..####..",
    ".###..#.",
    "###.....",
    "###.....",
    "###.....",
    "###.....",
    ".###..#.",
    "..####..",
)

SUN: tuple[str, ...] = (
    "..####..",
    ".######.",
    "########",
    "########",
    "########",
    "########",
    ".######.",
    "..####..",
)


@dataclass(frozen=True)
class Theme:
    """Colour palette for one colour scheme."""

    name: str
    sky: tuple[str, ...]
    title: str
    title_shadow: str
    subtitle: str
    accent: str
    blink: str
    cloud: str
    orb: str
    grass: str
    grass_dark: str
    dirt: str
    dirt_dark: str
    outline: str
    panel: str
    panel_border: str
    panel_inner: str
    label: str
    value: str
    heart: str
    star: str | None


LIGHT = Theme(
    name="light",
    sky=("#bfe3ff", "#cdeaff", "#dbf0ff", "#e8f6ff", "#f3faff"),
    title="#1b1b2f",
    title_shadow="#8fc1e8",
    subtitle="#3d3d6b",
    accent="#d6336c",
    blink="#1b1b2f",
    cloud="#ffffff",
    orb="#ffd166",
    grass="#6cc24a",
    grass_dark="#4a9a34",
    dirt="#c9884d",
    dirt_dark="#a86b35",
    outline="#1b1b2f",
    panel="#fffdf6",
    panel_border="#1b1b2f",
    panel_inner="#8fc1e8",
    label="#d6336c",
    value="#1b1b2f",
    heart="#e23b3b",
    star=None,
)

DARK = Theme(
    name="dark",
    sky=("#0b1026", "#101735", "#161f45", "#1c2856", "#233266"),
    title="#fff6e0",
    title_shadow="#d6336c",
    subtitle="#b8c4ff",
    accent="#ffd166",
    blink="#fff6e0",
    cloud="#3a4a86",
    orb="#fff3b0",
    grass="#3f8f3a",
    grass_dark="#2c6a29",
    dirt="#7a5230",
    dirt_dark="#5c3c22",
    outline="#05060f",
    panel="#141a36",
    panel_border="#b8c4ff",
    panel_inner="#3a4a86",
    label="#ffd166",
    value="#fff6e0",
    heart="#ff5d73",
    star="#fff6e0",
)


def _rect(x: float, y: float, w: float, h: float, fill: str | None = None, extra: str = "") -> str:
    attrs = f'x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}"'
    if fill:
        attrs += f' fill="{fill}"'
    return f"<rect {attrs}{extra}/>"


def _seg(x: float, y: float, w: float, h: float) -> str:
    """Return a rectangle as a compact path segment."""
    return f"M{x:g} {y:g}h{w:g}v{h:g}h{-w:g}z"


def _group(fill: str, segments: list[str]) -> str:
    return f'<path fill="{fill}" d="{"".join(segments)}"/>' if segments else ""


def _bitmap_rects(rows: tuple[str, ...], x: float, y: float, scale: float, fill: str) -> list[str]:
    """Render a 1-bit bitmap as horizontal pixel runs in a single path."""
    return [_group(fill, _bitmap_runs(rows, x, y, scale))]


def _bitmap_runs(rows: tuple[str, ...], x: float, y: float, scale: float) -> list[str]:
    rects: list[str] = []
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            if row[c] == ".":
                c += 1
                continue
            start = c
            while c < len(row) and row[c] != ".":
                c += 1
            rects.append(_seg(x + start * scale, y + r * scale, (c - start) * scale, scale))
    return rects


def text_width(text: str, scale: float) -> float:
    """Return the rendered width of ``text`` in SVG units."""
    glyphs = [FONT[ch] for ch in text.upper()]
    if not glyphs:
        return 0
    return (sum(len(g[0]) for g in glyphs) + len(glyphs) - 1) * scale


def pixel_text(
    text: str,
    x: float,
    y: float,
    scale: float,
    fill: str,
    shadow: str | None = None,
) -> str:
    """Render text in the bitmap font, optionally with a 1-pixel drop shadow."""
    layers: list[str] = []
    passes = [(scale, shadow), (0, fill)] if shadow else [(0, fill)]
    for offset, colour in passes:
        assert colour is not None
        cursor = x + offset
        rects: list[str] = []
        for ch in text.upper():
            glyph = FONT[ch]
            rects += _bitmap_runs(glyph, cursor, y + offset, scale)
            cursor += (len(glyph[0]) + 1) * scale
        layers.append(_group(colour, rects))
    return "".join(layers)


def sprite(
    rows: tuple[str, ...],
    colours: dict[str, str],
    x: float,
    y: float,
    scale: float,
    outline: str | None = None,
) -> str:
    """Render a multi-colour sprite with an optional automatic 1-pixel outline."""
    height, width = len(rows), len(rows[0])
    out: list[str] = []
    if outline:
        edge = []
        for r in range(-1, height + 1):
            line = ""
            for c in range(-1, width + 1):
                filled = 0 <= r < height and 0 <= c < width and rows[r][c] != "."
                near = any(
                    0 <= r + dr < height and 0 <= c + dc < width and rows[r + dr][c + dc] != "."
                    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))
                )
                line += "#" if near and not filled else "."
            edge.append(line)
        out += _bitmap_rects(tuple(edge), x - scale, y - scale, scale, outline)
    for key, colour in colours.items():
        mask = tuple("".join("#" if ch == key else "." for ch in row) for row in rows)
        out += _bitmap_rects(mask, x, y, scale, colour)
    return "".join(out)


def _style(theme: Theme) -> str:
    return (
        "<style>"
        "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
        "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}"
        "@keyframes drift{from{transform:translateX(-160px)}to{transform:translateX(1000px)}}"
        "@keyframes twinkle{0%,100%{opacity:1}50%{opacity:.25}}"
        ".blink{animation:blink 1.2s steps(1) infinite}"
        ".bob{animation:bob 1.6s steps(2) infinite}"
        ".drift{animation:drift linear infinite}"
        ".twinkle{animation:twinkle 2.4s steps(2) infinite}"
        "@media (prefers-reduced-motion:reduce){"
        ".blink,.bob,.drift,.twinkle{animation:none}}"
        "</style>"
    )


def banner(theme: Theme) -> str:
    """Build the hero banner SVG."""
    width, height, ground = 960, 270, 214
    p = 6  # base "pixel" size for scenery
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" shape-rendering="crispEdges" role="img" '
        'aria-labelledby="title desc">',
        '<title id="title">Miguel Peredo Zürcher - Data Platform Architect</title>',
        '<desc id="desc">8-bit banner with a pixel-art rooster, El Gallo.</desc>',
        _style(theme),
    ]

    band = ground / len(theme.sky)
    for i, colour in enumerate(theme.sky):
        parts.append(_rect(0, round(i * band), width, round(band) + 1, colour))

    if theme.star:
        stars = [(40, 24), (180, 12), (330, 36), (470, 18), (610, 30), (720, 12), (905, 60)]
        stars += [(250, 60), (560, 64), (860, 150), (120, 150), (690, 170)]
        for i, (sx, sy) in enumerate(stars):
            delay = f' style="animation-delay:{(i % 4) * 0.6:g}s"'
            parts.append(_rect(sx, sy, p / 2, p / 2, theme.star, f' class="twinkle"{delay}'))

    orb = MOON if theme.star else SUN
    parts.append("".join(_bitmap_rects(orb, 868, 18, p, theme.orb)))

    for y, dur, delay in ((6, 70, 0), (12, 95, -55)):
        cloud = "".join(_bitmap_rects(CLOUD, 0, y, p, theme.cloud))
        style = f' style="animation-duration:{dur}s;animation-delay:{delay}s"'
        parts.append(f'<g class="drift"{style}>{cloud}</g>')

    # Ground: jagged grass on top of a brick-patterned dirt strip.
    parts.append(_rect(0, ground, width, height - ground, theme.dirt))
    grass = [_seg(0, ground, width, p * 2)]
    grass_dark, bricks = [], []
    for gx in range(0, width, p * 2):
        grass_dark.append(_seg(gx, ground + p * 2, p, p))
        if (gx // (p * 2)) % 3 == 0:
            grass.append(_seg(gx + p, ground - p, p, p))
    for row, gy in enumerate(range(ground + p * 4, height, p * 3)):
        shift = 0 if row % 2 == 0 else p * 3
        for gx in range(-shift, width, p * 6):
            bricks.append(_seg(gx, gy, p * 5, p / 2))
    parts += [_group(theme.grass, grass), _group(theme.grass_dark, grass_dark)]
    parts.append(_group(theme.dirt_dark, bricks))

    rooster_scale = 9
    rooster_y = ground - len(ROOSTER) * rooster_scale
    rooster = sprite(ROOSTER, ROOSTER_COLORS, 64, rooster_y, rooster_scale, theme.outline)
    parts.append(f'<g class="bob">{rooster}</g>')

    tx = 250
    parts.append(pixel_text("Miguel Peredo", tx, 44, 6, theme.title, theme.title_shadow))
    parts.append(pixel_text("Zürcher", tx, 100, 6, theme.title, theme.title_shadow))
    parts.append(pixel_text("Data Platform Architect", tx, 158, 3, theme.subtitle))
    accent_x = tx + text_width("Data Platform Architect ", 3)
    parts.append(pixel_text("· AI Agents", accent_x, 158, 3, theme.accent))
    press = pixel_text("Press start ▶", tx, 190, 2, theme.blink)
    parts.append(f'<g class="blink">{press}</g>')
    parts.append("</svg>")
    return "".join(parts)


STATS: tuple[tuple[str, str], ...] = (
    ("Class", "Data Platform Architect"),
    ("Level", "20+ years"),
    ("Region", "Europe"),
    ("Guilds", "Automotive · Banking · Manufacturing"),
    ("Skills", "Azure · Snowflake · Python · SQL · IaC"),
    ("Magic", "LLMs · RAG · AI Agents · MCP"),
)


def player_card(theme: Theme) -> str:
    """Build an RPG-style 'player stats' dialog box SVG."""
    width, height, p = 960, 290, 6
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" shape-rendering="crispEdges" role="img" '
        'aria-labelledby="title">',
        '<title id="title">Player 1 stats: Data Platform Architect, 20+ years, Europe. '
        "Skills: Azure, Snowflake, Python, SQL, IaC, LLMs, RAG, AI Agents, MCP.</title>",
        _style(theme),
    ]
    # Stepped-corner dialog box: outer border, inner accent line, panel.
    parts.append(_rect(p, 0, width - 2 * p, height, theme.panel_border))
    parts.append(_rect(0, p, width, height - 2 * p, theme.panel_border))
    parts.append(_rect(p, p, width - 2 * p, height - 2 * p, theme.panel_inner))
    parts.append(_rect(2 * p, 2 * p, width - 4 * p, height - 4 * p, theme.panel))

    parts.append(pixel_text("Player 1", 36, 32, 4, theme.label))
    hearts_x = width - 36 - text_width("♥♥♥♥♥", 4)
    parts.append(pixel_text("♥♥♥♥♥", hearts_x, 32, 4, theme.heart))
    parts.append(_rect(36, 72, width - 72, p / 2, theme.panel_inner))

    label_x, value_x, y = 36, 180, 92
    for label, value in STATS:
        parts.append(pixel_text(label, label_x, y, 3, theme.label))
        parts.append(pixel_text(value, value_x, y, 3, theme.value))
        y += 30
    cursor = pixel_text("▶", width - 60, height - 50, 3, theme.value)
    parts.append(f'<g class="blink">{cursor}</g>')
    parts.append("</svg>")
    return "".join(parts)


def favicon() -> str:
    """Build a square rooster favicon for the GitHub Pages site."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 18 18" width="64" height="64" '
        'shape-rendering="crispEdges">'
        + sprite(ROOSTER, ROOSTER_COLORS, 1, 1, 1, LIGHT.outline)
        + "</svg>"
    )


def render_all() -> dict[str, str]:
    """Return every generated asset keyed by file name."""
    files = {"favicon.svg": favicon()}
    for theme in (LIGHT, DARK):
        files[f"banner-{theme.name}.svg"] = banner(theme)
        files[f"player-card-{theme.name}.svg"] = player_card(theme)
    return {name: svg + "\n" for name, svg in files.items()}


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for name, svg in render_all().items():
        (ASSETS_DIR / name).write_text(svg, encoding="utf-8")
        print(f"🕹️  wrote {ASSETS_DIR / name} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
