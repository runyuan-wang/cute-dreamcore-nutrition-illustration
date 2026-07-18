---
name: cute-chinese-dreamcore-nutrition-illustration
description: Transform verified nutrition information into highly cute, dreamy, Chinese-inspired floating-island science illustrations and inspectable bilingual poster packages. Use for nutrition science illustrations, nutrition posters, cute educational nutrition images, Chinese dreamcore nutrition visuals, PPT covers or section illustrations, social-media nutrition images, or visuals derived from a nutrition lesson package.
---

# Cute Chinese Dreamcore Nutrition Illustration

## Purpose

Turn evidence-based nutrition knowledge into an original, comforting miniature world: floating nutrition islands, friendly food residents, symbolic microbe sprites, cloud paths, mushrooms, stars, flowers, gentle Chinese-inspired cloud and garden motifs, and readable programmatic text overlays.

Keep the four layers separate:

1. **Scientific truth:** supported claims, population, evidence strength, citations, and limitations.
2. **Teaching messages:** one to three short audience-appropriate messages.
3. **Visual world:** metaphorical islands, characters, objects, and composition.
4. **Text overlay:** title, callouts, caption, citations, and accessibility text added after image generation.

The canonical source is `visual_spec.json`. Derive prompts, overlays, reports, captions, and images from it.

## Use and non-use

Use this skill for nutrition science illustrations, posters, PPT covers/sections, social-media visuals, article headers, and visual concepts from an external `lesson_spec.json`.

Do not use it for diagnosis, individualized treatment, supplement prescriptions, medication advice, unsupported claims, misleading before-and-after images, body-shaming, fear-based visuals, or emergency medical guidance.

## Required workflow

1. Identify topic, audience, format, language, aspect ratio, and population scope.
2. Load supplied structured claims, or use only a small curated fact set. If no evidence is available, create a concept-only package with a visible warning; never invent facts.
3. Validate claim sources, citations, numbers, causal language, treatment promises, population scope, food examples, and limitations.
4. Reduce the poster to no more than one to three primary messages.
5. Record limitations even when they will not all appear on the image.
6. Select visual metaphors and explicitly mark them as symbolic, not literal anatomy.
7. Build one hero floating island, appropriate satellite food islands, clear cloud paths, and a cozy miniature ecosystem.
8. Use the signature style: extremely cute, soft, warm, pastel, collectible, comforting, Chinese-inspired but original. Include recurring motifs such as a mushroom guide, round food residents, friendly microbe sprites, cloud paths, star markers, blank science boards, and a soft moon or sun when suitable.
9. Build a modular image prompt and negative prompt. Include clean title/caption safe zones and instruct the image model not to render long text.
10. Generate the illustration without long embedded text.
11. Add title, subtitle, up to three callouts, citation footer, and project signature programmatically using Pillow or SVG with wrapping, fitting, contrast, margins, and overflow checks.
12. Run science, style, readability, accessibility, and licensing checks.
13. Export the complete output package. For `mock`, use only `layout_mock_preview.png` and `text_overlay_mock_preview.png`, label them `LAYOUT MOCK — NOT FINAL ARTWORK`, and never create `illustration_final.png`. For a real provider, save `illustration_raw.png`, apply overlays, and then save `illustration_final.png`.

## Style guardrails

Dreamcore means soft childhood imagination, not horror. Do not use dark or eerie liminal spaces, grotesque or exposed anatomy, disgusting digestive imagery, illness fear, body-shaming, dramatic weight-loss imagery, distressed food characters, corporate medical vectors, neon/muddy colors, random letters or Chinese characters, watermarks, logos, copyrighted characters, living-artist imitation, hypersexualized characters, or unsafe child imagery.

Use subtle original auspicious-cloud curves, moon-gate silhouettes, rounded tiled-roof accents, garden bridges, paper-cut-like cloud edges, and mountain-and-cloud composition logic. Avoid costume collage, excessive dragons, repeated red lanterns, and imperial-palace clichés.

## Schema and integration rules

Use `IllustrationRequest`, `NutritionClaim`, and `VisualSpec` from the project. Every health-related concept must originate from a supplied claim or an explicitly labeled curated fact. A visual metaphor may describe a symbolic fiber garden or microbe neighborhood; it must never claim that fiber literally becomes a smiling microbe.

For Nutrition Lesson Generator integration, consume only its external `lesson_spec.json` contract. Select one cover or section slide at a time; do not import its internal Python package or automatically illustrate every slide.

## Agent handoff

For a coding agent, run the offline CLI and tests before using a real provider:

```bash
dreamnutri generate --topic "Dietary Fiber and Gut Health" --audience "general adults" --language en --use-case social_poster --aspect-ratio 4:5 --provider mock
dreamnutri validate outputs/<package>/visual_spec.json
pytest -q
```

For a multimodal agent, inspect real provider artwork against the style Bible and quality report. Confirm: floating islands, layered terrain, hero nutrition world, recognizable food/microbe characters, clouds, mushrooms, stars or flowers, soft Chinese-inspired motifs, a clean title safe zone, an educational reading path, rich detail without clutter, and no uncanny or horror mood. Never treat a programmatic mock as evidence of artistic fidelity.

Read `style/STYLE_BIBLE.md`, `style/ANTI_STYLE.md`, and `style/COMPOSITION_RULES.md` when making visual decisions. Keep provider keys in environment variables and never store secrets or hidden chain-of-thought.
