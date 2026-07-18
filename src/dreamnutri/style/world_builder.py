from dreamnutri.schemas.planning import StructuredVisualSpec
from dreamnutri.schemas.request import IllustrationRequest
from dreamnutri.schemas.visual import Character, Island, VisualWorld

from .motif_library import MOTIFS, enabled_motifs


def build_visual_world(
    request: IllustrationRequest,
    food_examples: list[str],
    planned_spec: StructuredVisualSpec | None = None,
) -> VisualWorld:
    """Compile the validated planner result into the existing dreamcore world.

    Deterministic style rules still supply safe defaults, but planner-provided
    names and directions are retained rather than replaced by generic content.
    """
    motif_names = enabled_motifs(request)
    secondary = []
    planned_names = list(planned_spec.secondary_island_names) if planned_spec else []
    island_count = max(1, request.floating_island_count - 1)
    for index in range(min(island_count, len(planned_names) or len(food_examples))):
        food = food_examples[index] if index < len(food_examples) else "everyday example"
        name = planned_names[index] if index < len(planned_names) else f"{food.title()} Island"
        secondary.append(
            Island(
                name=name,
                role="food source island" if index < len(food_examples) else "everyday example island",
                objects=[f"round {food} resident", "tiny garden patch", "blank science board"],
                position=["upper left", "left middle", "lower left", "lower middle", "upper middle"][index % 5],
            )
        )
    if not secondary:
        secondary.append(
            Island(
                name="Everyday Example Island",
                role="symbolic example island",
                objects=["friendly example residents", "tiny garden patch", "blank science board"],
                position="upper left",
            )
        )
    characters = []
    if request.include_food_characters:
        characters.extend(
            Character(name=f"{food.title()} resident", role="food example", expression="cheerful and welcoming")
            for food in food_examples[:6]
        )
    if request.include_microbe_characters:
        characters.append(Character(name="microbe garden sprites", role="symbolic microbiome residents", expression="curious and friendly"))
    if request.include_mushrooms:
        characters.append(Character(name="mushroom guide", role="visual guide", expression="smiling and pointing"))
    world_name = planned_spec.world_name if planned_spec else (
        "The Floating Fiber Garden" if "fiber" in request.topic.lower() else f"The Floating {request.topic} World"
    )
    hero_name = planned_spec.hero_island_name if planned_spec else "Hero Ecosystem Island"
    return VisualWorld(
        world_name=world_name,
        hero_island=Island(
            name=hero_name,
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
            "planner_guidance": planned_spec.image_prompt_guidance if planned_spec else None,
            "planner_visual_motifs": ", ".join(planned_spec.visual_motifs) if planned_spec else None,
        },
        chinese_motifs=[MOTIFS[name] for name in motif_names if name in {"chinese_clouds", "garden_bridge"}],
        decorative_elements=[MOTIFS[name] for name in motif_names if name not in {"chinese_clouds", "garden_bridge"}] + (list(planned_spec.visual_motifs) if planned_spec else []),
    )
