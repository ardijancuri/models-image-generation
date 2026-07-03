# Failure Modes

Fashion product generation is identity-sensitive. Bias toward review when the model makes the image prettier but less faithful.

## High-Risk Inputs

- Single reference image for a garment that needs back or side shots.
- White, ivory, sheer, lace, mesh, sequined, metallic, reflective, or fur-like garments.
- Strong prints, logos, embroidery, typography, or asymmetric graphics.
- Folded or partially occluded garments.
- Model-worn references with unusual pose, hidden closures, or cropped hems.
- Conflicting references for color, length, neckline, or hardware.

## Common Failures

- Color drift from studio lighting.
- Changed neckline, sleeve length, hem length, or garment fit.
- Invented zippers, buttons, pockets, tags, labels, or logos.
- Pattern placement changes or mirrored asymmetric details.
- Named print/logo landmarks get replaced by generic decoration.
- Back/side views hallucinate details that were never shown.
- Detail shots become generic fabric instead of the actual garment.
- White garments disappear into `#FEFEFE` studio backgrounds.
- Padded or letterboxed canvases create white top/bottom bands or side bars instead of native 3:4 composition.
- Hands, bags, jewelry, shoes, props, or extra garments appear.

## Handling Rules

- Ask for a missing authoritative reference when a factual back/side/detail view matters.
- Mark unsupported views as inferred in the prompt pack and manifest.
- Use targeted regeneration for one failure at a time.
- Treat logo/text exactness as a manual review requirement.
- For asymmetric prints, logo patches, and complex straps, add named `identity_landmarks` to the brief before generation.
- For white garments, request visible edge separation through soft contact shadow and tonal contrast on the garment while keeping unused background areas exactly `#FEFEFE`.
- For website-ready 3:4 images, regenerate padded or letterboxed outputs instead of fixing them with white padding.
