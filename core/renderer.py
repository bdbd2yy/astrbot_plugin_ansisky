from PIL import Image, ImageDraw, ImageFont

CELL_W = 10
CELL_H = 18
CANVAS_W = 80 * CELL_W   # 800
CANVAS_H = 30 * CELL_H   # 540


def load_font(size: int = 16) -> ImageFont.FreeTypeFont:
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

    Each cell is (char, (r, g, b)) or (char, color_tuple).
    Returns an RGB PIL Image sized CANVAS_W × CANVAS_H.
    """
    font = load_font(14)
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    for row_idx, row in enumerate(grid):
        y = row_idx * CELL_H
        for col_idx, cell in enumerate(row):
            x = col_idx * CELL_W
            char, color = cell
            if char == " ":
                # Draw background rect for spaces (sky/ground fill)
                draw.rectangle(
                    [x, y, x + CELL_W - 1, y + CELL_H - 1],
                    fill=color,
                )
            else:
                draw.text((x, y - 2), char, font=font, fill=color)

    return img
