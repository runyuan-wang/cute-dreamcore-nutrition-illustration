from dreamnutri.schemas.evidence import NutritionClaim
from dreamnutri.schemas.request import IllustrationRequest
from dreamnutri.schemas.visual import Composition, VisualWorld


ANTI_STYLE = [
    "horror", "dark dreamcore", "eerie liminal space", "grotesque anatomy", "exposed organs",
    "disgusting digestive imagery", "body horror", "illness fear", "body-shaming", "dramatic weight-loss imagery",
    "sad food characters", "excessive medical equipment", "generic corporate vector art", "overly realistic clinical anatomy",
    "unreadable text", "random letters", "watermark", "logo", "copyrighted characters", "living-artist imitation",
    "cluttered composition", "muddy colors", "neon colors", "hypersexualized characters", "unsafe child imagery",
]


def _section(title: str, body: str) -> str:
    return f"{title}: {body.strip()}"


def build_image_prompt(request: IllustrationRequest, claims: list[NutritionClaim], world: VisualWorld, composition: Composition) -> str:
    foods = ", ".join(request.food_examples) if request.food_examples else "age-appropriate plant foods"
    claim_summary = " ".join(claim.plain_language_message for claim in claims[:3]) or "a symbolic nutrition concept with no implied health effect"
    sections = [
        _section("Educational subject", f"Create an extremely cute science-education illustration about {request.topic} for {request.audience}."),
        _section("Visual narrative", f"Show this educational path symbolically: {claim_summary}"),
        _section("Floating-island composition", f"A large hero island named {world.hero_island.name} floats at the center, with {len(world.secondary_islands)} smaller food islands and cloud paths leading toward it. Keep the hero island symbolic, not literal anatomy. {composition.visual_focus}"),
        _section("Characters", "Include friendly round food residents, tiny abstract microbe sprites, and a smiling mushroom guide where enabled; expressions are welcoming and never distressed."),
        _section("Nutrition objects", f"Use food examples only from the supplied content: {foods}. Add miniature gardens and blank rounded science signboards."),
        _section("Chinese-inspired motifs", "Use subtle original auspicious-cloud-inspired curves, a small garden bridge, rounded tiled-roof accents, and mountain-and-cloud composition logic; do not add random Chinese characters or costume collage."),
        _section("Color and lighting", "Use Cloud Cream, Milk White, Misty Sky Blue, Mint Bean Green, Nutrition Green, Sweet Peach, Custard Yellow, Dream Lavender, and Mushroom Beige in a bright creamy pastel palette with soft warm light."),
        _section("Rendering style", "Rounded plush shapes, miniature collectible world, gentle paper-cut and clay-toy feeling, rich organized details, soft clouds, flowers, stars, and comforting Chinese childhood science-book warmth."),
        _section("Text-safe zones", f"Reserve a clean low-detail title safe zone at normalized rectangle {composition.title_safe_zone.model_dump()} and a small quiet caption safe zone at {composition.caption_safe_zone.model_dump()}."),
        _section("Scientific constraints", "Visual metaphors must not be presented as literal biological anatomy. Do not invent facts, quantities, citations, diagnoses, treatments, prevention promises, or long text. Do not render long text inside the image; use blank boards and safe zones for later programmatic overlays."),
    ]
    return "\n".join(sections)


def build_negative_prompt() -> str:
    return ", ".join(ANTI_STYLE + ["random decorative Chinese text", "symbolic scenery shown as literal scientific anatomy", "unsupported medical claim", "fake citation"])
