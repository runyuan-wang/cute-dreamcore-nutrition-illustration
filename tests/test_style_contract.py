import unittest

from dreamnutri.content.fact_normalizer import normalize_claims
from dreamnutri.schemas.request import IllustrationRequest
from dreamnutri.style.world_builder import build_visual_world


class StyleContractTests(unittest.TestCase):
    def test_world_contains_signature_motifs(self):
        request = IllustrationRequest(topic="Dietary Fiber and Gut Health", audience="general adults")
        world = build_visual_world(request, ["oats", "beans", "vegetables"])
        self.assertTrue(world.hero_island.role.startswith("symbolic"))
        self.assertTrue(any("mushroom" in character.name for character in world.characters))
        self.assertTrue(world.chinese_motifs)
        self.assertGreaterEqual(len(world.secondary_islands), 2)
