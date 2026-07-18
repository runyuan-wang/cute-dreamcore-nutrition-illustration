MOTIFS = {
    "mushroom_guide": "a tiny beige mushroom guide with a leaf satchel",
    "microbe_sprites": "tiny friendly abstract microbe sprites with round faces",
    "cloud_paths": "soft cloud paths and curved stepping-stone trails",
    "science_boards": "blank rounded science signboards reserved for later text overlays",
    "chinese_clouds": "subtle original auspicious-cloud-inspired curves",
    "garden_bridge": "a small rounded garden bridge with soft tiled-roof accents",
    "stars": "small soft stars and five-petal flowers",
    "moon": "one gentle milk-white moon or soft sun",
}


def enabled_motifs(request) -> list[str]:
    result = ["cloud_paths", "science_boards"]
    if request.include_mushrooms:
        result.append("mushroom_guide")
    if request.include_microbe_characters:
        result.append("microbe_sprites")
    if request.include_chinese_motifs:
        result.extend(["chinese_clouds", "garden_bridge"])
    if request.include_stars:
        result.append("stars")
    if request.include_moon:
        result.append("moon")
    return result
