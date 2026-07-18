---
name: cute-chinese-dreamcore-nutrition-illustration
description: Turn an arbitrary science-popularization topic into one cute Chinese dreamcore floating-island illustration through the six-stage topic, GPT-5.6 planning, style compilation, image generation, language-aware overlay, and export chain.
---

# Cute Chinese Dreamcore Nutrition Illustration

## Exact purpose

Run exactly this six-stage chain and nothing broader:

1. Accept a topic, audience, language, format, and optional caller-supplied content.
2. Use the injectable GPT-5.6 text planner to extract one to three teaching priorities.
3. Use GPT-5.6 again to produce a validated structured visual specification.
4. Compile that specification with the existing cute Chinese dreamcore floating-island world/style system and prompt compiler.
5. Send the compiled instruction to the selected image provider without long embedded text.
6. Select Chinese or English overlay fields, add accurate programmatic text, and export the final science-popularization image package.

The canonical downstream source is `visual_spec.json`. Both planner stages are Pydantic-validated before compilation. Planning and image-provider provenance belongs in `generation_manifest.json` and the visual-spec metadata.

## Input and boundary

A bare arbitrary topic must reach the two explicit planning stages. Caller-supplied messages, claims, food examples, and citations remain optional inputs. Missing citations and words such as prevention, treatment, diagnosis, and numbers do not block generation. This skill is not a content-review engine and must not import another product's evidence rules or add review gates.

The world is symbolic, not literal anatomy. Keep the original cute Chinese dreamcore floating-island system: pastel sky, hero ecosystem island, food islands, cloud paths, friendly food residents, microbe sprites, mushroom guide, flowers/stars, and subtle original Chinese-inspired cloud or garden motifs.

## Provider honesty

- `FakeTextPlanner` is an explicit offline/test provider. Its model is recorded as an offline fake and is never called GPT-5.6.
- `OpenAITextPlanner` is the production OpenAI-compatible adapter. Configure `OPENAI_API_KEY`, `OPENAI_TEXT_ENDPOINT`, and `OPENAI_TEXT_MODEL` (default `gpt-5.6`). It uses `httpx`, not a heavyweight SDK.
- If production text planning is unavailable, report that stage as unavailable; do not silently fabricate a GPT result.
- `MockProvider` creates only `layout_mock_preview.png` and `text_overlay_mock_preview.png`, each labeled **LAYOUT MOCK — NOT FINAL ARTWORK**. They are not final art and do not establish artistic fidelity.
- A real image provider writes `illustration_raw.png`; only then does the program write `illustration_final.png` after overlays. `FixtureImageProvider` is an offline decoded-PNG test path, not a live provider.

## Language-aware overlays

For `language="zh-CN"`, select `text_zh_cn` for title, subtitle, and callouts. For `language="en"`, select `text_en`. Bilingual runs explicitly show both. Use an available CJK-capable system font when possible; if only a fallback is available, preserve the image and record the font warning instead of turning font availability into a content gate.

## Required verification

Run in the candidate repository:

```bash
PYTHONPATH=src pytest -q
PYTHONPATH=src python -m compileall -q src tests
```

Tests must cover: arbitrary-topic fake planning; two explicit non-empty validated stages; provider-unavailable honesty; English/Chinese overlay selection; decoded PNG fixture through raw image and final overlay; no-citation and medical/numeric pass-through; lesson import; README image/hash; and generated PNG decode/integrity. Review real images manually for the cute dreamcore world, safe zones, readability, symbolic status, and absence of uncanny or horror elements.

The authentic human-supplied demo is `docs/images/authentic-demo-0718_1.png`, SHA-256 `4d7f583ad897190720038f0f00775aae876593166d0fe2978aa0623be06feaf2`. Preserve its original bytes and label README alt text as an authentic example; never claim this repair regenerated it or proves a live API call.
