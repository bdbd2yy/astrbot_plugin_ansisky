"""Static scene builder for the AnsiSky plugin.

Builds an 80x30 character grid (columns x rows) that serves as the background
for animated weather overlays.  Each cell is a ``(char, (r, g, b))`` tuple.

Visual style based on the weathr project (github.com/Veirt/weathr).
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Grid dimensions (must match renderer.py)
# ---------------------------------------------------------------------------
COLS = 80
ROWS = 30
CELL_W = 10
CELL_H = 18

GROUND_HEIGHT = 7

# ---------------------------------------------------------------------------
# Embedded ASCII art
# ---------------------------------------------------------------------------
HOUSE = [
    "            _   _._          ",
    "           |_|-'_~_`-._      ",
    "        _.-'-_~_-~_-~-_`-._  ",
    "    _.-'_~-_~-_-~-_~_~-_~-_`-._",
    "   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
    "     |  []  []   []   []  [] |",
    "     |           __    ___   |",
    "   ._|  []  []  | .|  [___]  |_._._._._._._._._._._._._._._._._. ",
    "   |=|________()|__|()_______|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|=|",
    " ^^^^^^^^^^^^^^^ === ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",
]

HOUSE_WIDTH = 64
HOUSE_HEIGHT = 10

TREE = [
    "      ####      ",
    "    ########    ",
    "   ##########   ",
    "    ########    ",
    "      _||_      ",
]

PINE_TREE = [
    "    *    ",
    "   ***   ",
    "  *****  ",
    " ******* ",
    "   |||   ",
]

FENCE = [
    "|--|--|--|--|",
    "|  |  |  |  |",
]

MAILBOX = [
    " ___ ",
    "|___|",
    "  |  ",
]

# ---------------------------------------------------------------------------
# Colour palette — day
# ---------------------------------------------------------------------------
# Sky / atmosphere
SKY_DAY = (0, 255, 255)       # Cyan
SKY_NIGHT = (0, 0, 139)       # DarkBlue

# House
ROOF_DAY = (139, 0, 0)         # DarkRed
ROOF_NIGHT = (139, 0, 139)     # DarkMagenta
WOOD_DAY = (210, 180, 140)     # Tan
WOOD_NIGHT = (100, 70, 50)     # Dark brown
DOOR_DAY = (139, 69, 19)       # SaddleBrown
DOOR_NIGHT = (80, 40, 10)
WINDOW_DAY = (0, 255, 255)     # Cyan
WINDOW_NIGHT = (255, 255, 0)   # Yellow
TRIM = (105, 105, 105)         # DimGrey

# Ground
GROUND_DAY = (0, 128, 0)       # Green
GROUND_NIGHT = (0, 100, 0)     # DarkGreen
GRASS_SECONDARY_DAY = (0, 100, 0)
GRASS_SECONDARY_NIGHT = (0, 50, 0)
SOIL_DAY = (101, 67, 33)
SOIL_NIGHT = (60, 40, 20)
FLOWER_COLORS_DAY = ((255, 0, 255), (255, 0, 0), (0, 255, 255), (255, 255, 0))
FLOWER_COLORS_NIGHT = ((139, 0, 139), (139, 0, 0), (0, 0, 255), (128, 128, 0))

# Decorations
TREE_FOLIAGE_DAY = (0, 100, 0)
TREE_FOLIAGE_NIGHT = (0, 50, 0)
TREE_TRUNK = (101, 67, 33)
FENCE_DAY = (255, 255, 255)
FENCE_NIGHT = (128, 128, 128)
MAILBOX_DAY = (0, 0, 255)
MAILBOX_NIGHT = (0, 0, 139)

# Chimney / smoke
CHIMNEY_COLOR = (120, 60, 30)
SMOKE_COLOR = (180, 180, 180)

# HUD
HUD_BG = (30, 30, 30)
HUD_TEXT = (255, 255, 255)

# ---------------------------------------------------------------------------
# Per-character colour maps for the embedded art
# ---------------------------------------------------------------------------
_HOUSE_WINDOW_CHARS = {"[", "]"}
_HOUSE_DOOR_CHARS = {"(", ")"}
_HOUSE_TRIM_CHARS = {"=", "|"}


# ---------------------------------------------------------------------------
# Ground generation
# ---------------------------------------------------------------------------

def _pseudo_rand(x: int, y: int) -> int:
    return ((x ^ 0x5DEECE6) * (y ^ 0xB)) % 100


def _ground_cell(x: int, y: int, is_day: bool) -> tuple[str, tuple[int, int, int]]:
    """Return a (char, color) for a ground cell at position (x, y).

    Row 0 (horizon): grass ^ ,, and occasional flowers *
    Rows 1+: soil ~ . or space
    """
    soil = SOIL_DAY if is_day else SOIL_NIGHT
    grass_primary = GROUND_DAY if is_day else GROUND_NIGHT
    grass_secondary = GRASS_SECONDARY_DAY if is_day else GRASS_SECONDARY_NIGHT
    flowers = FLOWER_COLORS_DAY if is_day else FLOWER_COLORS_NIGHT

    if y == 0:
        r = _pseudo_rand(x, y)
        if r < 5:
            return ("*", flowers[(x + y) % len(flowers)])
        elif r < 15:
            return (",", grass_secondary)
        else:
            return ("^", grass_primary)
    else:
        r = _pseudo_rand(x, y)
        if r < 20:
            return ("~", soil)
        elif r < 25:
            return (".", soil)
        else:
            return (" ", soil)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_static_grid(
    is_day: bool,
) -> list[list[tuple[str, tuple[int, int, int]]]]:
    """Build the full 80x30 character grid.

    Layering order (back to front):
    1. Sky fill
    2. Stars / sun / moon (handled by AnimationController)
    3. House centred
    4. Tree left of house
    5. Mailbox left of tree
    6. Fence right of house
    7. Pine tree far right
    8. Ground rows (bottom GROUND_HEIGHT)
    9. HUD background (bottom 2 rows)
    """
    sky = SKY_DAY if is_day else SKY_NIGHT

    # 1. Initialise grid — all sky
    grid: list[list[tuple[str, tuple[int, int, int]]]] = [
        [(" ", sky) for _ in range(COLS)] for _ in range(ROWS)
    ]

    ground_y = ROWS - GROUND_HEIGHT

    # 2. House — positioned so visible area fits with room for decorations
    house_x = 6
    house_y = ground_y - HOUSE_HEIGHT
    _overlay_house(grid, house_x, house_y, is_day)

    # 3. Tree — left edge, overlaps with house whitespace harmlessly
    tree_x = 0
    tree_y = ground_y - len(TREE)
    overlay_art(grid, TREE, tree_x, tree_y,
                TREE_FOLIAGE_DAY if is_day else TREE_FOLIAGE_NIGHT,
                trunk_color=TREE_TRUNK)

    # 4. Mailbox — between tree and house visible area
    mailbox_x = 16
    mailbox_y = ground_y - len(MAILBOX)
    overlay_art(grid, MAILBOX, mailbox_x, mailbox_y,
                MAILBOX_DAY if is_day else MAILBOX_NIGHT)

    # 5. Fence — right of house
    fence_x = 68
    fence_y = ground_y - len(FENCE)
    overlay_art(grid, FENCE, fence_x, fence_y,
                FENCE_DAY if is_day else FENCE_NIGHT)

    # 7. Ground (bottom GROUND_HEIGHT rows)
    for row_offset in range(GROUND_HEIGHT):
        gy = ground_y + row_offset
        for col_idx in range(COLS):
            grid[gy][col_idx] = _ground_cell(col_idx, row_offset, is_day)

    # 8. HUD background (bottom 2 rows)
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
    color: tuple[int, int, int],
    trunk_color: tuple[int, int, int] | None = None,
) -> None:
    """Overlay multi-line ASCII art onto *grid*.

    Parameters
    ----------
    art: List of strings, one per row.
    x, y: Top-left position on the grid.
    color: Default color for all non-space characters.
    trunk_color: If given, '_' and '|' characters use this color instead.
    """
    for row_idx, line in enumerate(art):
        gy = y + row_idx
        if not (0 <= gy < ROWS):
            continue
        for col_idx, ch in enumerate(line):
            gx = x + col_idx
            if not (0 <= gx < COLS):
                continue
            if ch == " ":
                continue
            c = color
            if trunk_color is not None and ch in ("_", "|"):
                c = trunk_color
            grid[gy][gx] = (ch, c)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _overlay_house(
    grid: list[list[tuple[str, tuple[int, int, int]]]],
    x: int,
    y: int,
    is_day: bool,
) -> None:
    """Render the house with per-character coloring matching weathr's style."""
    roof = ROOF_DAY if is_day else ROOF_NIGHT
    wood = WOOD_DAY if is_day else WOOD_NIGHT
    door_c = DOOR_DAY if is_day else DOOR_NIGHT
    window = WINDOW_DAY if is_day else WINDOW_NIGHT

    for row_idx, line in enumerate(HOUSE):
        gy = y + row_idx
        if not (0 <= gy < ROWS):
            continue
        for col_idx, ch in enumerate(line):
            gx = x + col_idx
            if not (0 <= gx < COLS):
                continue
            if ch == " ":
                continue

            if row_idx <= 4:
                # roof rows (0-4)
                color = roof
            elif ch in _HOUSE_WINDOW_CHARS:
                color = window
            elif ch in _HOUSE_DOOR_CHARS:
                color = door_c
            elif ch in _HOUSE_TRIM_CHARS:
                color = TRIM
            elif ch == "=":
                # ground-level trim
                color = TRIM
            elif ch == "^":
                # grass row under house
                color = GROUND_DAY if is_day else GROUND_NIGHT
            else:
                color = wood

            grid[gy][gx] = (ch, color)
