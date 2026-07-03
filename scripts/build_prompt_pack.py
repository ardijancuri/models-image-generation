#!/usr/bin/env python3
"""Build a prompt pack for no-face fashion studio image generation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


DEFAULT_SHOTS = [
    "main-front-on-model",
    "front-3q-on-model",
    "detail-fabric",
    "detail-feature",
]

DEFAULT_ASPECT_RATIO = "3:4"
DEFAULT_BACKGROUND = (
    "seamless solid #FEFEFE studio background; background pixels must be #FEFEFE wherever no product, "
    "model, or natural contact shadow appears; avoid pure #FFFFFF, gray, off-white gradients, texture, vignettes, or colored casts"
)
LEGACY_FACE_REFERENCE_ROLES = {"model_face", "face", "model-face"}

DEFAULT_MODEL_DIRECTION = (
    "adult ecommerce model, on-model product photography, no recognizable model face shown in any generated image"
)
DEFAULT_MODEL_APPEARANCE = (
    "adult ecommerce model body and hair may be visible only as product context; no eyes, nose, mouth, full profile, "
    "or recognizable facial identity"
)
DEFAULT_MODEL_STYLING = (
    "soft polished occasion styling and professionally styled hair that match the garment; no jewelry or accessories "
    "unless explicitly requested"
)
DEFAULT_MODEL_CONSISTENCY = (
    "keep body proportions, hair color, hair length, hairstyle, makeup-adjacent styling, and skin tone consistent where visible; "
    "do not create or use a face identity anchor"
)
DEFAULT_NATURAL_FIT = (
    "make the garment look naturally worn on a real body: preserve visible fabric tension, small wrinkles, fold lines, seam pull, "
    "hem weight, slight asymmetry, and realistic drape appropriate to the fabric; avoid mannequin-smooth or plastic-looking surfaces"
)
DEFAULT_TIGHT_TOP_CROP = (
    "avoid empty white space above the cropped model; keep the top of the visible neck/chin/shoulders close to the top of the 3:4 frame "
    "while still showing the full garment and hem"
)
DEFAULT_POSE_DIRECTION = (
    "neutral ecommerce stance with relaxed arms; do not hold, pinch, or lift the garment unless the shot specifically requires it"
)

NO_FACE_NEGATIVE_CONSTRAINTS = [
    "visible model face",
    "recognizable face",
    "eyes",
    "nose",
    "mouth",
    "lips",
    "full face",
    "facial profile",
    "portrait crop",
    "face focus",
    "headshot",
    "beauty portrait",
    "face-reference cloning",
    "using garment/product reference photos as model face reference",
    "model identity sheet",
    "model face reference",
    "mannequin-smooth garment",
    "plastic-looking fabric",
    "over-smoothed dress",
    "airbrushed fabric without wrinkles",
    "perfectly body-painted dress fit",
    "large empty white space above cropped model",
    "small model floating low in canvas",
]

FACE_FIELD_MARKERS = [
    "face",
    "facial",
    "eyes",
    "eye",
    "nose",
    "mouth",
    "lips",
    "identity sheet",
    "identity anchor",
    "00-model",
    "model_face",
    "headshot",
    "portrait",
]

SHOT_INSTRUCTIONS = {
    "main-front-on-model": (
        "Primary on-model ecommerce PDP image. Product centered, full garment and hem visible. "
        "Use no-eyes/no-nose model framing: neck-down, lower-face-only, hair-obscured upper face, or head cropped so "
        "eyes and nose are absent. Hair, back of head, crown of head, or a small chin/jaw edge may appear, "
        "but no recognizable face, eyes, nose, mouth focus, or full facial profile. Scale and crop so there is no large empty white band above the cropped model."
    ),
    "front-3q-on-model": (
        "Product-focused slight three-quarter front angle showing garment depth, drape, side seam, and silhouette. "
        "Crop the model face/head out of frame and let the product fill more of the image."
    ),
    "back-on-model": (
        "Back-facing studio image with no visible face, preserving full garment and hem. "
        "Do not invent back closures, labels, straps, or decoration if references do not show them."
    ),
    "side-on-model": (
        "Product-focused side-view studio image preserving hem length, sleeve shape, drape, and garment volume. "
        "Crop the model face/head out of frame; do not show a facial profile."
    ),
    "detail-fabric": (
        "True product-scale close-up of a small real garment area, shot from close range. Show fabric texture, "
        "surface, sheen, weave, folds, or drape at believable life-size scale. Do not show a waist-to-hem crop, "
        "whole skirt, full bodice, or a miniature/doll-like dress composition."
    ),
    "detail-feature": (
        "Close crop of a buying-confidence detail such as neckline, sleeve cuff, zipper, button, pocket, seam, hem, "
        "strap, lining, trim, hardware, or logo patch, filling the vertical 3:4 frame naturally."
    ),
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
    "main-front-on-model": ["full garment visible", "works as first PDP image", "no recognizable face", "#FEFEFE studio background"],
    "front-3q-on-model": ["same garment identity", "useful angle variation", "face cropped out", "product-focused framing", "no silhouette drift"],
    "back-on-model": ["back details supported or flagged inferred", "no invented closures", "no visible face", "#FEFEFE studio background"],
    "side-on-model": ["side details supported or flagged inferred", "no facial profile", "hem and drape preserved", "#FEFEFE studio background"],
    "detail-fabric": ["sharp texture", "actual fabric matches reference", "true close-up scale", "no miniature dress effect", "no waist-to-hem crop"],
    "detail-feature": ["feature is product-specific", "no invented label or hardware", "sharp crop", "no face focus"],
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def brief_hash(brief_path: Path) -> str:
    return hashlib.sha256(brief_path.read_bytes()).hexdigest()


def normalize_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    return [str(value)]


def dedupe_list(values: list[str]) -> list[str]:
    seen = set()
    output = []
    for value in values:
        if value and value not in seen:
            output.append(value)
            seen.add(value)
    return output


def legacy_face_reference_warnings(brief: dict[str, Any]) -> list[str]:
    warnings = []
    if normalize_list(brief.get("model_face_references")):
        warnings.append("model_face_references_ignored_no_faces_policy")
    roles = brief.get("reference_roles", {})
    if isinstance(roles, dict) and any(normalize_list(roles.get(role)) for role in LEGACY_FACE_REFERENCE_ROLES):
        warnings.append("model_face_reference_roles_ignored_no_faces_policy")
    for item in brief.get("source_images", []):
        if isinstance(item, dict) and str(item.get("role", "")).lower() in LEGACY_FACE_REFERENCE_ROLES:
            warnings.append("model_face_source_images_ignored_no_faces_policy")
            break
    return dedupe_list(warnings)


def sanitized_model_text(value: Any, fallback: str) -> str:
    text = str(value or "").strip()
    if not text:
        return fallback
    lowered = text.lower()
    if any(marker in lowered for marker in FACE_FIELD_MARKERS):
        return fallback
    return text


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
    if shot == "main-front-on-model":
        return (
            "No-face main-image framing: keep the full garment and hem visible on model. "
            "Crop or pose the model so the eyes and nose are not visible: use neck-down framing, lower-face-only framing, "
            "hair over the upper face, the head turned away without facial profile, or top-of-head cropped out. "
            "Hair, back of head, crown of head, or a small chin/jaw edge is acceptable, but eyes, nose, mouth focus, "
            "full face, full profile, and any recognizable face are forbidden."
        )
    if shot in {"front-3q-on-model", "side-on-model", "back-on-model"}:
        return (
            "Product-focused on-model framing: crop the model face/head out of the frame while preserving the garment. "
            "Frame from the neck, shoulders, upper torso, back of head, or hair down as appropriate for the product. "
            "Keep the relevant garment and hem visible when this is a full-length product shot. No visible face, no eyes, no nose, no mouth, and no facial profile."
        )
    if shot == "detail-fabric":
        return (
            "Detail-fabric framing: use a true close-up or macro-medium product angle, about 20-45 cm from the garment. "
            "Show only a small section of fabric, folds, drape, or texture at believable real garment scale. "
            "The fabric should fill at least 85% of the 3:4 canvas. Do not include both waist seam and hem in the same image, "
            "do not show the whole skirt, do not show the full bodice, and do not make the dress look miniature or doll-sized. No body or face focus."
        )
    if shot.startswith("detail-"):
        return (
            "Detail framing: the garment detail fills the vertical 3:4 frame naturally, "
            "with no huge empty top, bottom, or side bands and no square image placed inside a portrait canvas. No face or body focus."
        )
    return (
        "No-face on-model framing: preserve the garment and crop out any recognizable model face."
    )


def model_style(brief: dict[str, Any], shot: str) -> str:
    model_direction = sanitized_model_text(brief.get("model_direction"), DEFAULT_MODEL_DIRECTION)
    model_appearance = sanitized_model_text(brief.get("model_appearance"), DEFAULT_MODEL_APPEARANCE)
    model_styling = sanitized_model_text(brief.get("model_styling"), DEFAULT_MODEL_STYLING)
    model_consistency = sanitized_model_text(brief.get("model_consistency"), DEFAULT_MODEL_CONSISTENCY)
    if shot.startswith("detail-"):
        return (
            f"{model_direction}; any body context is secondary and should avoid the face entirely; "
            f"{model_appearance}; {model_styling}; {model_consistency}; no visible face, no portrait framing"
        )
    return (
        f"{model_direction}; {model_appearance}; {model_styling}; {model_consistency}; "
        "no visible face, no eyes, no nose, no mouth, no facial profile, no face identity anchor"
    )


def shot_focus(brief: dict[str, Any], shot: str) -> str:
    detail_focus = brief.get("detail_shot_focus")
    focus = ""
    if isinstance(detail_focus, dict):
        focus = str(detail_focus.get(shot, "") or "")
    if not focus and shot == "detail-fabric":
        focus = str(brief.get("detail_fabric_focus", "") or "")
    if not focus and shot == "detail-feature":
        focus = str(brief.get("detail_feature_focus", "") or "")
    return f"Shot focus: {focus}\n" if focus else ""


def optional_brief_line(brief: dict[str, Any], key: str, label: str, fallback: str = "") -> str:
    text = str(brief.get(key, "") or fallback).strip()
    return f"{label}: {text}\n" if text else ""


def build_prompt(brief: dict[str, Any], shot: str, inferred: bool) -> str:
    must_preserve = normalize_list(brief.get("must_preserve"))
    avoid = normalize_list(brief.get("avoid"))
    background = brief.get("background") or DEFAULT_BACKGROUND
    preserve_line = "; ".join(must_preserve) if must_preserve else "all visible garment identity details from the references"
    garment_identity = brief.get("garment_identity", {})
    landmarks = normalize_list(garment_identity.get("identity_landmarks") if isinstance(garment_identity, dict) else None)
    landmarks_line = "; ".join(landmarks) if landmarks else "none listed; manually review any asymmetric prints, logo patches, embroidery, or complex strap routing"
    avoid_line = "; ".join(avoid) if avoid else "props; hanger; mannequin; extra accessories; new logos; watermark; text overlay"
    focus_line = shot_focus(brief, shot)
    inferred_line = ""
    if inferred:
        inferred_line = "This requested view is not fully supported by references; keep unsupported details minimal and do not invent closures, labels, straps, trim, or decoration.\n"

    return (
        "Generate a clean no-face ecommerce studio product image for a fashion PDP gallery.\n"
        f"Product identity: {identity_capsule(brief)}\n"
        "Reference priority: product references control garment silhouette, color, construction, proportions, and fit; supporting product references add only the details they show. "
        "Ignore any legacy model_face references because this skill follows a strict no-recognizable-face policy.\n"
        f"Shot: {shot}. {SHOT_INSTRUCTIONS.get(shot, 'Create the requested ecommerce fashion studio shot without showing a recognizable face.')}\n"
        f"{focus_line}"
        f"{inferred_line}"
        "Face policy: do not show a recognizable model face in this image. No eyes, nose, mouth, lips, full face, full profile, portrait crop, or face focus. "
        "A partial head crop, hair, back of head, crown of head, or small chin/jaw edge is acceptable only when needed for natural on-model product framing.\n"
        "Output: native portrait 3:4 ecommerce website image, full-frame composition. Fill the entire 3:4 canvas naturally. "
        "No padding, no white bars, no border, no letterboxing, no smaller image centered on a larger white canvas. "
        "Do not make a 2:3 image such as 1024x1536.\n"
        f"{shot_framing_rule(shot)}\n\n"
        f"{optional_brief_line(brief, 'framing_direction', 'Crop/scale direction', DEFAULT_TIGHT_TOP_CROP)}"
        f"{optional_brief_line(brief, 'natural_fit_direction', 'Natural fit direction', DEFAULT_NATURAL_FIT)}"
        f"{optional_brief_line(brief, 'pose_direction', 'Pose direction', DEFAULT_POSE_DIRECTION)}"
        f"Studio/model: {model_style(brief, shot)}; {background}; soft diffused studio lighting; realistic fabric texture; natural garment drape.\n"
        f"Preserve: {preserve_line}.\n"
        f"Identity landmarks: {landmarks_line}.\n"
        f"Avoid: {avoid_line}; altered color/silhouette/neckline/hem, invented closures/logos/text, accessories, cropped product, cropped hem, "
        "visible model face, recognizable face, eyes, nose, mouth, lips, full face, facial profile, portrait crop, face focus, face-reference cloning, "
        "padding, white bars, borders, letterboxing, 2:3 ratio."
    )


def shot_negative_constraints(shot: str) -> list[str]:
    if shot == "detail-fabric":
        return [
            "miniature dress effect",
            "doll-sized garment",
            "waist-to-hem detail crop",
            "whole skirt shown in detail shot",
            "full bodice shown in fabric detail",
            "zoomed-out fabric detail",
            "fabric detail too far from camera",
            "generic fabric macro unrelated to product reference",
            "detail crop from another garment",
        ]
    return []


def negative_constraints_for_shot(brief: dict[str, Any], shot: str) -> list[str]:
    constraints = normalize_list(brief.get("avoid")) + [
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
        "cropped product",
        "cropped hem",
        "large empty white space above cropped model",
        "small model floating low in canvas",
        "mannequin-smooth garment",
        "plastic-looking fabric",
        "over-smoothed dress",
        "airbrushed fabric without wrinkles",
        "perfectly body-painted dress fit",
        "missing natural wrinkles",
        "missing fabric tension",
        "missing seam pull",
        "hands holding skirt when not requested",
        "hands pinching dress fabric when not requested",
    ]
    constraints.extend(NO_FACE_NEGATIVE_CONSTRAINTS)
    constraints.extend(shot_negative_constraints(shot))
    return dedupe_list(constraints)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief", required=True, help="Path to brief.json")
    parser.add_argument("--out", required=True, help="Path to write prompt-pack JSON")
    parser.add_argument("--shots", help="Comma-separated deliverable shot IDs. Defaults to brief.shot_pack or the standard 4-shot pack.")
    args = parser.parse_args()

    brief_path = Path(args.brief)
    brief = load_json(brief_path)
    requested_shots = [s.strip() for s in args.shots.split(",") if s.strip()] if args.shots else brief.get("shot_pack") or DEFAULT_SHOTS
    shots = requested_shots or DEFAULT_SHOTS
    legacy_warnings = legacy_face_reference_warnings(brief)

    items = []
    for index, shot in enumerate(shots, start=1):
        inferred = shot_is_inferred(brief, shot)
        warnings = list(legacy_warnings)
        if inferred:
            warnings.append("shot_view_not_supported_by_reference")
        items.append(
            {
                "id": f"{index:02d}-{shot}",
                "shot": shot,
                "aspect_ratio": DEFAULT_ASPECT_RATIO,
                "deliverable": True,
                "face_visible": False,
                "requires_model_identity_anchor": False,
                "prompt": build_prompt(brief, shot, inferred),
                "negative_constraints": negative_constraints_for_shot(brief, shot),
                "reference_roles": SHOT_REFERENCE_ROLES.get(shot, ["primary"]),
                "qa_checks": SHOT_QA.get(shot, ["product identity preserved", "#FEFEFE studio background", "no recognizable face"]),
                "model_appearance": sanitized_model_text(brief.get("model_appearance"), DEFAULT_MODEL_APPEARANCE),
                "model_styling": sanitized_model_text(brief.get("model_styling"), DEFAULT_MODEL_STYLING),
                "model_consistency": sanitized_model_text(brief.get("model_consistency"), DEFAULT_MODEL_CONSISTENCY),
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
        "model_appearance": sanitized_model_text(brief.get("model_appearance"), DEFAULT_MODEL_APPEARANCE),
        "model_styling": sanitized_model_text(brief.get("model_styling"), DEFAULT_MODEL_STYLING),
        "model_consistency": sanitized_model_text(brief.get("model_consistency"), DEFAULT_MODEL_CONSISTENCY),
        "natural_fit_direction": brief.get("natural_fit_direction", DEFAULT_NATURAL_FIT),
        "framing_direction": brief.get("framing_direction", DEFAULT_TIGHT_TOP_CROP),
        "pose_direction": brief.get("pose_direction", DEFAULT_POSE_DIRECTION),
        "deliverable_count": len(items),
        "internal_count": 0,
        "face_visible_deliverable_count": 0,
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
