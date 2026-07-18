from enum import Enum
from pathlib import Path
from typing import List

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .evidence import Citation, NutritionClaim


class Language(str, Enum):
    EN = "en"
    ZH_CN = "zh-CN"
    BILINGUAL = "bilingual"


class UseCase(str, Enum):
    SOCIAL_POSTER = "social_poster"
    PPT_COVER = "ppt_cover"
    PPT_SECTION = "ppt_section"
    SQUARE_POST = "square_post"
    VERTICAL_STORY = "vertical_story"
    ARTICLE_HEADER = "article_header"
    ILLUSTRATION_ONLY = "illustration_only"


class AspectRatio(str, Enum):
    PORTRAIT = "4:5"
    SQUARE = "1:1"
    SLIDE = "16:9"
    STORY = "9:16"


class ProviderName(str, Enum):
    MOCK = "mock"
    OPENAI = "openai"


class TextOverlayMode(str, Enum):
    PROGRAMMATIC = "programmatic"
    NONE = "none"


class IllustrationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    topic: str = Field(min_length=1)
    audience: str = Field(min_length=1)
    language: Language = Language.EN
    use_case: UseCase = UseCase.SOCIAL_POSTER
    aspect_ratio: AspectRatio = AspectRatio.PORTRAIT
    width: int | None = Field(default=None, ge=320, le=4096)
    height: int | None = Field(default=None, ge=320, le=4096)
    title: str | None = None
    subtitle: str | None = None
    educational_goal: str = Field(default="Explain a nutrition concept accurately and gently.", min_length=1)
    primary_messages: List[str] = Field(default_factory=list, max_length=3)
    nutrition_claims: List[NutritionClaim] = Field(default_factory=list)
    food_examples: List[str] = Field(default_factory=list)
    population_scope: str = "general adults"
    limitations: List[str] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    style_preset: str = "cute_chinese_dreamcore_floating_islands"
    cuteness_level: int = Field(default=5, ge=1, le=5)
    dreamcore_level: int = Field(default=3, ge=1, le=5)
    floating_island_count: int = Field(default=4, ge=1, le=8)
    character_density: int = Field(default=4, ge=1, le=5)
    decorative_density: int = Field(default=4, ge=1, le=5)
    include_food_characters: bool = True
    include_microbe_characters: bool = True
    include_mushrooms: bool = True
    include_clouds: bool = True
    include_stars: bool = True
    include_moon: bool = True
    include_rainbow: bool = False
    include_chinese_motifs: bool = True
    text_overlay_mode: TextOverlayMode = TextOverlayMode.PROGRAMMATIC
    provider: ProviderName = ProviderName.MOCK
    model: str | None = None
    output_directory: str = "outputs"
    seed: int = 42

    @field_validator("topic", "audience", "population_scope", "educational_goal")
    @classmethod
    def strip_required(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("value must not be blank")
        return value

    @model_validator(mode="after")
    def infer_dimensions(self):
        dimensions = {
            "4:5": (1080, 1350),
            "1:1": (1080, 1080),
            "16:9": (1600, 900),
            "9:16": (1080, 1920),
        }
        default_width, default_height = dimensions[self.aspect_ratio]
        if self.width is None:
            self.width = default_width
        if self.height is None:
            self.height = default_height
        if self.width / self.height < 0.45 or self.width / self.height > 2.2:
            raise ValueError("width and height produce an unsupported aspect ratio")
        if self.primary_messages and len(self.primary_messages) > 3:
            raise ValueError("a poster may contain no more than 3 primary messages")
        return self

    def output_path(self) -> Path:
        return Path(self.output_directory)
