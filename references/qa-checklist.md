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
- Background is seamless solid `#FEFEFE` wherever no product, model, or natural contact shadow appears; no pure `#FFFFFF`, gray, off-white gradient, texture, vignette, or color cast.
- Lighting is soft and commercial, without harsh theatrical shadows.
- Main image shows the full garment and full hem and is not cropped at hem, sleeves, straps, or shoulders.
- Main image has no recognizable face; hair, back of head, crown of head, or a small chin/jaw edge is acceptable only when needed for natural framing.
- No generated image shows eyes, nose, mouth, lips, full face, facial profile, portrait crop, headshot framing, or face focus.
- Product is centered and large enough for PDP use.
- Model body and hair context, if visible, is neutral and does not distract from the product.
- No internal `00-model-identity-sheet`, model-face reference output, or face anchor appears in the generated gallery.
- No props, hanger, mannequin, clutter, extra garments, watermark, or text overlay unless requested.

## Shot Coverage

- Main front image works as the first online store product image without showing a recognizable face.
- Default deliverable count is four website images unless the brief overrides it.
- Exactly zero default deliverables have visible face focus.
- `front-3q-on-model` is product-focused, crops the model face/head out, and still adds useful silhouette/depth information.
- Detail shots are sharp and actually show material or a construction feature.
- Detail shots fill the vertical 3:4 frame naturally, without huge empty top, bottom, or side bands.
- `detail-fabric` is a true close-up at believable real garment scale: fabric fills most of the frame, and the shot does not show a whole skirt, full bodice, waist-to-hem crop, or miniature/doll-sized garment effect.
- Back and side shots are supported by references or clearly flagged as inferred.

## Review Status

Use these statuses in manifests:

- `pass`: suitable for delivery.
- `warn_review`: plausible but needs human review.
- `fail_regenerate`: visible generation error, product drift, cropped main-image product or hem, recognizable face, visible eyes/nose/mouth/lips, full facial profile, portrait crop, face focus, padded/letterboxed 3:4 canvas, or detail-fabric shot that looks zoomed out or miniature.
- `fail_reference_needed`: requested view cannot be trusted without another reference.
