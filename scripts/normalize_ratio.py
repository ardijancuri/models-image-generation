#!/usr/bin/env python3
"""Verify or explicitly transform fashion studio images for 3:4 delivery."""

from __future__ import annotations

import argparse
import json
import math
import shutil
from pathlib import Path
from typing import Any

from PIL import Image, ImageColor, ImageOps, ImageStat


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
TARGET_W = 3
TARGET_H = 4
TARGET_RATIO = TARGET_W / TARGET_H
RATIO_TOLERANCE = 0.02
WHITE_MEAN_THRESHOLD = 248.0
WHITE_STDDEV_THRESHOLD = 3.0
BAND_FRACTION = 0.10


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def manifest_images(manifest_path: Path, images_dir: Path) -> list[Path]:
    manifest = load_manifest(manifest_path)
    paths: list[Path] = []
    for entry in manifest.get("entries", []):
        raw = entry.get("output_path")
        if not raw:
            continue
        candidate = Path(raw)
        if not candidate.exists():
            candidate = images_dir / Path(raw).name
        if candidate.exists() and candidate.suffix.lower() in IMAGE_EXTENSIONS:
            paths.append(candidate)
    return paths


def directory_images(images_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in images_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def normalize_with_padding(img: Image.Image, fill: tuple[int, int, int]) -> Image.Image:
    width, height = img.size
    if width * TARGET_H == height * TARGET_W:
        return img.copy()
    scale = math.ceil(max(width / TARGET_W, height / TARGET_H))
    new_width = TARGET_W * scale
    new_height = TARGET_H * scale
    canvas = Image.new("RGB", (new_width, new_height), fill)
    x = (new_width - width) // 2
    y = (new_height - height) // 2
    canvas.paste(img.convert("RGB"), (x, y))
    return canvas


def normalize_with_crop(img: Image.Image) -> Image.Image:
    width, height = img.size
    if width * TARGET_H == height * TARGET_W:
        return img.copy()
    scale = math.floor(min(width / TARGET_W, height / TARGET_H))
    if scale < 1:
        raise ValueError(f"Image is too small to crop to 3:4: {width}x{height}")
    new_width = TARGET_W * scale
    new_height = TARGET_H * scale
    left = (width - new_width) // 2
    top = (height - new_height) // 2
    box = (left, top, left + new_width, top + new_height)
    return img.crop(box)


def is_near_3x4(img: Image.Image) -> bool:
    return abs((img.width / img.height) - TARGET_RATIO) <= RATIO_TOLERANCE


def is_uniform_white(crop: Image.Image) -> bool:
    stat = ImageStat.Stat(crop)
    mean = sum(stat.mean) / 3
    max_stddev = max(stat.stddev)
    return mean >= WHITE_MEAN_THRESHOLD and max_stddev <= WHITE_STDDEV_THRESHOLD


def has_letterbox_or_padding(img: Image.Image) -> bool:
    rgb = ImageOps.exif_transpose(img).convert("RGB")
    width, height = rgb.size
    horizontal_band = max(8, int(height * BAND_FRACTION))
    vertical_band = max(8, int(width * BAND_FRACTION))

    top = rgb.crop((0, 0, width, horizontal_band))
    top_inner = rgb.crop((0, horizontal_band, width, min(height, horizontal_band * 2)))
    bottom = rgb.crop((0, height - horizontal_band, width, height))
    bottom_inner = rgb.crop((0, max(0, height - horizontal_band * 2), width, height - horizontal_band))
    left = rgb.crop((0, 0, vertical_band, height))
    left_inner = rgb.crop((vertical_band, 0, min(width, vertical_band * 2), height))
    right = rgb.crop((width - vertical_band, 0, width, height))
    right_inner = rgb.crop((max(0, width - vertical_band * 2), 0, width - vertical_band, height))

    horizontal_padding = (
        (is_uniform_white(top) and not is_uniform_white(top_inner))
        or (is_uniform_white(bottom) and not is_uniform_white(bottom_inner))
        or (is_uniform_white(top) and is_uniform_white(bottom))
    )
    vertical_padding = (
        (is_uniform_white(left) and not is_uniform_white(left_inner))
        or (is_uniform_white(right) and not is_uniform_white(right_inner))
        or (is_uniform_white(left) and is_uniform_white(right) and not (is_uniform_white(left_inner) and is_uniform_white(right_inner)))
    )
    return horizontal_padding or vertical_padding


def verify_image(path: Path, out_dir: Path) -> dict[str, Any]:
    with Image.open(path) as src:
        img = ImageOps.exif_transpose(src).convert("RGB")
        warnings: list[str] = []
        if not is_near_3x4(img):
            warnings.append("not_3x4_aspect_ratio")
        if has_letterbox_or_padding(img):
            warnings.append("letterboxed_or_padded_canvas")

        result: dict[str, Any] = {
            "source": str(path),
            "output": None,
            "mode": "verify",
            "original": {"width": img.width, "height": img.height},
            "aspect_ratio": round(img.width / img.height, 4),
            "status": "regenerate_required" if warnings else "copied",
            "warnings": warnings,
        }
        if warnings:
            return result

        output_path = out_dir / path.name
        if path.resolve() != output_path.resolve():
            shutil.copy2(path, output_path)
        result["output"] = str(output_path)
        return result


def normalize_image(path: Path, out_dir: Path, mode: str, fill: tuple[int, int, int]) -> dict[str, Any]:
    if mode == "verify":
        return verify_image(path, out_dir)

    with Image.open(path) as src:
        img = ImageOps.exif_transpose(src).convert("RGB")
        original = {"width": img.width, "height": img.height}
        if mode == "crop":
            normalized = normalize_with_crop(img)
        else:
            normalized = normalize_with_padding(img, fill)
        output_path = out_dir / f"{path.stem}_3x4.png"
        normalized.save(output_path)
        return {
            "source": str(path),
            "output": str(output_path),
            "mode": mode,
            "original": original,
            "normalized": {"width": normalized.width, "height": normalized.height},
            "aspect_ratio": "3:4",
            "status": "transformed",
            "warnings": ["pad_mode_explicit_fallback_not_recommended_for_website"] if mode == "pad" else [],
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--images-dir", required=True, help="Directory containing generated images")
    parser.add_argument("--out-dir", required=True, help="Directory for verified or transformed output copies")
    parser.add_argument("--manifest", help="Optional manifest JSON to choose images from")
    parser.add_argument(
        "--mode",
        choices=["verify", "crop", "pad"],
        default="verify",
        help="Default verify copies only native usable 3:4 images; crop and pad are explicit manual fallbacks",
    )
    parser.add_argument("--background", default="#ffffff", help="Padding color, default #ffffff")
    parser.add_argument("--report", help="Optional JSON report path")
    args = parser.parse_args()

    images_dir = Path(args.images_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    fill = ImageColor.getrgb(args.background)

    images = manifest_images(Path(args.manifest), images_dir) if args.manifest else directory_images(images_dir)
    results = [normalize_image(path, out_dir, args.mode, fill) for path in images]

    report = {
        "target_aspect_ratio": "3:4",
        "mode": args.mode,
        "count": len(results),
        "copied": sum(1 for item in results if item.get("status") == "copied"),
        "regenerate_required": sum(1 for item in results if item.get("status") == "regenerate_required"),
        "results": results,
    }
    report_path = Path(args.report) if args.report else out_dir / "normalize-ratio-report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    if args.mode == "verify":
        print(f"Verified {len(results)} image(s); copied {report['copied']} native 3:4 image(s) to {out_dir}")
        if report["regenerate_required"]:
            print(f"Regenerate required for {report['regenerate_required']} image(s); no padding was added")
    else:
        print(f"Wrote {len(results)} transformed 3:4 image(s) to {out_dir}")
    print(f"Wrote report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
