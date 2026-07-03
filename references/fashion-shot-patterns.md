# Fashion Shot Patterns

Use these patterns to build concise no-face prompts. Keep the garment identity factual and short.

## Shared Prompt Skeleton

```text
TASK:
Generate a clean no-face ecommerce studio product image for a fashion PDP gallery.

PRODUCT IDENTITY:
{garment_identity_capsule}

REFERENCE PRIORITY:
Use product references for garment silhouette, color, construction, proportions, and fit. Use supporting product references only for the details they show. Ignore legacy model_face references under the no-face policy.

SHOT:
{shot_name}. {shot_instruction}

FACE POLICY:
Do not show a recognizable model face in this image. No eyes, nose, mouth, lips, full face, full profile, portrait crop, headshot, or face focus. Hair, back of head, crown of head, or a small chin/jaw edge is acceptable only when needed for natural on-model product framing.

OUTPUT FORMAT:
Native portrait 3:4 ecommerce website image. Fill the entire 3:4 canvas naturally. No padding, no white bars, no border, no letterboxing. Do not generate a smaller image centered on a larger white canvas.

FRAMING:
For `main-front-on-model`, keep the full garment and hem visible on model with no recognizable face. For supporting on-model shots, crop the model face/head out and frame from the neck, shoulders, upper torso, back of head, or hair down so the product fills more of the image. For `detail-fabric`, use a true close-up or macro-medium product angle from about 20-45 cm away; fabric should fill at least 85% of the 3:4 canvas at believable real garment scale. For other detail shots, make the garment detail fill the vertical 3:4 frame naturally with no huge empty bands.

STUDIO STYLE:
Adult ecommerce no-face on-model product photography, neutral ecommerce pose, soft polished occasion styling, professionally styled hair matched to the garment when visible, seamless solid #FEFEFE background, soft diffused studio lighting, realistic fabric texture, natural garment drape, product fully visible unless this is a detail shot. The background must be exactly #FEFEFE wherever no product, model, or natural contact shadow appears; avoid pure #FFFFFF, gray, off-white gradients, texture, vignettes, or colored casts. Do not create or use a face identity anchor.

PRESERVE:
{must_preserve}

IDENTITY LANDMARKS:
{identity_landmarks}

AVOID:
No props, hanger, mannequin unless requested, extra accessories, new logos, altered color, changed sleeve length, changed neckline, changed hem length, changed print placement, text overlay, watermark, dramatic shadow, duplicate garment, distorted body, cropped product, cropped hem, visible face, recognizable face, eyes, nose, mouth, lips, full face, facial profile, portrait crop, face focus, headshot, padding, white bars, border, or letterboxing.
```

## Default Shots

The default prompt pack contains four deliverable website images. It does not contain an internal identity sheet.

`main-front-on-model`
: Primary no-face on-model ecommerce PDP image. Product centered, full garment and hem visible. Use a partial head crop only when needed for natural product framing: hair, back of head, crown of head, or a small chin/jaw edge may appear, but no eyes, nose, mouth, full face, full profile, or recognizable identity.

`front-3q-on-model`
: Product-focused slight three-quarter front angle. Show garment depth, drape, side seam, and silhouette while preserving the same product and any named print/logo landmarks. Crop the model face/head out of frame and let the product fill more of the native 3:4 canvas.

`back-on-model`
: Optional no-face back-facing studio image. Use only if back reference exists. If inferred, state that back details must remain minimal and avoid inventing closures, labels, straps, or decoration.

`side-on-model`
: Optional no-face side-view studio image. Use only if side structure is visible or can be safely inferred. Preserve hem length, sleeve shape, drape, and garment volume. Crop out the face/head and never show a facial profile.

`detail-fabric`
: True product-scale close-up of a small real garment area: fabric texture, weave, lace, knit, sheen, print, embroidery, surface finish, or localized folds/drape. The fabric should fill the native vertical 3:4 frame naturally and read as life-size, not miniature. Do not include both waist seam and hem in one fabric-detail image; avoid whole skirt, full bodice, waist-to-hem crops, zoomed-out garment crops, doll-sized garments, blank bands, unrelated body parts, or face focus.

`detail-feature`
: Close crop of a product-specific buying detail in a native 3:4 portrait image: neckline, sleeve cuff, zipper, buttons, pocket, waistband, seam, hem, strap, lining, trim, hardware, or logo patch. Preserve exact placement where visible and prefer named landmarks when available. The detail should fill the frame without blank bands and with no face focus.

## Revision Pattern

When a shot is weak, revise only the failure:

```text
Regenerate only the {shot_name} image. Keep the same product identity and all reference priorities. Fix: {specific_failure}. Do not change color, silhouette, fabric, neckline, sleeve length, hem length, closure details, or print/logo placement. Do not show a recognizable model face, eyes, nose, mouth, full face, facial profile, portrait crop, or face focus.
```
