"""Static scene builder for the AnsiSky plugin.

Builds an 80x30 character grid (columns x rows) that serves as the background
for animated weather overlays.  Each cell is a ``(char, (r, g, b))`` tuple.
"""

from __future__ import annotations

import random

# ---------------------------------------------------------------------------
# Grid dimensions (must match renderer.py)
# ---------------------------------------------------------------------------
COLS = 80
ROWS = 30
CELL_W = 10
CELL_H = 18

# ---------------------------------------------------------------------------
# Embedded ASCII art
# ---------------------------------------------------------------------------
HOUSE = [
    "            _   _._          ",
    "           |_|-'_~_`-._      ",
    "        _.-'-_~_-~-_~-_`-._  ",
    "    _.-'_~-_~-_-~-_~_~-_~-_`-._",
    "   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
    "     |  []  []   []   []  [] |",
    "     |           __    ___   |",
    "   ._|  []  []  | .|  [___]  |_._._._._._._._._._._._._._._._._. ",
    "   |=|________()|__|()_______|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|",
    " ^^^^^^^^^^^^^^^ === ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",
]

TREE = [
    "      ####      ",
    "    ########    ",
    "   ##########   ",
    "    ########    ",
    "      _||_      ",
]

PINE_TREE = [
    "      *    ",
    "     ***   ",
    "    *****  ",
    "   ******* ",
    "     |||   ",
]

FENCE_ROW = "|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|"

# ---------------------------------------------------------------------------
# Colour palette (RGB tuples)
# ---------------------------------------------------------------------------
SKY_DAY = (135, 206, 235)
SKY_NIGHT = (15, 23, 42)
GROUND_GREEN = (34, 139, 34)
GROUND_SOIL = (139, 90, 43)
HOUSE_WALL = (210, 180, 140)
HOUSE_ROOF = (160, 82, 45)
HOUSE_DOOR = (101, 67, 33)
HOUSE_WINDOW = (255, 255, 150)
TREE_GREEN = (0, 100, 0)
TREE_TRUNK = (101, 67, 33)
PINE_GREEN = (0, 80, 0)
FENCE_COLOR = (160, 130, 100)
CHIMNEY_COLOR = (120, 60, 30)
SMOKE_COLOR = (180, 180, 180)
HUD_BG = (30, 30, 30)
HUD_TEXT = (255, 255, 255)
STAR_COLOR = (255, 255, 200)
CLOUD_COLOR = (240, 240, 240)
RAIN_COLOR = (173, 216, 230)
SNOW_COLOR = (255, 250, 250)
LIGHTNING_COLOR = (255, 255, 100)

# ---------------------------------------------------------------------------
# Per-character colour maps for the embedded art
# ---------------------------------------------------------------------------
_HOUSE_COLORS: dict[str, tuple[int, int, int]] = {
    # Roof / decorative lines
    "_": HOUSE_ROOF,
    "-": HOUSE_ROOF,
    "'": HOUSE_ROOF,
    "~": HOUSE_ROOF,
    ".": HOUSE_ROOF,
    "`": HOUSE_ROOF,
    # Walls
    "|": HOUSE_WALL,
    "(": HOUSE_WALL,
    ")": HOUSE_WALL,
    # Windows
    "[": HOUSE_WINDOW,
    "]": HOUSE_WINDOW,
    # Door
    "=": HOUSE_DOOR,
    # Chimney / smoke
    "^": CHIMNEY_COLOR,
}

_TREE_COLORS: dict[str, tuple[int, int, int]] = {
    "#": TREE_GREEN,
    "_": TREE_TRUNK,
    "|": TREE_TRUNK,
}

_PINE_COLORS: dict[str, tuple[int, int, int]] = {
    "*": PINE_GREEN,
    "|": TREE_TRUNK,
}

# ---------------------------------------------------------------------------
# Ground generation helpers
# ---------------------------------------------------------------------------
_GRASS_CHARS = ('"', "'", ",", "_")
_SOIL_CHAR = "."


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_ground_row(width: int, variant: int) -> str:
    """Return a string of *width* chars with alternating patches of grass and soil.

    The *variant* seeds the random pattern so each row looks different.
    Grass chars are ``\"``, ``'``, ``,``, ``_``; bare soil is ``.``.
    """
    rng = random.Random(variant + 42)  # deterministic, row-unique
    chars: list[str] = []
    col = 0
    while col < width:
        patch_type = rng.randint(0, 1)  # 0 = grass, 1 = soil
        patch_len = rng.randint(3, 9)
        patch_len = min(patch_len, width - col)
        if patch_type == 0:
            for _ in range(patch_len):
                chars.append(rng.choice(_GRASS_CHARS))
        else:
            chars.append(_SOIL_CHAR * patch_len)
        col += patch_len
    return "".join(chars)


def build_static_grid(
    is_day: bool,
) -> list[list[tuple[str, tuple[int, int, int]]]]:
    """Build the full 80x30 character grid.

    Each cell is ``(char, (r, g, b))``.  Layering order (back to front):

    1. Sky fill
    2. House at centre
    3. Trees left and right of house
    4. Ground rows (bottom 6)
    5. Fence
    6. HUD background (bottom 2 rows)
    """
    sky = SKY_DAY if is_day else SKY_NIGHT

    # 1. Initialise grid -- all sky
    grid: list[list[tuple[str, tuple[int, int, int]]]] = [
        [(" ", sky) for _ in range(COLS)] for _ in range(ROWS)
    ]

    # 2. House
    overlay_art(grid, HOUSE, 28, 13, _HOUSE_COLORS, default_sky=sky)

    # 3. Trees
    overlay_art(grid, TREE, 12, 18, _TREE_COLORS, default_sky=sky)
    overlay_art(grid, TREE, 4, 19, _TREE_COLORS, default_sky=sky)

    # 3b. Pine trees
    overlay_art(grid, PINE_TREE, 58, 17, _PINE_COLORS, default_sky=sky)
    overlay_art(grid, PINE_TREE, 68, 18, _PINE_COLORS, default_sky=sky)

    # 4. Ground (rows 24-29)
    for row_idx in range(24, ROWS):
        ground_str = generate_ground_row(COLS, row_idx)
        for col_idx, ch in enumerate(ground_str):
            color = GROUND_SOIL if ch == _SOIL_CHAR else GROUND_GREEN
            grid[row_idx][col_idx] = (ch, color)

    # 5. Fence (row 24 -- overwrites ground on that row)
    for col_idx, ch in enumerate(FENCE_ROW):
        if col_idx < COLS:
            grid[24][col_idx] = (ch, FENCE_COLOR)

    # 6. HUD background (rows 28-29)
    for row_idx in range(ROWS - 2, ROWS):
        for col_idx in range(COLS):
            grid[row_idx][col_idx] = (" ", HUD_BG)

    return grid


def overlay_text(
    grid: list[list[tuple[str, tuple[int, int, int]]]],
    text: str,
    x: int,
    y: int,
    color: tuple[int, int, int],
) -> None:
    """Write *text* characters onto *grid* at position (*x*, *y*).

    Overwrites existing cells.  Characters outside grid bounds are silently
    skipped.
    """
    for offset, ch in enumerate(text):
        gx = x + offset
        if 0 <= gx < COLS and 0 <= y < ROWS:
            grid[y][gx] = (ch, color)


def overlay_art(
    grid: list[list[tuple[str, tuple[int, int, int]]]],
    art: list[str],
    x: int,
    y: int,
    colors: dict[str, tuple[int, int, int]],
    default_sky: tuple[int, int, int] | None = None,
) -> None:
    """Overlay multi-line ASCII art onto *grid*.

    Parameters
    ----------
    art:
        List of strings, one per row.
    x, y:
        Top-left position on the grid.
    colors:
        Maps specific characters to RGB colour tuples.  Characters **not** in
        this dict retain the grid's existing colour (only the glyph is
        replaced).
    default_sky:
        If given, space characters (``" "``) that are **not** in *colors* are
        set to this colour.  Useful when placing art onto a uniform sky
        background.
    """
    for row_idx, line in enumerate(art):
        gy = y + row_idx
        if not (0 <= gy < ROWS):
            continue
        for col_idx, ch in enumerate(line):
            gx = x + col_idx
            if not (0 <= gx < COLS):
                continue
            if ch in colors:
                grid[gy][gx] = (ch, colors[ch])
            elif ch != " ":
                # Replace the glyph, keep the existing colour
                grid[gy][gx] = (ch, grid[gy][gx][1])
            elif default_sky is not None:
                grid[gy][gx] = (ch, default_sky)
