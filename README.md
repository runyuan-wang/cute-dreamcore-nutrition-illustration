# Cute Chinese Dreamcore Nutrition Illustration

> Turn evidence-based nutrition knowledge into adorable Chinese dreamcore floating worlds.

**Science first. Teaching second. Dreamlike visual storytelling third.**

This standalone, open-source Python project turns verified nutrition claims into an inspectable visual package: normalized facts, teaching messages, a floating-island world plan, modular image prompts, negative prompts, bilingual captions, accessible alt text, quality checks, and an optional rendered poster.

It is designed by a Chinese Registered Dietitian to combine evidence-based nutrition communication with an original cute Chinese dreamcore visual system. It supports science communication; it does not provide diagnosis, treatment, prescriptions, or individualized medical advice.

## Why this project

The project deliberately separates four layers:

1. **Scientific truth** — supported claims, population scope, limitations, and citations.
2. **Teaching messages** — short, audience-appropriate educational statements.
3. **Visual world** — floating islands, food residents, microbe sprites, clouds, bridges, and gentle Chinese-inspired motifs.
4. **Text overlay** — readable titles, callouts, captions, and citations added programmatically after image generation.

Image models are not asked to reason about evidence or render long accurate text. The canonical source of every downstream artifact is `visual_spec.json`.

## Signature style

Every poster is a self-contained miniature nutrition world suspended in a creamy pastel sky: a hero island, satellite food islands, cloud paths, miniature gardens, friendly microbe neighborhoods, a tiny mushroom guide, soft stars and flowers, and subtle auspicious-cloud or garden-bridge motifs. The mood is warm, whimsical, bright, and comforting—not horror dreamcore, liminal, dark, uncanny, or generic corporate medical art.

## Installation

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

No API key is required for the default offline path.

## Offline quick start

```bash
dreamnutri generate \
  --topic "Dietary Fiber and Gut Health" \
  --audience "general adults" \
  --language en \
  --use-case social_poster \
  --aspect-ratio 4:5 \
  --provider mock \
  --output outputs/fiber-poster
```

The command creates a complete package including `layout_mock_preview.png` and `text_overlay_mock_preview.png`. Both are diagnostic layout previews labeled **LAYOUT MOCK — NOT FINAL ARTWORK**. They are not illustrations and cannot demonstrate artistic style fidelity.

## Optional image provider

Copy `.env.example` to `.env` or export variables in the shell:

```bash
export OPENAI_API_KEY="..."
export OPENAI_IMAGE_MODEL="your-approved-image-model"
export OPENAI_IMAGE_TIMEOUT_SECONDS=120
```

Then run:

```bash
dreamnutri generate \
  --request examples/dietary-fiber-gut-health/request.json \
  --provider openai \
  --output outputs/fiber-openai
```

The optional adapter reads credentials only from the environment, never logs keys, records provider metadata, and fails clearly on timeout or access errors. It does not silently switch models. Provider terms determine generated-image rights.

When the real provider succeeds, the package contains `illustration_raw.png` and `illustration_final.png`. When it is unavailable, the pipeline stops honestly after the prompt package and labeled mock previews; it never creates or reuses `illustration_final.png`.

## CLI

```bash
dreamnutri generate --request examples/dietary-fiber-gut-health/request.json --provider mock
dreamnutri validate outputs/fiber-poster/visual_spec.json
dreamnutri from-lesson \
  --lesson-spec ../nutrition-lesson-generator/output/lesson_spec.json \
  --slide 4 --use-case ppt_section --provider mock
```

The lesson integration consumes only the external JSON contract and does not import the other repository's Python package.

## Output package

Each run contains `request.json`, `normalized_facts.json`, `teaching_messages.json`, `visual_spec.json`, `visual_brief.md`, `image_prompt.md`, `negative_prompt.md`, bilingual captions and alt text, `citations.md`, JSON/Markdown quality reports, a generation manifest, `layout_mock_preview.png`, `text_overlay_mock_preview.png`, and `comparison_contact_sheet.png`. Real-provider runs additionally contain `illustration_raw.png` and `illustration_final.png`.

## Science-safety design

Every health-related visual begins with a supplied or curated `NutritionClaim`. The package distinguishes evidence-supported fact, educational interpretation, and visual metaphor. Causal overstatement, treatment promises, unsupported numbers, random citations, and population-scope loss are rejected or downgraded to a clearly marked concept-only package.

Food is not moralized, body size is not stigmatized, and symbolic scenery is never presented as literal anatomy. Limitations remain in the package even when they are not printed on the poster.

## Text-overlay architecture

The raw image prompt explicitly asks for clean safe zones and no long embedded text. Pillow then wraps, fits, contrasts, and renders titles, subtitles, up to three callouts, citations, and a project signature. System fonts are used through configurable paths; no font files are bundled.

Recommended fonts: Noto Sans, Noto Sans CJK SC, Source Han Sans, or an accessible local sans-serif fallback.

## Limitations

The MVP has a small curated fact set and no literature retrieval. The deterministic geometric mock is deliberately limited to layout/overlay testing. It cannot pass the artistic style-fidelity checklist. Real provider output requires human review for visual fidelity, scientific interpretation, accessibility, and licensing.

## Roadmap

- More curated nutrition evidence adapters.
- Human-in-the-loop visual review cards.
- Provider adapters with explicit model capability metadata.
- More layout templates and accessible export formats.

## License and originality

Code is released under the MIT License. Example JSON and text are project-original. Generated images are subject to the selected provider's terms. No copyrighted characters, copied art, third-party font files, living-artist imitation, or franchise assets are included. The project name and visual system should be treated as project identifiers rather than an assertion of trademark registration.

## Author

Designed by a Chinese Registered Dietitian to combine evidence-based nutrition communication with an original cute Chinese dreamcore visual system.
