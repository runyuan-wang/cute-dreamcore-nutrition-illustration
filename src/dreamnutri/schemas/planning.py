"""Typed contracts for the two text-planning stages.

The renderer intentionally keeps these contracts small.  A text provider must
first extract teaching priorities and then produce a structured visual plan;
only validated Pydantic values are handed to the existing style/compiler code.
"""

from typing import List

from pydantic import BaseModel, ConfigDict, Field


class TeachingPriorityPlan(BaseModel):
    """Stage one: audience-facing priorities for an arbitrary topic."""

    model_config = ConfigDict(extra="forbid")

    topic: str = Field(min_length=1)
    audience: str = Field(min_length=1)
    educational_goal: str = Field(min_length=1)
    teaching_priorities: List[str] = Field(min_length=1, max_length=3)


class PlannedTeachingMessage(BaseModel):
    """A compact bilingual message that can be overlaid without guessing."""

    model_config = ConfigDict(extra="forbid")

    message_id: str = Field(min_length=1)
    text_en: str = Field(min_length=1)
    text_zh_cn: str = Field(min_length=1)
    visual_metaphor: str = Field(min_length=1)


class StructuredVisualSpec(BaseModel):
    """Stage two: structured visual directions and bilingual display copy."""

    model_config = ConfigDict(extra="forbid")

    topic: str = Field(min_length=1)
    title_en: str = Field(min_length=1)
    title_zh_cn: str = Field(min_length=1)
    subtitle_en: str = Field(min_length=1)
    subtitle_zh_cn: str = Field(min_length=1)
    world_name: str = Field(min_length=1)
    hero_island_name: str = Field(min_length=1)
    teaching_messages: List[PlannedTeachingMessage] = Field(min_length=1, max_length=3)
    secondary_island_names: List[str] = Field(default_factory=list, max_length=7)
    visual_motifs: List[str] = Field(min_length=1, max_length=12)
    image_prompt_guidance: str = Field(min_length=1)


# Descriptive aliases make the two stages easy to discover for callers while
# retaining one canonical Pydantic type for validation and serialization.
TeachingPriorityExtraction = TeachingPriorityPlan
VisualSpecPlan = StructuredVisualSpec


class PlanningMetadata(BaseModel):
    """Provenance retained in ``visual_spec.json`` and generation manifests."""

    model_config = ConfigDict(extra="forbid")

    status: str = "planned"
    provider: str = "unknown"
    model: str | None = None
    stages: List[str] = Field(default_factory=list)
    response_ids: List[str] = Field(default_factory=list)
    injected: bool = False
    error: str | None = None
    teaching_priorities: List[str] = Field(default_factory=list)
    visual_spec_source: str = "text_planner"


class PlanningResult(BaseModel):
    """Validated result of both explicit planning stages."""

    model_config = ConfigDict(extra="forbid")

    priority_plan: TeachingPriorityPlan
    visual_spec: StructuredVisualSpec
    metadata: PlanningMetadata
