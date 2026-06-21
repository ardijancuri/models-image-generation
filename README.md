# Models Image Generation

Codex skill and helper scripts for generating traceable ecommerce fashion studio image packs from product references.

## Contents

- `SKILL.md` - Codex workflow for using the skill.
- `scripts/` - helpers for reference manifests, prompt packs, ratio checks, manifests, contact sheets, and gallery validation.
- `assets/` - reusable brief and manifest templates.
- `references/` - schema, QA, shot-pattern, and failure-mode guidance.
- `agents/` - optional agent routing metadata.

The scripts do not call an image-generation API directly. They prepare prompts, validate outputs, and preserve provenance while Codex performs image generation.

## Quick Check

```powershell
python -m compileall scripts
```
