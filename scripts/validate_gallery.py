#!/usr/bin/env python3
"""Run lightweight validation checks for a generated fashion studio gallery."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps, ImageStat


TARGET_RATIO = 3 / 4
RATIO_TOLERANCE = 0.02
WHITE_MEAN_THRESHOLD = 248.0
WHITE_STDDEV_THRESHOLD = 3.0
BAND_FRACTION = 0.10
FAIL_REGENERATE_WARNINGS = {
    "missing_generated_image",
    "not_3x4_aspect_ratio",
    "letterboxed_or_padded_canvas",
}


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


def border_whiteness(img: Image.Image) -> float:
    rgb = ImageOps.exif_transpose(img).convert("RGB")
    w, h = rgb.size
    band = max(4, min(w, h) // 40)
    crops = [
        rgb.crop((0, 0, w, band)),
        rgb.crop((0, h - band, w, h)),
        rgb.crop((0, 0, band, h)),
        rgb.crop((w - band, 0, w, h)),
    ]
    total = 0.0
    count = 0
    for crop in crops:
        stat = ImageStat.Stat(crop)
        total += sum(stat.sum) / 3
        count += crop.width * crop.height
    return total / count if count else 0.0


def is_uniform_white(crop: Image.Image) -> bool:
    stat = ImageStat.Stat(crop)
    mean = sum(stat.mean) / 3
    max_stddev = max(stat.stddev)
    return mean >= WHITE_MEAN_THRESHOLD and max_stddev <= WHITE_STDDEV_THRESHOLD


def has_letterbox_or_padding(img: Image.Image) -> bool:
    rgb = ImageOps.exif_transpose(img).convert("RGB")
    w, h = rgb.size
    horizontal_band = max(8, int(h * BAND_FRACTION))
    vertical_band = max(8, int(w * BAND_FRACTION))
    top = rgb.crop((0, 0, w, horizontal_band))
    top_inner = rgb.crop((0, horizontal_band, w, min(h, horizontal_band * 2)))
    bottom = rgb.crop((0, h - horizontal_band, w, h))
    bottom_inner = rgb.crop((0, max(0, h - horizontal_band * 2), w, h - horizontal_band))
    left = rgb.crop((0, 0, vertical_band, h))
    left_inner = rgb.crop((vertical_band, 0, min(w, vertical_band * 2), h))
    right = rgb.crop((w - vertical_band, 0, w, h))
    right_inner = rgb.crop((max(0, w - vertical_band * 2), 0, w - vertical_band, h))

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


def validate_entry(entry: dict[str, Any], images_dir: Path) -> dict[str, Any]:
    warnings = list(entry.get("qa_warnings", []))
    image_path = resolve_image(entry, images_dir)
    dimensions = None

    if image_path is None:
        warnings.append("missing_generated_image")
        return {
            "prompt_id": entry.get("prompt_id", ""),
            "shot": entry.get("shot", ""),
            "status": "fail_regenerate",
            "image_path": None,
            "dimensions": dimensions,
            "warnings": sorted(set(warnings)),
        }

    try:
        with Image.open(image_path) as img:
            img = ImageOps.exif_transpose(img)
            actual_ratio = img.width / img.height
            dimensions = {"width": img.width, "height": img.height, "aspect_ratio": round(actual_ratio, 4)}
            if min(img.width, img.height) < 768:
                warnings.append("low_resolution_output")
            if abs(actual_ratio - TARGET_RATIO) > RATIO_TOLERANCE:
                warnings.append("not_3x4_aspect_ratio")
            if "detail" not in entry.get("shot", ""):
                whiteness = border_whiteness(img)
                if whiteness < 235:
                    warnings.append("border_not_white_studio_background")
            if has_letterbox_or_padding(img):
                warnings.append("letterboxed_or_padded_canvas")
            if "detail" not in entry.get("shot", "") and img.height < img.width:
                warnings.append("non_detail_shot_is_landscape_review_crop")
    except Exception as exc:
        warnings.append(f"image_read_error:{exc}")

    if entry.get("inferred"):
        warnings.append("view_inferred_requires_manual_review")

    status = "pass" if not warnings else "warn_review"
    if any(w in FAIL_REGENERATE_WARNINGS for w in warnings) or any(
        w.startswith("image_read_error") for w in warnings
    ):
        status = "fail_regenerate"
    if entry.get("inferred") and entry.get("shot") in {"back-on-model", "side-on-model"}:
        status = "fail_reference_needed"

    return {
        "prompt_id": entry.get("prompt_id", ""),
        "shot": entry.get("shot", ""),
        "status": status,
        "image_path": str(image_path),
        "dimensions": dimensions,
        "warnings": sorted(set(warnings)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, help="Path to manifest JSON")
    parser.add_argument("--images-dir", required=True, help="Directory containing generated images")
    parser.add_argument("--out", required=True, help="Path to write validation report JSON")
    args = parser.parse_args()

    manifest = load_json(Path(args.manifest))
    images_dir = Path(args.images_dir)
    results = [validate_entry(entry, images_dir) for entry in manifest.get("entries", [])]

    if not results:
        results.append(
            {
                "prompt_id": "",
                "shot": "",
                "status": "fail_regenerate",
                "image_path": None,
                "dimensions": None,
                "warnings": ["manifest_has_no_entries"],
            }
        )

    statuses = {item["status"] for item in results}
    summary_status = "pass"
    if "fail_regenerate" in statuses or "fail_reference_needed" in statuses:
        summary_status = "fail"
    elif "warn_review" in statuses:
        summary_status = "warn_review"

    output = {
        "product_id": manifest.get("product_id", ""),
        "product_name": manifest.get("product_name", ""),
        "status": summary_status,
        "results": results,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote validation report: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
