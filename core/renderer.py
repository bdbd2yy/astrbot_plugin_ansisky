from PIL import Image, ImageDraw, ImageFont

CELL_W = 7
CELL_H = 12
CANVAS_W = 114 * CELL_W   # 798
CANVAS_H = 45 * CELL_H    # 540


def load_font(size: int = 11) -> ImageFont.FreeTypeFont:
    """Load a monospace font, trying common paths. Falls back to default."""
    font_paths = [
        "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/TTF/JetBrainsMono-Regular.ttf",
        "/usr/share/fonts/TTF/FiraCode-Regular.ttf",
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def render_frame(grid: list[list[tuple[str, tuple[int, int, int]]]]) -> Image.Image:
    """Render a single frame from a character+color grid.

    Each cell is (char, (r, g, b)).  Only non-space characters are drawn;
    spaces leave the grid-provided canvas background showing through.
    """
    font = load_font(11)
    background = grid[0][0][1] if grid and grid[0] else (26, 25, 26)
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), background)
    draw = ImageDraw.Draw(img)

    for row_idx, row in enumerate(grid):
        y = row_idx * CELL_H
        for col_idx, cell in enumerate(row):
            x = col_idx * CELL_W
            char, color = cell
            if char != " ":
                draw.text((x, y - 1), char, font=font, fill=color)

    return img
