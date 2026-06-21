# QA Checklist

Run this checklist before delivering generated ecommerce fashion images.

## Product Fidelity

- Product category, color, silhouette, neckline, sleeve length, hem length, fabric, and fit match the references.
- Seams, closures, pockets, trim, hardware, logo patches, and print placement are preserved where visible.
- Named identity landmarks are still in the correct location and have not been mirrored, shifted, simplified, or replaced by generic decoration.
- No new logos, labels, readable text, certifications, accessories, or decorative details were invented.
- Asymmetric details are not flipped unless the requested view requires it and references support it.

## Studio Requirements

- Image is a native full-frame 3:4 portrait suitable for website upload.
- Image has no padding, white bars, borders, letterboxing, or smaller centered image on a larger white canvas.
- Background is pure white or near-white studio white.
- Lighting is soft and commercial, without harsh theatrical shadows.
- Main image shows the full head/face/hair, full garment, and full hem, and is not cropped at hem, sleeves, straps, shoulders, head, or face.
- Product is centered and large enough for PDP use.
- Model is adult, generic, neutral, and does not distract from the product.
- Visible model faces look natural and generic; they do not preserve or clone the reference model identity.
- No props, hanger, mannequin, clutter, extra garments, watermark, or text overlay.

## Shot Coverage

- Main front image works as the first online store product image.
- Angle shots add useful silhouette information.
- Detail shots are sharp and actually show material or a construction feature.
- Detail shots fill the vertical 3:4 frame naturally, without huge empty top, bottom, or side bands.
- Back and side shots are supported by references or clearly flagged as inferred.

## Review Status

Use these statuses in manifests:

- `pass`: suitable for delivery.
- `warn_review`: plausible but needs human review.
- `fail_regenerate`: visible generation error or product drift.
- `fail_regenerate`: visible generation error, product drift, cropped full-body framing, or padded/letterboxed 3:4 canvas.
- `fail_reference_needed`: requested view cannot be trusted without another reference.
