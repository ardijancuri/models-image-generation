# Fashion Shot Patterns

Use these patterns to build concise prompts. Keep the garment identity factual and short.

## Shared Prompt Skeleton

```text
TASK:
Generate a clean ecommerce studio product image for a fashion PDP gallery.

PRODUCT IDENTITY:
{garment_identity_capsule}

REFERENCE PRIORITY:
Use the primary reference for silhouette, color, construction, proportions, and fit. Use supporting references only for the details they show.

SHOT:
{shot_name}. {shot_instruction}

OUTPUT FORMAT:
Native portrait 3:4 ecommerce website image. Fill the entire 3:4 canvas naturally. No padding, no white bars, no border, no letterboxing. Do not generate a smaller image centered on a larger white canvas.

FRAMING:
For full-body shots, keep the full head/face/hair, shoulders, full garment, and full hem visible inside the frame. For detail shots, make the garment detail fill the vertical 3:4 frame naturally with no huge empty bands.

STUDIO STYLE:
Adult generic model with visible natural face allowed, neutral ecommerce pose, seamless pure white background, soft diffused studio lighting, realistic fabric texture, natural garment drape, product fully visible unless this is a detail shot. Do not preserve or clone the reference model identity.

PRESERVE:
{must_preserve}

IDENTITY LANDMARKS:
{identity_landmarks}

AVOID:
No props, hanger, mannequin, extra accessories, new logos, altered color, changed sleeve length, changed neckline, changed hem length, changed print placement, text overlay, watermark, dramatic shadow, duplicate garment, distorted body, cropped product, cropped head or face, cropped hem, padding, white bars, border, letterboxing.
```

## Default Shots

`main-front-on-model`
: Front-facing full-body ecommerce PDP main image. Product centered, full head/face/hair and full garment visible through the hem, model pose straight and neutral, product fills the native 3:4 canvas without pasted-on white margins.

`front-3q-on-model`
: Slight three-quarter front angle. Show garment depth, drape, side seam, and silhouette while preserving the same product and any named print/logo landmarks. Keep full head/face/hair and hem visible.

`back-on-model`
: Back-facing studio image. Use only if back reference exists. If inferred, state that back details must remain minimal and avoid inventing closures, labels, straps, or decoration.

`side-on-model`
: Side-view studio image. Use only if side structure is visible or can be safely inferred. Preserve hem length, sleeve shape, drape, and garment volume. Keep full head/face/hair and hem visible.

`detail-fabric`
: Close crop of fabric texture, weave, lace, knit, sheen, print, embroidery, or surface finish. The detail should fill the native vertical 3:4 frame naturally. No model face, no unrelated body parts, no invented labels, no blank top/bottom bands.

`detail-feature`
: Close crop of a product-specific buying detail in a native 3:4 portrait image: neckline, sleeve cuff, zipper, buttons, pocket, waistband, seam, hem, strap, lining, trim, hardware, or logo patch. Preserve exact placement where visible and prefer named landmarks when available. The detail should fill the frame without blank bands.

## Revision Pattern

When a shot is weak, revise only the failure:

```text
Regenerate only the {shot_name} image. Keep the same product identity and all reference priorities. Fix: {specific_failure}. Do not change color, silhouette, fabric, neckline, sleeve length, hem length, closure details, or print/logo placement.
```
