from dreamnutri.content.fact_normalizer import normalize_claims
from dreamnutri.render.safe_zones import zones_for
from dreamnutri.schemas.request import IllustrationRequest
from dreamnutri.style.prompt_builder import build_image_prompt, build_negative_prompt
from dreamnutri.style.world_builder import build_visual_world
from dreamnutri.content.teaching_messages import build_teaching_messages
from dreamnutri.schemas.output import Composition


def test_prompt_includes_style_and_science_constraints():
    request = IllustrationRequest(topic="Dietary Fiber and Gut Health", audience="general adults", food_examples=["oats"])
    claims = normalize_claims([], request.topic)
    messages = build_teaching_messages([], claims)
    world = build_visual_world(request, ["oats"])
    title, caption = zones_for(request)
    composition = Composition(aspect_ratio="4:5", title_safe_zone=title, caption_safe_zone=caption, visual_focus="hero", reading_path=["food", "ecosystem"])
    prompt = build_image_prompt(request, claims, world, composition)
    assert "cute" in prompt.lower()
    assert "chinese" in prompt.lower()
    assert "floating" in prompt.lower() and "island" in prompt.lower()
    assert "not literal anatomy" in prompt.lower()
    assert "long text" in prompt.lower()


def test_negative_prompt_blocks_horror_and_grotesque_anatomy():
    negative = build_negative_prompt()
    assert "horror" in negative
    assert "grotesque anatomy" in negative
    assert "copyrighted characters" in negative
