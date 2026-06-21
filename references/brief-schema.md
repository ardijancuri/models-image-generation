# Brief Schema

Use a compact JSON brief as the source of truth for a fashion studio image pack.

```json
{
  "product_id": "sku-dress-001",
  "product_name": "Black satin midi dress",
  "category": "womenswear dress",
  "source_images": [
    {
      "path": "references/front.jpg",
      "role": "front",
      "notes": "front view, strongest identity reference"
    }
  ],
  "primary_reference": "references/front.jpg",
  "reference_roles": {
    "primary": ["references/front.jpg"],
    "front": ["references/front.jpg"],
    "back": [],
    "side": [],
    "detail": []
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
    "back-on-model",
    "side-on-model",
    "detail-fabric",
    "detail-feature"
  ],
  "aspect_ratio": "3:4",
  "background": "seamless pure white studio background",
  "model_direction": "adult generic model, visible natural ecommerce face allowed, neutral expression, do not preserve the reference model identity",
  "avoid": [
    "props",
    "hanger",
    "mannequin",
    "extra accessories",
    "new logo",
    "watermark",
    "text overlay"
  ],
  "output_dir": "outputs/fashion-studio/sku-dress-001"
}
```

## Required Fields

- `product_id`: stable folder and filename identifier.
- `product_name`: human-readable product name.
- `category`: product type, for example `dress`, `blouse`, `coat`, `skirt`, `womenswear set`.
- `source_images`: image paths or objects with `path`, `role`, and optional `notes`.
- `primary_reference`: the most authoritative identity image.
- `reference_roles`: role-to-image mapping.
- `must_preserve`: visible product features that must not drift.
- `shot_pack`: requested shot IDs.
- `aspect_ratio`: always use native full-frame `3:4` for website-ready portrait images.
- `background`: default to seamless pure white studio background.
- `model_direction`: default to adult generic model, visible natural ecommerce face allowed, neutral expression, and no reference-model identity preservation.
- `avoid`: negative constraints.
- `output_dir`: default `outputs/fashion-studio/<product_id>`.

## Role Guidance

Use `primary` for the main identity reference. Use `front`, `back`, and `side` only when that view is visible. Use `detail`, `texture`, `label`, and `color` for supporting references that should influence only localized details.

When a required shot lacks supporting references, set the shot-level `inferred` flag in the prompt pack and include a QA warning.

## Identity Landmarks

Use `garment_identity.identity_landmarks` for exact positional markers that must survive generation. This is especially important for asymmetric prints, florals, embroidery, logo patches, typography, strap routing, unusual seams, and hardware.

Good examples:

- `large ivory flower begins at the wearer's left waist and crosses toward the center skirt`
- `small logo patch sits on the lower front band, slightly right of center`
- `double straps cross at the back and attach near the outer shoulder edge`

If these details are unknown, leave the list empty and flag the output for manual review.

## Ratio And Faces

Use `3:4` as width:height, for example `1536x2048` or `1200x1600`. All generated shots, including detail crops, should be composed natively as full-frame 3:4 portrait website images.

Do not treat 3:4 as a post-processing padding step. The image should fill the 3:4 canvas naturally during generation. Padded outputs, white top/bottom bands, white side bars, borders, letterboxing, or a smaller image centered on a larger white canvas should be marked `fail_regenerate`.

Faces are allowed by default for full-body and angle shots. Use a generic adult ecommerce model face with a natural neutral expression. Do not preserve, clone, or imply the identity of the person in the reference images. Detail shots should focus on garment construction and usually avoid the full face.
