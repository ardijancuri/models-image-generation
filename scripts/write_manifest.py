#!/usr/bin/env python3
"""Write a generation manifest from a prompt pack and generated image folder."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def image_candidates(images_dir: Path) -> list[Path]:
    if not images_dir.exists():
        return []
    return sorted([p for p in images_dir.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS])


def match_image(images: list[Path], prompt_id: str, shot: str) -> Path | None:
    prompt_key = prompt_id.lower()
    shot_key = shot.lower()
    for image in images:
        name = image.stem.lower()
        if prompt_key in name or shot_key in name:
            return image
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-pack", required=True, help="Path to prompt-pack JSON")
    parser.add_argument("--images-dir", required=True, help="Directory containing generated images")
    parser.add_argument("--out", required=True, help="Path to write manifest JSON")
    args = parser.parse_args()

    prompt_pack_path = Path(args.prompt_pack)
    prompt_pack = load_json(prompt_pack_path)
    images_dir = Path(args.images_dir)
    images = image_candidates(images_dir)

    entries = []
    manifest_warnings = []
    if not images:
        manifest_warnings.append("no_generated_images_found")

    for item in prompt_pack.get("items", []):
        matched = match_image(images, item.get("id", ""), item.get("shot", ""))
        warnings = list(item.get("warnings", []))
        status = "warn_review" if warnings else "pending_review"
        if matched is None:
            warnings.append("missing_generated_image")
            status = "fail_regenerate"
        entries.append(
            {
                "prompt_id": item.get("id", ""),
                "shot": item.get("shot", ""),
                "deliverable": bool(item.get("deliverable", True)),
                "face_visible": bool(item.get("face_visible", False)),
                "requires_model_identity_anchor": bool(item.get("requires_model_identity_anchor", False)),
                "output_path": str(matched) if matched else None,
                "prompt": item.get("prompt", ""),
                "negative_constraints": item.get("negative_constraints", []),
                "reference_roles": item.get("reference_roles", []),
                "qa_checks": item.get("qa_checks", []),
                "model_appearance": item.get("model_appearance", ""),
                "model_realism": item.get("model_realism", ""),
                "model_styling": item.get("model_styling", ""),
                "model_consistency": item.get("model_consistency", ""),
                "inferred": bool(item.get("inferred", False)),
                "review_status": status,
                "qa_warnings": warnings,
                "selected": False,
                "rejected": False,
                "review_notes": "",
            }
        )

    output = {
        "product_id": prompt_pack.get("product_id", ""),
        "product_name": prompt_pack.get("product_name", ""),
        "brief_hash": prompt_pack.get("brief_hash", ""),
        "source_images": prompt_pack.get("source_images", []),
        "deliverable_count": sum(1 for entry in entries if entry.get("deliverable", True)),
        "internal_count": sum(1 for entry in entries if not entry.get("deliverable", True)),
        "model_appearance": prompt_pack.get("model_appearance", ""),
        "model_realism": prompt_pack.get("model_realism", ""),
        "model_styling": prompt_pack.get("model_styling", ""),
        "model_consistency": prompt_pack.get("model_consistency", ""),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "output_dir": str(images_dir),
        "entries": entries,
        "review_summary": {
            "status": "warn_review" if manifest_warnings or any(e["qa_warnings"] for e in entries) else "pending_review",
            "warnings": manifest_warnings,
        },
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote manifest: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
