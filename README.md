# Cute Chinese Dreamcore Nutrition Illustration

A six-stage product chain for turning an arbitrary science-popularization topic into one cute Chinese dreamcore floating-island illustration package.

## Author

**Wang Runyuan (王润圆)**

Wang Runyuan holds a master's degree in Nutrition and Food Hygiene from Kunming Medical University, is a Chinese Registered Dietitian, and serves on the secretariat of the Yunnan Astronomy Enthusiasts Association. Curious and active in science communication for many years, she is exploring how AI can support nutrition education and practical nutrition work to help more people. She designed this project to combine evidence-based nutrition communication with an original cute Chinese dreamcore visual system.

- GitHub: [@9s5bz2jvd2-lang](https://github.com/9s5bz2jvd2-lang)
- Contact: [jykmsg@163.com](mailto:jykmsg@163.com)

## Examples

![Human-supplied authentic example: a cute Chinese dreamcore nutrition illustration with floating islands and a warm pastel educational scene.](docs/images/authentic-demo-0718_1.png)

> **Human-supplied reference:** original bytes preserved (SHA-256 `4d7f583ad897190720038f0f00775aae876593166d0fe2978aa0623be06feaf2`).

### Actual bilingual overlay proof (offline fixture)

![Side-by-side zh-CN and English programmatic text overlays on the same human-supplied offline fixture, both visibly labeled FIXTURE.](docs/images/bilingual-overlay-fixture-proof.jpg)

Same supplied base image, actual zh-CN and English compositor runs. The visible `FIXTURE` label distinguishes this offline overlay proof from provider output.

## Exact product chain

1. **Topic input:** accept a science-popularization topic, audience, language, format, and optional caller-supplied content.
2. **Teaching-priority extraction:** GPT-5.6 extracts one to three audience-facing teaching priorities. The typed, injectable planner validates the result before continuing.
3. **Structured visual-spec generation:** GPT-5.6 turns those priorities into a validated structured visual plan: messages, metaphors, island world, motifs, and image direction.
4. **Dreamcore compilation:** the existing style/world compiler converts that validated plan into cute Chinese dreamcore floating-island drawing instructions, safe zones, and a negative prompt.
5. **Illustration generation:** the selected image provider generates the real artwork without long embedded text. A real-provider run writes `illustration_raw.png`.
6. **Accurate overlay and export:** Pillow selects `text_zh_cn` for Chinese runs or `text_en` for English runs, adds title/subtitle/callouts, and exports `illustration_final.png` plus the inspectable package and provenance manifest.

The renderer does not judge or rewrite the user's science content; upstream authors remain responsible for content accuracy.

## Installation

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

No API key is required for the default offline path.

## Offline development

The default offline path uses `FakeTextPlanner` plus `MockProvider` and stamps every preview **LAYOUT MOCK — NOT FINAL ARTWORK**.

```bash
PYTHONPATH=src python -m dreamnutri.cli generate \
  --topic "Dietary Fiber and Gut Health" \
  --audience "general adults" \
  --language en \
  --provider mock \
  --output outputs/fiber-poster
```

Inject `FakeTextPlanner` in tests with `generate_package(..., text_planner=FakeTextPlanner())`. It records both explicit planning stages and validates both Pydantic contracts. A production planner failure is reported as unavailable; it never silently substitutes fabricated GPT output.

## Production providers

The text planner uses existing `httpx` and an OpenAI-compatible endpoint. Configure the text stage explicitly:

```bash
export OPENAI_API_KEY="..."
export OPENAI_TEXT_MODEL="gpt-5.6"
export OPENAI_TEXT_ENDPOINT="https://api.openai.com/v1/chat/completions"
```

The image adapter remains explicit and separate:

```bash
export OPENAI_IMAGE_MODEL="your-approved-image-model"
export OPENAI_IMAGE_ENDPOINT="https://api.openai.com/v1/images/generations"

PYTHONPATH=src python -m dreamnutri.cli generate \
  --topic "Dietary Fiber and Gut Health" \
  --audience "general adults" \
  --language zh-CN \
  --provider openai \
  --output outputs/fiber-poster-real
```

Keys are not stored or logged. Provider failures are recorded without writing final artwork; `FixtureImageProvider` is test-only.

## Inspectable outputs

A run writes the request, normalized facts, two-stage planning provenance, `visual_spec.json`, image and negative prompts, bilingual captions and alt text, quality reports, mock previews, and `generation_manifest.json`. Successful real-provider or fixture-provider tests additionally write `illustration_raw.png` and `illustration_final.png`.


## Use boundary

This Skill renders caller-supplied science content; it does not validate medical claims or replace human review. Review final visuals and provider licensing before publication.

## Tests

```bash
PYTHONPATH=src pytest -q
PYTHONPATH=src python -m compileall -q src tests
```

## License and originality

Code is released under the MIT License. Examples are project-original. Generated-image rights follow the selected provider's terms; no third-party font, art, character, or franchise assets are bundled.
