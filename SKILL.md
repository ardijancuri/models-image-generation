---
name: generate-fashion-studio-images
description: Generate ecommerce studio image packs from one or more fashion product references, especially dresses and womenswear. Use when Codex needs 3:4 on-model white-background product shots, visible generic model faces, PDP gallery images, angle variants, detail crops, prompt packs, contact sheets, or QA notes while preserving garment identity.
---

# Generate Fashion Studio Images

Create traceable ecommerce studio image packs for fashion products from one or more uploaded reference images. Default to an on-model white-background 3:4 portrait PDP gallery for dresses and womenswear, with product identity preserved ahead of visual novelty.

## Default Outcome

Produce a 6-shot pack unless the user asks otherwise:

1. `main-front-on-model` - primary website/store image, front view, full product visible.
2. `front-3q-on-model` - slight three-quarter view for shape and depth.
3. `back-on-model` - back view only when references support it; otherwise mark inferred or ask.
4. `side-on-model` - side view only when references support it; otherwise mark inferred or ask.
5. `detail-fabric` - close crop showing material, texture, weave, lace, print, or finish.
6. `detail-feature` - close crop of a buying-confidence detail such as neckline, sleeve, zipper, button, seam, pocket, trim, hardware, or logo patch.

Default studio style: seamless pure white background, adult generic model with visible natural ecommerce face allowed, soft commercial studio lighting, native full-frame 3:4 portrait composition, product fully visible, no props, no visible brand invention, no text overlays, no watermark, no dramatic shadows. Do not preserve or clone the real reference model's identity.

## Workflow

1. Inspect all supplied images. If images are local files, use `view_image` before generation so the references are visible in context.
2. Assign reference roles: `primary`, `front`, `back`, `side`, `detail`, `texture`, `label`, `color`.
3. Summarize a compact garment identity capsule: category, silhouette, color, fabric, neckline/collar, sleeve/leg length, closures, pockets, seams, print/logo placement, trim/hardware, identity landmarks, and uncertainties.
4. Create or update a `brief.json` using `assets/brief-template.json` and the schema in `references/brief-schema.md`.
5. Run `scripts/prepare_references.py` to hash and inspect source references when paths are available.
6. Run `scripts/build_prompt_pack.py` to create a prompt pack for the requested shot list.
7. Generate images with Codex built-in image generation by default, one shot prompt at a time. Preserve reference priority and negative constraints in every prompt, and request native full-frame `3:4` portrait composition.
8. Save generated assets under `outputs/fashion-studio/<product_id>/`, then run `scripts/normalize_ratio.py --mode verify` only to copy outputs that are already usable native 3:4 images. Regenerate anything reported as padded, letterboxed, or off-ratio.
9. Run `scripts/write_manifest.py`.
10. Run `scripts/make_contact_sheet.py` for review and `scripts/validate_gallery.py` for basic automated warnings.
11. Review against `references/qa-checklist.md` before delivery. Regenerate weak shots with targeted prompt changes.

## Reference Priority

Use one primary identity reference whenever possible. The primary image defines garment shape, color, construction, proportions, and fit. Supporting references add only the details they show.

If references conflict on color, silhouette, sleeve length, hardware, print placement, or closure details, pause and ask which image is authoritative. If the back or side is not visible, do not present the result as factual; mark it as inferred or ask for a reference.

## Prompt Rules

Each generated prompt should include:

- task: clean ecommerce studio product image
- product identity capsule
- reference priority
- exact shot name
- required native full-frame `3:4` portrait ecommerce website ratio
- no padding, no white bars, no borders, and no letterboxing
- white studio background and on-model presentation
- product fidelity requirements
- negative constraints

Always preserve garment silhouette, color, texture, stitching, closures, prints, logos, proportions, and distinctive construction details. For asymmetric prints, logo patches, embroidery, and complex strap routing, name concrete identity landmarks such as "large flower at left hip" or "logo patch centered on lower band" instead of relying only on general preservation wording. Use a generic adult model face when faces are visible; do not preserve or clone the face/identity from the reference images. Do not invent labels, logos, readable text, extra accessories, props, stains, hands, duplicate garments, altered sleeve length, altered neckline, changed print placement, padded canvases, white bars, borders, or letterboxing.

Read `references/fashion-shot-patterns.md` when composing or revising prompts.

## Scripts

Use these helpers from the skill folder:

```powershell
python scripts/prepare_references.py --brief brief.json --out reference-manifest.json
python scripts/build_prompt_pack.py --brief brief.json --out prompt-pack.json
python scripts/normalize_ratio.py --mode verify --images-dir outputs/fashion-studio/<product_id> --out-dir outputs/fashion-studio/<product_id>/native-3x4
python scripts/write_manifest.py --prompt-pack prompt-pack.json --images-dir outputs/fashion-studio/<product_id>/native-3x4 --out manifest.json
python scripts/make_contact_sheet.py --manifest manifest.json --images-dir outputs/fashion-studio/<product_id>/native-3x4 --out contact-sheet.png
python scripts/validate_gallery.py --manifest manifest.json --images-dir outputs/fashion-studio/<product_id>/native-3x4 --out validation-report.json
```

The scripts do not call an image-generation API. They prepare, track, and review the work so Codex can use built-in image generation without losing provenance.

## Resource Routing

- Read `references/brief-schema.md` when creating, validating, or explaining a brief.
- Read `references/fashion-shot-patterns.md` before building prompts or revising a weak shot.
- Read `references/qa-checklist.md` before final delivery.
- Read `references/failure-modes.md` when references are incomplete, garments are white/reflective/patterned, or logos/text must remain exact.

## Delivery Rules

- Put the main PDP image first.
- Deliver images as native full-frame 3:4 portrait files for website upload.
- Treat padded outputs, white top/bottom bands, side bars, borders, letterboxing, or a smaller centered image on a larger white canvas as `fail_regenerate`.
- Save every final output and sidecar metadata in the product output folder.
- Include the final prompt pack, manifest, contact sheet, validation report, and any unresolved QA risks.
- Treat exact logo/text reproduction as high risk and require manual review.
- Keep commercial claims, certifications, awards, and brand partnerships out of generated visuals unless the source reference clearly contains them.
