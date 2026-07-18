"""Injectable two-stage text planning providers.

This module deliberately uses only ``httpx`` for the production adapter.  The
renderer never pretends that the deterministic fake made a GPT request: its
provider/model and stage history are retained in the planning metadata.
"""

from __future__ import annotations

import json
import os
import re
from abc import ABC, abstractmethod
from typing import Any, Callable

from dreamnutri.schemas.evidence import NutritionClaim
from dreamnutri.schemas.planning import (
    PlanningMetadata,
    PlanningResult,
    StructuredVisualSpec,
    TeachingPriorityPlan,
    PlannedTeachingMessage,
)
from dreamnutri.schemas.request import IllustrationRequest


class TextPlannerError(RuntimeError):
    """Raised when a production text planner cannot complete honestly."""


class TextPlanner(ABC):
    """Provider contract with two explicit, independently validated stages."""

    name = "text-planner"
    model: str | None = None
    injected = False

    @abstractmethod
    def extract_teaching_priorities(
        self, request: IllustrationRequest, claims: list[NutritionClaim], food_examples: list[str]
    ) -> TeachingPriorityPlan:
        raise NotImplementedError

    @abstractmethod
    def generate_visual_spec(
        self,
        request: IllustrationRequest,
        priorities: TeachingPriorityPlan,
        claims: list[NutritionClaim],
        food_examples: list[str],
    ) -> StructuredVisualSpec:
        raise NotImplementedError

    def plan(
        self, request: IllustrationRequest, claims: list[NutritionClaim], food_examples: list[str]
    ) -> PlanningResult:
        priorities = TeachingPriorityPlan.model_validate(
            self.extract_teaching_priorities(request, claims, food_examples)
        )
        visual_spec = StructuredVisualSpec.model_validate(
            self.generate_visual_spec(request, priorities, claims, food_examples)
        )
        metadata = PlanningMetadata(
            status="planned",
            provider=self.name,
            model=self.model,
            stages=["teaching_priority_extraction", "structured_visual_spec_generation"],
            injected=bool(self.injected),
            teaching_priorities=priorities.teaching_priorities,
        )
        return PlanningResult(priority_plan=priorities, visual_spec=visual_spec, metadata=metadata)


class FakeTextPlanner(TextPlanner):
    """Deterministic, offline provider for tests and explicitly offline runs."""

    name = "fake-text-planner"
    model = "offline-deterministic-text-planner-v1"
    injected = True

    def __init__(self, response_factory: Callable[..., Any] | None = None) -> None:
        self.response_factory = response_factory
        self.calls: list[dict[str, Any]] = []

    def _custom(self, stage: str, **payload: Any) -> Any:
        if self.response_factory is None:
            return None
        return self.response_factory(stage=stage, **payload)

    def extract_teaching_priorities(self, request, claims, food_examples):
        self.calls.append({"stage": "teaching_priority_extraction", "topic": request.topic})
        custom = self._custom(
            "teaching_priority_extraction", request=request, claims=claims, food_examples=food_examples
        )
        if custom is not None:
            return TeachingPriorityPlan.model_validate(custom)
        priorities = [message.strip() for message in request.primary_messages if message.strip()][:3]
        if not priorities:
            priorities = [claim.plain_language_message for claim in claims[:3] if claim.plain_language_message.strip()]
        if not priorities:
            priorities = [
                f"Define {request.topic} in clear everyday language.",
                f"Connect {request.topic} to one familiar food or daily-life example.",
                "Use a gentle visual metaphor without implying literal anatomy.",
            ]
        return TeachingPriorityPlan(
            topic=request.topic,
            audience=request.audience,
            educational_goal=request.educational_goal,
            teaching_priorities=priorities[:3],
        )

    def generate_visual_spec(self, request, priorities, claims, food_examples):
        self.calls.append({"stage": "structured_visual_spec_generation", "topic": request.topic})
        custom = self._custom(
            "structured_visual_spec_generation",
            request=request,
            priorities=priorities,
            claims=claims,
            food_examples=food_examples,
        )
        if custom is not None:
            return StructuredVisualSpec.model_validate(custom)
        messages = []
        claim_metaphors = [claim.allowed_visual_metaphors[0] for claim in claims if claim.allowed_visual_metaphors]
        for index, headline in enumerate(priorities.teaching_priorities[:3], 1):
            metaphor = claim_metaphors[index - 1] if index <= len(claim_metaphors) else "a friendly floating garden path"
            messages.append(
                PlannedTeachingMessage(
                    message_id=f"message_{index:02d}",
                    text_en=headline,
                    text_zh_cn=f"用简单语言理解{request.topic}" if index == 1 else f"认识{request.topic}的日常例子",
                    visual_metaphor=metaphor,
                )
            )
        secondary_names = [f"{food.title()} Island" for food in food_examples[:6]]
        if not secondary_names:
            secondary_names = ["Everyday Example Island"]
        topic_slug = re.sub(r"[^A-Za-z0-9]+", " ", request.topic).strip().title() or "Nutrition"
        return StructuredVisualSpec(
            topic=request.topic,
            title_en=request.title or request.topic,
            title_zh_cn=("膳食纤维与肠道健康" if any(token in request.topic.lower() for token in ("fiber", "fibre")) else ((request.title or request.topic) if any("\u4e00" <= char <= "\u9fff" for char in (request.title or request.topic)) else f"{request.title or request.topic}科普")),
            subtitle_en=request.subtitle or request.educational_goal,
            subtitle_zh_cn=f"用温和、准确的方式解释{request.topic}",
            world_name=f"The Floating {topic_slug} Garden",
            hero_island_name="Hero Ecosystem Island",
            teaching_messages=messages,
            secondary_island_names=secondary_names,
            visual_motifs=["cloud paths", "friendly food residents", "microbe garden sprites", "mushroom guide"],
            image_prompt_guidance=(
                "Keep the educational path symbolic and welcoming; reserve clean safe zones for programmatic text."
            ),
        )


# Descriptive aliases keep the provider discoverable across integrations that
# call this abstraction a text provider rather than a planner.
OfflineTextPlanner = FakeTextPlanner
FakePlanner = FakeTextPlanner
TextPlanningProvider = TextPlanner


def _extract_json(value: Any) -> dict[str, Any]:
    """Accept JSON objects returned by common OpenAI-compatible adapters."""
    if isinstance(value, dict):
        return value
    if not isinstance(value, str):
        raise TextPlannerError("Text planner returned a non-object response.")
    text = value.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE | re.DOTALL).strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise TextPlannerError("Text planner returned invalid JSON.") from exc
    if not isinstance(parsed, dict):
        raise TextPlannerError("Text planner JSON result must be an object.")
    return parsed


class OpenAITextPlanner(TextPlanner):
    """OpenAI-compatible GPT-5.6 planner with explicit endpoint/model config."""

    name = "openai-compatible"
    injected = False

    def __init__(
        self,
        endpoint: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
        post: Callable[..., Any] | None = None,
    ) -> None:
        self.endpoint = endpoint or os.getenv("OPENAI_TEXT_ENDPOINT", "https://api.openai.com/v1/chat/completions")
        self.api_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_TEXT_MODEL", "gpt-5.6")
        self.timeout = timeout if timeout is not None else float(os.getenv("OPENAI_TEXT_TIMEOUT_SECONDS", "120"))
        self._post = post
        self.response_ids: list[str] = []

    def _request(self, stage: str, system: str, user: str) -> dict[str, Any]:
        if not self.api_key:
            raise TextPlannerError("OPENAI_API_KEY is required for GPT-5.6 planning; no request was sent.")
        try:
            import httpx
        except ImportError as exc:
            raise TextPlannerError("Install the optional httpx dependency before using GPT-5.6 planning.") from exc
        payload = {
            "model": self.model,
            # Do not force a sampling parameter: some GPT-class and
            # OpenAI-compatible routes accept only their provider default.
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "response_format": {"type": "json_object"},
        }
        post = self._post or httpx.post
        try:
            response = post(
                self.endpoint,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
        except httpx.TimeoutException as exc:
            raise TextPlannerError(f"GPT-5.6 planning timed out after {self.timeout:g}s.") from exc
        except httpx.HTTPError as exc:
            raise TextPlannerError(f"GPT-5.6 planning request failed: {exc}") from exc
        except (ValueError, TypeError) as exc:
            raise TextPlannerError("GPT-5.6 planning returned invalid JSON envelope.") from exc
        choices = data.get("choices") or []
        if not choices:
            raise TextPlannerError("GPT-5.6 planning response contained no choices.")
        content = ((choices[0].get("message") or {}).get("content"))
        if isinstance(content, list):
            content = "".join(str(part.get("text", "")) if isinstance(part, dict) else str(part) for part in content)
        result = _extract_json(content)
        if data.get("id"):
            self.response_ids.append(str(data["id"]))
        return result

    def extract_teaching_priorities(self, request, claims, food_examples):
        user = json.dumps(
            {
                "topic": request.topic,
                "audience": request.audience,
                "language": request.language,
                "educational_goal": request.educational_goal,
                "caller_messages": request.primary_messages,
                "food_examples": food_examples,
                "supplied_claim_messages": [claim.plain_language_message for claim in claims],
            },
            ensure_ascii=False,
        )
        result = self._request(
            "teaching_priority_extraction",
            "You extract up to three teaching priorities for a science-popularization illustration. Honor the requested language: use Simplified Chinese for zh-CN, English for en, and concise paired copy for bilingual. Return only JSON with keys topic, audience, educational_goal, teaching_priorities (an array of one to three non-empty strings). Do not add citations or approval gates.",
            user,
        )
        return TeachingPriorityPlan.model_validate(result)

    def generate_visual_spec(self, request, priorities, claims, food_examples):
        user = json.dumps(
            {
                "topic": request.topic,
                "audience": request.audience,
                "language": request.language,
                "priorities": priorities.model_dump(mode="json"),
                "food_examples": food_examples,
                "style_preset": request.style_preset,
            },
            ensure_ascii=False,
        )
        result = self._request(
            "structured_visual_spec_generation",
            "You generate a structured visual plan for a cute Chinese dreamcore floating-island illustration. Return only JSON matching keys topic, title_en, title_zh_cn, subtitle_en, subtitle_zh_cn, world_name, hero_island_name, teaching_messages (one to three objects with message_id, text_en, text_zh_cn, visual_metaphor), secondary_island_names (array), visual_motifs (non-empty array), image_prompt_guidance. Produce concise, meaning-equivalent English and Simplified-Chinese display copy; honor the requested language as the primary audience language. Keep metaphors symbolic, not literal anatomy.",
            user,
        )
        return StructuredVisualSpec.model_validate(result)

    def plan(self, request, claims, food_examples):
        result = super().plan(request, claims, food_examples)
        result.metadata.response_ids = list(self.response_ids)
        return result


OpenAICompatibleTextPlanner = OpenAITextPlanner
