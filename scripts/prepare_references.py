#!/usr/bin/env python3
"""Inspect fashion product reference images and write a reference manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageOps
except Exception:  # pragma: no cover - dependency guard
    Image = None
    ImageOps = None


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def source_path(item: Any) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return str(item.get("path", ""))
    return ""


def source_role(item: Any, brief: dict[str, Any], path_value: str) -> str:
    if isinstance(item, dict) and item.get("role"):
        return str(item["role"])
    for role, paths in brief.get("reference_roles", {}).items():
        if path_value in paths:
            return str(role)
    if path_value == brief.get("primary_reference"):
        return "primary"
    return "reference"


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def image_info(path: Path) -> dict[str, Any]:
    info: dict[str, Any] = {
        "exists": path.exists(),
        "sha256": None,
        "width": None,
        "height": None,
        "mode": None,
        "format": None,
        "quality_flags": [],
    }
    if not path.exists():
        info["quality_flags"].append("missing_file")
        return info
    if path.suffix.lower() not in IMAGE_EXTENSIONS:
        info["quality_flags"].append("unsupported_extension")
    info["sha256"] = file_hash(path)
    if Image is None:
        info["quality_flags"].append("pillow_not_available_dimensions_not_checked")
        return info
    try:
        with Image.open(path) as img:
            img = ImageOps.exif_transpose(img)
            info.update(
                {
                    "width": img.width,
                    "height": img.height,
                    "mode": img.mode,
                    "format": img.format,
                }
            )
            if min(img.width, img.height) < 512:
                info["quality_flags"].append("low_resolution")
            if img.mode not in {"RGB", "RGBA"}:
                info["quality_flags"].append("non_rgb_mode")
    except Exception as exc:
        info["quality_flags"].append(f"image_read_error:{exc}")
    return info


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief", required=True, help="Path to brief.json")
    parser.add_argument("--out", required=True, help="Path to write reference manifest JSON")
    args = parser.parse_args()

    brief_path = Path(args.brief)
    brief = load_json(brief_path)
    base_dir = brief_path.parent
    entries = []

    for item in brief.get("source_images", []):
        raw_path = source_path(item)
        if not raw_path:
            continue
        resolved = Path(raw_path)
        if not resolved.is_absolute():
            resolved = base_dir / resolved
        info = image_info(resolved)
        entries.append(
            {
                "source": raw_path,
                "resolved_path": str(resolved),
                "role": source_role(item, brief, raw_path),
                **info,
            }
        )

    warnings = []
    if not entries:
        warnings.append("no_source_images_listed")
    if brief.get("primary_reference") and not any(e["source"] == brief["primary_reference"] for e in entries):
        warnings.append("primary_reference_not_in_source_images")
    if not brief.get("primary_reference"):
        warnings.append("missing_primary_reference")

    output = {
        "product_id": brief.get("product_id", ""),
        "product_name": brief.get("product_name", ""),
        "source_count": len(entries),
        "references": entries,
        "warnings": warnings,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote reference manifest: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
