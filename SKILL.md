---
name: generate-fashion-studio-images
description: Generate no-face ecommerce studio image packs from one or more fashion product references, especially dresses and womenswear. Use when Codex needs 4-shot 3:4 on-model #FEFEFE-background PDP galleries, product-only garment references, neck-down or partial-head cropped model framing, true-scale close-up detail crops, prompt packs, contact sheets, run estimates, or QA notes while preserving garment identity and never showing recognizable model faces.
---

# Generate Fashion Studio Images

Create traceable ecommerce studio image packs for fashion products from one or more uploaded reference images. Default to an on-model `#FEFEFE` background 3:4 portrait PDP gallery for dresses and womenswear, with product identity preserved ahead of visual novelty and no recognizable model faces in any generated output.

## Default Outcome

Produce four deliverable website images by default. Do not generate internal face anchors, identity sheets, headshots, model-face references, or any image with a recognizable face.

1. `main-front-on-model` - primary website/store image, front view, full product visible, no recognizable face. Use partial head/hair crop only when needed for natural on-model framing.
2. `front-3q-on-model` - product-focused slight three-quarter view, face/head cropped out, shape and depth emphasized.
3. `detail-fabric` - true product-scale close-up showing material, texture, weave, lace, print, or finish; no face or body focus.
4. `detail-feature` - close crop of a buying-confidence detail such as neckline, sleeve, zipper, button, seam, pocket, trim, hardware, or logo patch; no face focus.

Default studio style: seamless solid `#FEFEFE` background, adult ecommerce on-model product photography, soft commercial studio lighting, native full-frame 3:4 portrait composition, product fully visible, no props, no visible brand invention, no text overlays, no watermark, no dramatic shadows. The background must render as exactly `#FEFEFE` wherever no product, model, or natural contact shadow appears; do not use pure `#FFFFFF`, gray, off-white gradients, texture, vignettes, or colored casts. Hair, back of head, crown of head, or a small chin/jaw edge may appear only when needed in the main image; eyes, nose, mouth, full face, facial profile, portrait crop, or recognizable identity are always forbidden.

## Single Main Image Override

When the user asks for only one main image per product, override the default four-shot pack and set `shot_pack` to only `main-front-on-model`. Generate exactly one deliverable per product unless the user later requests additional angles or details.

For single-main-image runs, the model must be cropped or posed so the dress remains fully visible while the eyes and nose are not visible. Acceptable framing includes a neck-down crop, a crop at or below the mouth/chin, hair covering the upper face, the head turned away with no facial profile, or the top of the head cropped out. Eyes, nose, full face, facial profile, portrait framing, and recognizable identity are `fail_regenerate`. Mouth/lips should also be avoided unless unavoidable as a tiny lower-face edge; never make the face a selling point.

Use the strongest product reference as the garment identity source and treat exact garment fidelity as more important than model novelty. Preserve the dress silhouette, color, neckline, straps, bodice construction, skirt shape, hem length, fabric texture, print, beading, trim, and distinctive details as closely as possible to the supplied image.

## Natural Fit And Tight Crop Rules

For on-model generated images, the garment should look photographed on a real body, not perfectly smoothed onto a mannequin. Include natural fabric tension, small wrinkles, compression lines, vertical folds, seam pull, hem weight, shadowing under overlays, and slight asymmetry from gravity and posture when appropriate for the fabric. Do not over-smooth satin, crepe, chiffon, tulle, organza, ruffles, beading, or fitted bodices. A natural fit should still be flattering and commercial, but it should not erase real dress lines or make fabric look like plastic.

Preserve construction landmarks exactly where they define the garment: corset top shape, pointed or curved waist seams, dropped waist position, belly/waist transition, ruffle tier count, beaded trim paths, cape attachment points, floral print scale, and applique placement. If a reference shows the skirt beginning at a specific belly/waist point, name that transition and do not move it up or down.

For no-eyes/no-nose main images, avoid leaving a large blank white band above the cropped head or neck. The top of the visible model crop should sit close to the top of the 3:4 canvas, usually within a small ecommerce headroom margin, while still preserving the full dress and hem. Large empty top space, decapitated-head whitespace, or a small model floating low in the canvas is `fail_regenerate`.

When a supporting image is supplied only for pose or hand behavior, use it only for pose guidance. Do not borrow garment identity, face, background, styling, or accessories from that secondary pose reference. If the user says the model should not hold the dress, use relaxed arms or hands behind/along the body and keep hands away from lifting or pinching skirt fabric.

## Workflow

1. Inspect all supplied images. If images are local files, use `view_image` before generation so the references are visible in context.
2. Assign product reference roles: `primary`, `front`, `back`, `side`, `detail`, `texture`, `label`, `color`. Ignore legacy `model_face` references under the no-face policy.
3. Summarize a compact garment identity capsule: category, silhouette, color, fabric, neckline/collar, sleeve/leg length, closures, pockets, seams, print/logo placement, trim/hardware, identity landmarks, and uncertainties.
4. Create or update a `brief.json` using `assets/brief-template.json` and the schema in `references/brief-schema.md`.
5. Run `scripts/prepare_references.py` to hash and inspect source references when paths are available.
6. Run `scripts/build_prompt_pack.py` to create a prompt pack from the requested `shot_pack`. It must not prepend an internal identity sheet. For single-main-image requests, use only `main-front-on-model`.
7. Generate images with Codex built-in image generation by default, one shot prompt at a time. Preserve reference priority and negative constraints in every prompt, request native full-frame `3:4` portrait composition, and keep every output free of recognizable faces. For single-main-image requests, make eyes and nose absent from the image.
8. Save generated assets under `outputs/fashion-studio/<product_id>/`, then run `scripts/normalize_ratio.py --mode verify` only to copy outputs that are already usable native 3:4 images. Regenerate anything reported as padded, letterboxed, off-ratio, or showing a recognizable face.
9. Run `scripts/write_manifest.py`.
10. Run `scripts/make_contact_sheet.py` for review and `scripts/validate_gallery.py` for basic automated warnings.
11. Review against `references/qa-checklist.md` before delivery. Regenerate weak shots with targeted prompt changes.

## Reference Priority

Use one primary garment identity reference whenever possible. The primary product image defines garment shape, color, construction, proportions, and fit. Supporting product references add only the details they show. Do not use uploaded people, faces, or legacy `model_face` references as face or identity anchors.

If references conflict on color, silhouette, sleeve length, hardware, print placement, or closure details, pause and ask which image is authoritative. If the back or side is not visible, do not present the result as factual; mark it as inferred or ask for a reference.

## Prompt Rules

Each generated prompt should include:

- task: clean no-face ecommerce studio product image
- product identity capsule
- product reference priority
- exact shot name
- required native full-frame `3:4` portrait ecommerce website ratio
- no padding, no white bars, no borders, and no letterboxing
- seamless solid `#FEFEFE` studio background and on-model presentation
- explicit no-face rule: no visible face, recognizable face, eyes, nose, mouth, lips, full face, facial profile, portrait crop, or face focus
- partial head/hair crop allowance for the main image only when needed for natural on-model framing
- single-main-image no-eyes/no-nose framing when requested: neck-down or lower-face-only crop, hair/pose obstruction, or top-of-head crop that prevents visible eyes and nose
- tight top crop rule: no large empty white area above the cropped model/head/neck; scale the model so the product fills the 3:4 frame naturally
- product fidelity requirements
- natural fit requirements: visible fabric tension, wrinkles, fold lines, seam pull, hem weight, and real-body drape appropriate to the reference
- true-scale detail framing for `detail-fabric`: close camera distance, fabric filling the frame, no waist-to-hem crop, no full skirt/full bodice, and no miniature/doll-sized garment effect
- product-specific `detail_fabric_focus` / `detail_feature_focus` when a reference image shows the exact area to crop
- negative constraints

Always preserve garment silhouette, color, texture, stitching, closures, prints, logos, proportions, and distinctive construction details. For asymmetric prints, logo patches, embroidery, and complex strap routing, name concrete identity landmarks such as "large flower at left hip" or "logo patch centered on lower band" instead of relying only on general preservation wording. Do not create, use, or reference model identity sheets, model-face assets, or face references. Do not invent labels, logos, readable text, extra accessories, props, stains, hands, duplicate garments, altered sleeve length, altered neckline, changed print placement, padded canvases, white bars, borders, or letterboxing.

Read `references/fashion-shot-patterns.md` when composing or revising prompts.

## Scripts

Use these helpers from the skill folder:

```powershell
python scripts/prepare_references.py --brief brief.json --out reference-manifest.json
python scripts/build_prompt_pack.py --brief brief.json --out prompt-pack.json
python scripts/estimate_generation_run.py --prompt-pack prompt-pack.json --out generation-estimate.json
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
- Deliver four website images by default: two no-face on-model product shots and two no-face detail shots. If the user requests only one main image per product, deliver exactly one `main-front-on-model` image per product instead.
- Deliver images as native full-frame 3:4 portrait files for website upload with a seamless solid `#FEFEFE` background.
- Treat visible faces, recognizable faces, eyes, nose, full profiles, portrait crops, padded outputs, white top/bottom bands, side bars, borders, letterboxing, or a smaller centered image on a larger white canvas as `fail_regenerate`. For single-main-image requests, visible eyes or nose are always `fail_regenerate`; visible mouth/lips are also unacceptable unless only a tiny lower-face edge remains and the face is not identifiable.
- Treat mannequin-smooth, plastic-looking, over-retouched, or physically implausible garment fit as `warn_review` or `fail_regenerate` when the reference shows wrinkles, folds, ruching, seams, ruffles, or fabric tension that should be visible.
- Treat `detail-fabric` outputs as `fail_regenerate` if they look like a small dress or zoomed-out garment crop instead of a real close-up fabric/detail shot.
- Save every final output and sidecar metadata in the product output folder.
- Include the final prompt pack, manifest, contact sheet, validation report, and any unresolved QA risks.
- Treat exact logo/text reproduction as high risk and require manual review.
- Keep commercial claims, certifications, awards, and brand partnerships out of generated visuals unless the source reference clearly contains them.
