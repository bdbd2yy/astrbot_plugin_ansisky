from PIL import Image, ImageDraw, ImageFont

CELL_W = 8
CELL_H = 15
CANVAS_W = 100 * CELL_W   # 800
CANVAS_H = 36 * CELL_H    # 540


def load_font(size: int = 13) -> ImageFont.FreeTypeFont:
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
    spaces leave the black canvas background showing through.
    Returns an RGB PIL Image sized CANVAS_W x CANVAS_H.
    """
    font = load_font(13)
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    for row_idx, row in enumerate(grid):
        y = row_idx * CELL_H
        for col_idx, cell in enumerate(row):
            x = col_idx * CELL_W
            char, color = cell
            if char != " ":
                draw.text((x, y - 2), char, font=font, fill=color)

    return img
