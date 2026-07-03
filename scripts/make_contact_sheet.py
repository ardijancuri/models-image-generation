#!/usr/bin/env python3
"""Create a PNG contact sheet from a fashion studio image manifest."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def resolve_image(entry: dict[str, Any], images_dir: Path) -> Path | None:
    output_path = entry.get("output_path")
    if output_path:
        candidate = Path(output_path)
        if candidate.exists():
            return candidate
        candidate = images_dir / Path(output_path).name
        if candidate.exists():
            return candidate
    return None


def draw_wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, width: int, fill: str) -> int:
    font = ImageFont.load_default()
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    x, y = xy
    for line in lines[:4]:
        draw.text((x, y), line, fill=fill, font=font)
        y += 16
    return y


def placeholder(tile_size: tuple[int, int], label: str) -> Image.Image:
    tile = Image.new("RGB", tile_size, "white")
    draw = ImageDraw.Draw(tile)
    draw.rectangle((0, 0, tile_size[0] - 1, tile_size[1] - 1), outline="#d1d5db", width=2)
    draw_wrapped(draw, (18, 40), label, tile_size[0] - 36, "#4b5563")
    return tile


def make_tile(entry: dict[str, Any], images_dir: Path, tile_w: int, tile_h: int) -> Image.Image:
    label_h = 96
    image_h = tile_h - label_h
    tile = Image.new("RGB", (tile_w, tile_h), "white")
    draw = ImageDraw.Draw(tile)
    draw.rectangle((0, 0, tile_w - 1, tile_h - 1), outline="#e5e7eb")

    image_path = resolve_image(entry, images_dir)
    if image_path:
        try:
            with Image.open(image_path) as img:
                img = ImageOps.exif_transpose(img).convert("RGB")
                img.thumbnail((tile_w - 24, image_h - 24))
                x = (tile_w - img.width) // 2
                y = 12 + (image_h - 24 - img.height) // 2
                tile.paste(img, (x, y))
        except Exception as exc:
            tile.paste(placeholder((tile_w - 24, image_h - 24), f"Image read error: {exc}"), (12, 12))
    else:
        tile.paste(placeholder((tile_w - 24, image_h - 24), "Missing generated image"), (12, 12))

    status = entry.get("review_status", "pending_review")
    marker = "internal " if not entry.get("deliverable", True) else ""
    title = f"{marker}{entry.get('prompt_id', '')} {entry.get('shot', '')}".strip()
    warnings = ", ".join(entry.get("qa_warnings", [])[:2])
    draw.text((12, image_h + 10), title[:58], fill="#111827", font=ImageFont.load_default())
    draw.text((12, image_h + 30), f"status: {status}", fill="#374151", font=ImageFont.load_default())
    if warnings:
        draw_wrapped(draw, (12, image_h + 50), f"warnings: {warnings}", tile_w - 24, "#b45309")
    return tile


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, help="Path to manifest JSON")
    parser.add_argument("--images-dir", required=True, help="Directory containing generated images")
    parser.add_argument("--out", required=True, help="Path to write contact sheet PNG")
    parser.add_argument("--columns", type=int, default=3, help="Number of columns")
    parser.add_argument("--include-internal", action="store_true", help="Include non-deliverable internal anchor images")
    args = parser.parse_args()

    manifest = load_json(Path(args.manifest))
    entries = [
        entry
        for entry in manifest.get("entries", [])
        if args.include_internal or entry.get("deliverable", True)
    ]
    if not entries:
        entries = [{"prompt_id": "empty", "shot": "no entries", "review_status": "warn_review", "qa_warnings": ["manifest_has_no_entries"]}]

    columns = max(1, args.columns)
    tile_w, tile_h = 420, 560
    rows = math.ceil(len(entries) / columns)
    sheet = Image.new("RGB", (columns * tile_w, rows * tile_h), "white")
    images_dir = Path(args.images_dir)

    for index, entry in enumerate(entries):
        tile = make_tile(entry, images_dir, tile_w, tile_h)
        x = (index % columns) * tile_w
        y = (index // columns) * tile_h
        sheet.paste(tile, (x, y))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)
    print(f"Wrote contact sheet: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
