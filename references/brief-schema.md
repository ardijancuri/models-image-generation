# Brief Schema

Use a compact JSON brief as the source of truth for a no-face fashion studio image pack.

```json
{
  "product_id": "sku-dress-001",
  "product_name": "Black satin midi dress",
  "category": "womenswear dress",
  "source_images": [
    {
      "path": "references/front.jpg",
      "role": "front",
      "notes": "front view, strongest garment identity reference"
    }
  ],
  "primary_reference": "references/front.jpg",
  "reference_roles": {
    "primary": ["references/front.jpg"],
    "front": ["references/front.jpg"],
    "back": [],
    "side": [],
    "detail": [],
    "texture": [],
    "label": [],
    "color": []
  },
  "garment_identity": {
    "category": "dress",
    "silhouette": "fitted bodice with A-line midi skirt",
    "color": "black",
    "fabric": "smooth satin",
    "neckline": "square neckline",
    "sleeves": "sleeveless",
    "closures": "hidden back zipper if visible",
    "seams": "princess seams",
    "print_or_logo": "none visible",
    "trim_or_hardware": "none visible",
    "identity_landmarks": [
      "large motif at left hip if visible",
      "logo patch location if visible"
    ],
    "uncertainties": ["back closure not visible"]
  },
  "must_preserve": [
    "black satin color",
    "square neckline",
    "midi length",
    "A-line skirt shape"
  ],
  "shot_pack": [
    "main-front-on-model",
    "front-3q-on-model",
    "detail-fabric",
    "detail-feature"
  ],
  "aspect_ratio": "3:4",
  "background": "seamless solid #FEFEFE studio background; background pixels must be #FEFEFE wherever no product, model, or natural contact shadow appears",
  "model_direction": "adult ecommerce on-model product photography; no recognizable model face in any generated image",
  "model_appearance": "adult ecommerce model body and hair may be visible only as product context; no eyes, nose, mouth, full face, facial profile, or recognizable identity",
  "model_styling": "soft polished occasion styling and professionally styled hair that match the garment; no jewelry or accessories unless explicitly requested",
  "model_consistency": "keep body proportions, hair color, hair length, hairstyle, and skin tone consistent where visible; do not create or use a face identity anchor",
  "detail_fabric_focus": "optional product-specific instruction for the fabric detail crop",
  "detail_feature_focus": "optional product-specific instruction for the feature detail crop",
  "avoid": [
    "props",
    "visible model face",
    "recognizable face",
    "eyes",
    "nose",
    "mouth",
    "facial profile",
    "portrait crop"
  ],
  "output_dir": "outputs/fashion-studio/sku-dress-001"
}
```

## Required Fields

- `product_id`: stable folder and filename identifier.
- `product_name`: human-readable product name.
- `category`: product type, for example `dress`, `blouse`, `coat`, `skirt`, `womenswear set`.
- `source_images`: product image paths or objects with `path`, `role`, and optional `notes`.
- `primary_reference`: the most authoritative garment identity image.
- `reference_roles`: product role-to-image mapping. Valid roles are `primary`, `front`, `back`, `side`, `detail`, `texture`, `label`, and `color`.
- `must_preserve`: visible product features that must not drift.
- `shot_pack`: requested deliverable shot IDs. Defaults to four final website images: `main-front-on-model`, `front-3q-on-model`, `detail-fabric`, and `detail-feature`. The prompt builder must not prepend an internal identity sheet.
- `aspect_ratio`: always use native full-frame `3:4` for website-ready portrait images.
- `background`: default to a seamless solid `#FEFEFE` studio background. Prompts must request exactly `#FEFEFE` wherever no product, model, or natural contact shadow appears, and must avoid pure `#FFFFFF`, gray, off-white gradients, texture, vignettes, or colored casts.
- `model_direction`: default to adult ecommerce on-model product photography with no recognizable face.
- `model_appearance`: optional body/hair context direction. It must not describe a visible face.
- `model_styling`: optional hair and styling direction matched to the garment, with no jewelry or accessories unless requested.
- `model_consistency`: optional consistency direction for visible body/hair context. It must not request a face identity anchor.
- `detail_fabric_focus`: optional, but recommended when a supplied reference shows the exact close-up area. Use it to prevent generic fabric macros or detail crops from another product.
- `detail_feature_focus`: optional, but recommended for a specific neckline, sleeve, trim, hardware, closure, or drape construction detail.
- `avoid`: negative constraints. Include no-face constraints.
- `output_dir`: default `outputs/fashion-studio/<product_id>`.

## Role Guidance

Use `primary` for the main garment identity reference. Use `front`, `back`, and `side` only when that view is visible. Use `detail`, `texture`, `label`, and `color` for supporting product references that should influence only localized garment details.

Ignore legacy `model_face`, `face`, or `model-face` roles under the no-face policy. They should not be included in prompt packs except as warnings such as `model_face_references_ignored_no_faces_policy`.

When a required shot lacks supporting references, set the shot-level `inferred` flag in the prompt pack and include a QA warning.

## Identity Landmarks

Use `garment_identity.identity_landmarks` for exact positional markers that must survive generation. This is especially important for asymmetric prints, florals, embroidery, logo patches, typography, strap routing, unusual seams, and hardware.

Good examples:

- `large ivory flower begins at the wearer's left waist and crosses toward the center skirt`
- `small logo patch sits on the lower front band, slightly right of center`
- `double straps cross at the back and attach near the outer shoulder edge`

If these details are unknown, leave the list empty and flag the output for manual review.

## Ratio And Face Policy

Use `3:4` as width:height, for example `1536x2048` or `1200x1600`. All generated shots, including detail crops, should be composed natively as full-frame 3:4 portrait website images.

Do not treat 3:4 as a post-processing padding step. The image should fill the 3:4 canvas naturally during generation. Padded outputs, white top/bottom bands, white side bars, borders, letterboxing, or a smaller image centered on a larger white canvas should be marked `fail_regenerate`.

Faces are not allowed in any generated output. The main shot can use a partial head crop, hair, back of head, crown of head, or a small chin/jaw edge when needed for natural on-model product framing. Eyes, nose, mouth, lips, full face, full facial profile, portrait crop, headshot, or any recognizable identity should be marked `fail_regenerate`.

No `00-model-identity-sheet` is generated. `face_visible` is always `false`, `requires_model_identity_anchor` is always `false`, and `internal_count` is `0`.

## Prompt Pack Metadata

`build_prompt_pack.py` adds metadata that downstream scripts use:

- `deliverable`: `true` for all default website images.
- `face_visible`: `false` for every shot.
- `requires_model_identity_anchor`: `false` for every shot.
- `inferred`: `true` only for unsupported optional back or side views.

Contact sheets and validation reports should review deliverables only by default because there are no internal identity-sheet images.
