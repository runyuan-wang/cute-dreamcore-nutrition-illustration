from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Citation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    citation_id: str
    text: str
    url: str | None = None


class NutritionClaim(BaseModel):
    """A supported claim that is allowed to drive a visual concept."""

    model_config = ConfigDict(extra="forbid")
    claim_id: str = Field(min_length=1)
    claim_text: str = Field(min_length=1)
    plain_language_message: str = Field(min_length=1)
    evidence_source: str = Field(min_length=1)
    citation_id: str = Field(min_length=1)
    population: str = Field(min_length=1)
    evidence_strength: str = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)
    limitations: List[str] = Field(default_factory=list)
    allowed_visual_metaphors: List[str] = Field(default_factory=list)
    prohibited_visual_implications: List[str] = Field(default_factory=list)

    @field_validator("claim_text", "plain_language_message", "evidence_source")
    @classmethod
    def no_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must not be blank")
        return value.strip()
