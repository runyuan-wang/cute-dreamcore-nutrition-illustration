from dreamnutri.schemas.request import IllustrationRequest
from dreamnutri.schemas.visual import Character, Island, VisualWorld

from .motif_library import MOTIFS, enabled_motifs


def build_visual_world(request: IllustrationRequest, food_examples: list[str]) -> VisualWorld:
    motif_names = enabled_motifs(request)
    secondary = []
    for index, food in enumerate(food_examples[: max(1, request.floating_island_count - 1)], 1):
        secondary.append(
            Island(
                name=f"{food.title()} Island",
                role="food source island",
                objects=[f"round {food} resident", "tiny garden patch", "blank science board"],
                position=["upper left", "left middle", "lower left", "lower middle", "upper middle"][index % 5],
            )
        )
    characters = []
    if request.include_food_characters:
        characters.extend(Character(name=f"{food.title()} resident", role="food example", expression="cheerful and welcoming") for food in food_examples[:6])
    if request.include_microbe_characters:
        characters.append(Character(name="microbe garden sprites", role="symbolic microbiome residents", expression="curious and friendly"))
    if request.include_mushrooms:
        characters.append(Character(name="mushroom guide", role="visual guide", expression="smiling and pointing"))
    return VisualWorld(
        world_name="The Floating Fiber Garden" if "fiber" in request.topic.lower() else f"The Floating {request.topic} World",
        hero_island=Island(
            name="Hero Ecosystem Island",
            role="symbolic nutrition ecosystem, not literal anatomy",
            objects=["layered garden terrain", "microbe neighborhood", "rounded pathways", "blank science signboards"],
            position="center",
        ),
        secondary_islands=secondary,
        characters=characters,
        environment={
            "sky": "creamy pastel cloud sky with gentle depth",
            "lighting": "soft warm morning light with optional moon glow",
            "rendering": "rounded paper-cut and clay-toy miniature feeling",
            "symbolic_status": "visual metaphor only; never literal anatomy",
        },
        chinese_motifs=[MOTIFS[name] for name in motif_names if name in {"chinese_clouds", "garden_bridge"}],
        decorative_elements=[MOTIFS[name] for name in motif_names if name not in {"chinese_clouds", "garden_bridge"}],
    )
