#!/usr/bin/env python3
"""Estimate prompt-text tokens and runtime for a fashion image generation run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def prompt_chars(item: dict[str, Any]) -> int:
    return len(str(item.get("prompt", "")))


def token_estimate(chars: int) -> int:
    return round(chars / 4)


def minutes_range(image_calls: int, min_seconds: int, max_seconds: int, setup_minutes: int, review_minutes: int) -> dict[str, float]:
    return {
        "min": round(setup_minutes + review_minutes + (image_calls * min_seconds / 60), 1),
        "max": round(setup_minutes + review_minutes + (image_calls * max_seconds / 60), 1),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-pack", required=True, help="Path to prompt-pack JSON")
    parser.add_argument("--out", help="Optional JSON output path")
    parser.add_argument("--image-seconds-min", type=int, default=60, help="Optimistic seconds per image call")
    parser.add_argument("--image-seconds-max", type=int, default=120, help="Conservative seconds per image call")
    parser.add_argument("--setup-minutes", type=int, default=2, help="Expected orchestration/setup minutes")
    parser.add_argument("--review-minutes", type=int, default=3, help="Expected validation/review minutes")
    parser.add_argument("--regen-count", type=int, default=1, help="Likely number of regeneration calls for overhead estimate")
    args = parser.parse_args()

    prompt_pack_path = Path(args.prompt_pack)
    prompt_pack = load_json(prompt_pack_path)
    items = prompt_pack.get("items", [])
    deliverables = [item for item in items if item.get("deliverable", True)]
    internal = [item for item in items if not item.get("deliverable", True)]
    face_visible = [item for item in items if item.get("face_visible", False)]

    per_item = [
        {
            "id": item.get("id", ""),
            "shot": item.get("shot", ""),
            "deliverable": bool(item.get("deliverable", True)),
            "face_visible": bool(item.get("face_visible", False)),
            "prompt_chars": prompt_chars(item),
            "estimated_prompt_tokens": token_estimate(prompt_chars(item)),
        }
        for item in items
    ]
    total_chars = sum(item["prompt_chars"] for item in per_item)
    total_tokens = token_estimate(total_chars)
    no_regen = minutes_range(
        len(items),
        args.image_seconds_min,
        args.image_seconds_max,
        args.setup_minutes,
        args.review_minutes,
    )
    with_regen = minutes_range(
        len(items) + max(0, args.regen_count),
        args.image_seconds_min,
        args.image_seconds_max,
        args.setup_minutes,
        args.review_minutes,
    )

    output = {
        "product_id": prompt_pack.get("product_id", ""),
        "product_name": prompt_pack.get("product_name", ""),
        "prompt_pack": str(prompt_pack_path),
        "image_calls_planned": len(items),
        "deliverable_count": len(deliverables),
        "internal_count": len(internal),
        "face_visible_deliverable_count": sum(1 for item in face_visible if item.get("deliverable", True)),
        "prompt_text": {
            "chars": total_chars,
            "estimated_tokens_chars_div_4": total_tokens,
            "method": "rough prompt-text estimate using characters / 4; built-in image generation billing internals are not exposed",
        },
        "time_estimate_minutes": {
            "no_regeneration": no_regen,
            "with_likely_regeneration": with_regen,
            "assumptions": {
                "seconds_per_image_call": [args.image_seconds_min, args.image_seconds_max],
                "setup_minutes": args.setup_minutes,
                "review_minutes": args.review_minutes,
                "regen_count": max(0, args.regen_count),
            },
        },
        "workflow_notes": [
            "Generate only the deliverable no-face PDP shots; no internal model identity sheet is used.",
            "Keep every generated image free of recognizable model faces, including eyes, nose, mouth, full face, and facial profile.",
            "Use partial head/hair crops only when needed for natural on-model product framing.",
            "Use normalize_ratio.py --mode verify; regenerate failures instead of padding.",
        ],
        "items": per_item,
    }

    rendered = json.dumps(output, indent=2)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered, encoding="utf-8")
        print(f"Wrote estimate: {out_path}")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
