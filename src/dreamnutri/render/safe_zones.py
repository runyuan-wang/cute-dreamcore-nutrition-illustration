from dreamnutri.schemas.request import IllustrationRequest
from dreamnutri.schemas.visual import SafeZone


def zones_for(request: IllustrationRequest) -> tuple[SafeZone, SafeZone]:
    if request.aspect_ratio == "16:9":
        return SafeZone(x=0.06, y=0.08, width=0.46, height=0.2), SafeZone(x=0.06, y=0.78, width=0.56, height=0.14)
    if request.aspect_ratio == "9:16":
        return SafeZone(x=0.08, y=0.05, width=0.84, height=0.15), SafeZone(x=0.08, y=0.86, width=0.84, height=0.09)
    if request.aspect_ratio == "1:1":
        return SafeZone(x=0.08, y=0.06, width=0.84, height=0.16), SafeZone(x=0.08, y=0.82, width=0.84, height=0.12)
    return SafeZone(x=0.08, y=0.06, width=0.84, height=0.18), SafeZone(x=0.08, y=0.84, width=0.84, height=0.11)


def pixel_box(zone: SafeZone, width: int, height: int) -> tuple[int, int, int, int]:
    return (round(zone.x * width), round(zone.y * height), round((zone.x + zone.width) * width), round((zone.y + zone.height) * height))
