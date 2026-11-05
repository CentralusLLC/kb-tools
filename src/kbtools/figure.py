"""Curate a key graphic into the knowledge base: crop, resize, save, and print a Markdown snippet."""

from __future__ import annotations

import os
from pathlib import Path

from .common import Repo


def parse_crop(value: str | None, width: int, height: int) -> tuple[int, int, int, int] | None:
    """Crop box 'left,top,right,bottom' as fractions (all <= 1, as in slides.md) or pixels."""
    if not value:
        return None
    try:
        numbers = [float(x) for x in value.replace("[", "").replace("]", "").split(",")]
    except ValueError:
        raise SystemExit("kb: --crop must be 'left,top,right,bottom'")
    if len(numbers) != 4:
        raise SystemExit("kb: --crop needs four numbers")
    if all(0 <= n <= 1 for n in numbers):
        numbers = [numbers[0] * width, numbers[1] * height, numbers[2] * width, numbers[3] * height]
    left, top, right, bottom = (int(round(n)) for n in numbers)
    left, top = max(0, left), max(0, top)
    right, bottom = min(width, right), min(height, bottom)
    if right <= left or bottom <= top:
        raise SystemExit("kb: --crop box is empty")
    return left, top, right, bottom


def make_figure(
    repo: Repo,
    image: Path,
    out: Path,
    *,
    crop: str | None = None,
    pad: float = 0.01,
    max_width: int = 1600,
    page: Path | None = None,
    alt: str = "",
    caption: str = "",
    source_ref: str = "",
    overwrite: bool = False,
) -> str:
    from PIL import Image

    image = image if image.is_absolute() else repo.root / image
    out = out if out.is_absolute() else repo.root / out
    if not image.is_file():
        raise SystemExit(f"kb: {image} not found")
    if not out.resolve().is_relative_to(repo.docs.resolve()):
        raise SystemExit("kb: figures must be saved inside docs/ (for example next to the page in an assets/ folder)")
    if out.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise SystemExit("kb: --out must end in .png, .jpg or .webp")
    if out.exists() and not overwrite:
        raise SystemExit(f"kb: {repo.rel(out)} exists; pass --overwrite to replace it")
    with Image.open(image) as source:
        picture = source.convert("RGB")
    box = parse_crop(crop, *picture.size)
    if box:
        margin_x, margin_y = int(picture.size[0] * pad), int(picture.size[1] * pad)
        box = (max(0, box[0] - margin_x), max(0, box[1] - margin_y),
               min(picture.size[0], box[2] + margin_x), min(picture.size[1], box[3] + margin_y))
        picture = picture.crop(box)
    if picture.size[0] > max_width:
        ratio = max_width / picture.size[0]
        picture = picture.resize((max_width, int(picture.size[1] * ratio)), Image.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    options = {"optimize": True}
    if out.suffix.lower() in {".jpg", ".jpeg", ".webp"}:
        options["quality"] = 88
    picture.save(out, **options)

    target = os.path.relpath(out, (repo.root / page).parent if page else repo.docs)
    alt = alt or "TODO: describe what the figure shows"
    caption = caption or "TODO: one-sentence caption"
    source_ref = source_ref or "TODO: source file and page/slide"
    return f"""![{alt}]({target})

*Figure: {caption}* Source: {source_ref}.

| Element | What it shows |
| --- | --- |
| TODO | TODO |
"""
