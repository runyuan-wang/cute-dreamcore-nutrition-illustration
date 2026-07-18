from typing import Any, List

from pydantic import BaseModel, ConfigDict, Field


class TeachingMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message_id: str
    headline: str
    supporting_claim_ids: List[str]
    visual_metaphor: str


class Island(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    role: str
    objects: List[str] = Field(default_factory=list)
    position: str


class Character(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    role: str
    expression: str
    symbolic_only: bool = True


class VisualWorld(BaseModel):
    model_config = ConfigDict(extra="forbid")
    world_name: str
    hero_island: Island
    secondary_islands: List[Island]
    characters: List[Character]
    environment: dict[str, Any]
    chinese_motifs: List[str]
    decorative_elements: List[str]


class SafeZone(BaseModel):
    model_config = ConfigDict(extra="forbid")
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    width: float = Field(gt=0, le=1)
    height: float = Field(gt=0, le=1)


class Composition(BaseModel):
    model_config = ConfigDict(extra="forbid")
    aspect_ratio: str
    title_safe_zone: SafeZone
    caption_safe_zone: SafeZone
    visual_focus: str
    reading_path: List[str]


class TextOverlay(BaseModel):
    model_config = ConfigDict(extra="forbid")
    overlay_id: str
    kind: str
    text_en: str
    text_zh_cn: str
    safe_zone: SafeZone
    max_lines: int = Field(default=2, ge=1, le=4)
