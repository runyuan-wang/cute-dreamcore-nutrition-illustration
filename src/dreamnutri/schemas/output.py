from datetime import datetime, timezone
from typing import Any, List

from pydantic import BaseModel, ConfigDict, Field

from .evidence import Citation, NutritionClaim
from .visual import Composition, TeachingMessage, TextOverlay, VisualWorld


class ProjectMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: str = "0.2.0"
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    provider: str
    model: str | None = None


class ScienceContent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    claims: List[NutritionClaim]
    limitations: List[str]
    citations: List[Citation]


class QualityStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: str
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class VisualSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    project_metadata: ProjectMetadata
    topic: str
    audience: str
    language: str
    educational_goal: str
    science_content: ScienceContent
    teaching_messages: List[TeachingMessage]
    visual_world: VisualWorld
    composition: Composition
    image_prompt: str
    negative_prompt: str
    text_overlays: List[TextOverlay]
    alt_text: str
    alt_text_zh_cn: str
    quality_status: QualityStatus


def model_dump_jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    return value
