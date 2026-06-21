#!/usr/bin/env python3
"""Build a prompt pack for fashion studio image generation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


DEFAULT_SHOTS = [
    "main-front-on-model",
    "front-3q-on-model",
    "back-on-model",
    "side-on-model",
    "detail-fabric",
    "detail-feature",
]

DEFAULT_ASPECT_RATIO = "3:4"

SHOT_INSTRUCTIONS = {
    "main-front-on-model": "Front-facing full-body ecommerce PDP main image. Product centered, full head/face/hair, full garment, and hem visible in a native 3:4 frame.",
    "front-3q-on-model": "Slight three-quarter front angle showing garment depth, drape, side seam, and silhouette, with full head/face/hair and hem visible.",
    "back-on-model": "Back-facing studio image with full head/hair, full garment, and hem visible. Do not invent back closures, labels, straps, or decoration if references do not show them.",
    "side-on-model": "Side-view studio image preserving hem length, sleeve shape, drape, and garment volume, with full head/face/hair and hem visible.",
    "detail-fabric": "Close crop of the actual garment fabric texture, weave, lace, knit, sheen, print, embroidery, or surface finish, filling the vertical 3:4 frame naturally.",
    "detail-feature": "Close crop of a buying-confidence detail such as neckline, sleeve cuff, zipper, button, pocket, seam, hem, strap, lining, trim, hardware, or logo patch, filling the vertical 3:4 frame naturally.",
}

SHOT_REFERENCE_ROLES = {
    "main-front-on-model": ["primary", "front", "color"],
    "front-3q-on-model": ["primary", "front", "side", "color"],
    "back-on-model": ["primary", "back", "color"],
    "side-on-model": ["primary", "side", "front", "color"],
    "detail-fabric": ["primary", "detail", "texture", "color"],
    "detail-feature": ["primary", "detail", "label", "texture"],
}

SHOT_QA = {
    "main-front-on-model": ["full garment visible", "works as first PDP image", "white studio background"],
    "front-3q-on-model": ["same garment identity", "useful angle variation", "no silhouette drift"],
    "back-on-model": ["back details supported or flagged inferred", "no invented closures", "white studio background"],
    "side-on-model": ["side details supported or flagged inferred", "hem and drape preserved", "white studio background"],
    "detail-fabric": ["sharp texture", "actual fabric matches reference", "no generic substitute material"],
    "detail-feature": ["feature is product-specific", "no invented label or hardware", "sharp crop"],
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def brief_hash(brief_path: Path) -> str:
    data = brief_path.read_bytes()
    return hashlib.sha256(data).hexdigest()


def normalize_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    return [str(value)]


def identity_capsule(brief: dict[str, Any]) -> str:
    identity = brief.get("garment_identity", {})
    if isinstance(identity, str):
        return identity
    if not isinstance(identity, dict):
        identity = {}
    fields = [
        ("category", identity.get("category") or brief.get("category")),
        ("silhouette", identity.get("silhouette")),
        ("color", identity.get("color")),
        ("fabric", identity.get("fabric")),
        ("neckline", identity.get("neckline")),
        ("sleeves", identity.get("sleeves")),
        ("closures", identity.get("closures")),
        ("seams", identity.get("seams")),
        ("print/logo", identity.get("print_or_logo")),
        ("trim/hardware", identity.get("trim_or_hardware")),
    ]
    parts = [f"{label}: {value}" for label, value in fields if value]
    landmarks = normalize_list(identity.get("identity_landmarks"))
    if landmarks:
        parts.append("identity landmarks: " + "; ".join(landmarks))
    uncertainties = normalize_list(identity.get("uncertainties"))
    if uncertainties:
        parts.append("uncertainties: " + "; ".join(uncertainties))
    return "; ".join(parts) if parts else "identity not yet summarized from references"


def role_has_reference(brief: dict[str, Any], role: str) -> bool:
    roles = brief.get("reference_roles", {})
    values = roles.get(role, []) if isinstance(roles, dict) else []
    return bool(values)


def shot_is_inferred(brief: dict[str, Any], shot: str) -> bool:
    if shot == "back-on-model":
        return not role_has_reference(brief, "back")
    if shot == "side-on-model":
        return not role_has_reference(brief, "side")
    return False


def shot_framing_rule(shot: str) -> str:
    if shot.startswith("detail-"):
        return (
            "Detail framing: the garment detail fills the vertical 3:4 frame naturally, "
            "with no huge empty top, bottom, or side bands and no square image placed inside a portrait canvas."
        )
    return (
        "Full-body framing: full head/face/hair, shoulders, full garment, and full hem must be visible inside the 3:4 frame. "
        "The model and product should fill the canvas naturally for ecommerce without cropped face/head or cropped hem."
    )


def build_prompt(brief: dict[str, Any], shot: str, inferred: bool) -> str:
    must_preserve = normalize_list(brief.get("must_preserve"))
    avoid = normalize_list(brief.get("avoid"))
    background = brief.get("background") or "seamless pure white studio background"
    model_direction = brief.get("model_direction") or "adult generic model, visible natural ecommerce face allowed, neutral expression, do not preserve the reference model identity"
    preserve_line = "; ".join(must_preserve) if must_preserve else "all visible garment identity details from the references"
    garment_identity = brief.get("garment_identity", {})
    landmarks = normalize_list(garment_identity.get("identity_landmarks") if isinstance(garment_identity, dict) else None)
    landmarks_line = "; ".join(landmarks) if landmarks else "none listed; manually review any asymmetric prints, logo patches, embroidery, or complex strap routing"
    avoid_line = "; ".join(avoid) if avoid else "props; hanger; mannequin; extra accessories; new logos; watermark; text overlay"
    inferred_line = ""
    if inferred:
        inferred_line = "This requested view is not fully supported by references; keep unsupported details minimal and do not invent closures, labels, straps, trim, or decoration.\n\n"
    return (
        "TASK:\n"
        "Generate a clean ecommerce studio product image for a fashion PDP gallery.\n\n"
        "PRODUCT IDENTITY:\n"
        f"{identity_capsule(brief)}\n\n"
        "REFERENCE PRIORITY:\n"
        "Use the primary reference for silhouette, color, construction, proportions, and fit. "
        "Use supporting references only for the details they show.\n\n"
        "SHOT:\n"
        f"{shot}. {SHOT_INSTRUCTIONS.get(shot, 'Create the requested ecommerce fashion studio shot.')}\n\n"
        f"{inferred_line}"
        "OUTPUT FORMAT:\n"
        "Native portrait 3:4 ecommerce website image. Fill the entire 3:4 canvas naturally. "
        "No padding, no white bars, no border, no letterboxing. "
        "Do not generate a smaller image centered on a larger white canvas.\n"
        f"{shot_framing_rule(shot)}\n\n"
        "STUDIO STYLE:\n"
        f"{model_direction}; {background}; soft diffused studio lighting; realistic fabric texture; "
        "natural garment drape; product fully visible unless this is a detail shot; do not preserve or clone the reference model identity.\n\n"
        "PRESERVE:\n"
        f"{preserve_line}\n\n"
        "IDENTITY LANDMARKS:\n"
        f"{landmarks_line}\n\n"
        "AVOID:\n"
        f"{avoid_line}; no altered color; no changed sleeve length; no changed neckline; no changed hem length; "
        "no changed print placement; no duplicate garment; no distorted body; no cropped product; "
        "no cropped head or face; no cropped hem; no padding; no white bars; no border; no letterboxing; "
        "no smaller image centered on a larger white canvas."
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief", required=True, help="Path to brief.json")
    parser.add_argument("--out", required=True, help="Path to write prompt-pack JSON")
    parser.add_argument("--shots", help="Comma-separated shot IDs. Defaults to brief.shot_pack or the standard 6-shot pack.")
    args = parser.parse_args()

    brief_path = Path(args.brief)
    brief = load_json(brief_path)
    shots = [s.strip() for s in args.shots.split(",") if s.strip()] if args.shots else brief.get("shot_pack") or DEFAULT_SHOTS

    items = []
    for index, shot in enumerate(shots, start=1):
        inferred = shot_is_inferred(brief, shot)
        warnings = []
        if inferred:
            warnings.append("shot_view_not_supported_by_reference")
        items.append(
            {
                "id": f"{index:02d}-{shot}",
                "shot": shot,
                "aspect_ratio": DEFAULT_ASPECT_RATIO,
                "prompt": build_prompt(brief, shot, inferred),
                "negative_constraints": normalize_list(brief.get("avoid"))
                + [
                    "invented logos",
                    "altered garment color",
                    "changed silhouette",
                    "watermark",
                    "text overlay",
                    "props",
                    "padding",
                    "white bars",
                    "letterboxing",
                    "border",
                    "smaller image centered on larger canvas",
                    "cropped head or face",
                    "cropped hem",
                ],
                "reference_roles": SHOT_REFERENCE_ROLES.get(shot, ["primary"]),
                "qa_checks": SHOT_QA.get(shot, ["product identity preserved", "white studio background"]),
                "inferred": inferred,
                "warnings": warnings,
            }
        )

    output = {
        "product_id": brief.get("product_id", ""),
        "product_name": brief.get("product_name", ""),
        "brief_hash": brief_hash(brief_path),
        "primary_reference": brief.get("primary_reference", ""),
        "source_images": brief.get("source_images", []),
        "output_dir": brief.get("output_dir") or f"outputs/fashion-studio/{brief.get('product_id', 'product')}",
        "items": items,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote prompt pack: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
