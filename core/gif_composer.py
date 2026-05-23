from io import BytesIO
from pathlib import Path

from PIL import Image


def compose_gif(frames: list[Image.Image], duration_ms: int = 150) -> BytesIO:
    """Compose a list of PIL Images into an animated GIF stored in a BytesIO buffer."""
    buf = BytesIO()
    frames[0].save(
        buf,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0,
        optimize=False,
        disposal=2,
    )
    buf.seek(0)
    return buf


def save_gif(frames: list[Image.Image], path: Path, duration_ms: int = 150) -> None:
    """Save an animated GIF to a file path."""
    frames[0].save(
        str(path),
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0,
        optimize=False,
        disposal=2,
    )
