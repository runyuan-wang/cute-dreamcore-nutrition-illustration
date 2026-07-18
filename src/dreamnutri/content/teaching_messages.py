from dreamnutri.schemas.evidence import NutritionClaim
from dreamnutri.schemas.visual import TeachingMessage


def build_teaching_messages(primary_messages: list[str], claims: list[NutritionClaim]) -> list[TeachingMessage]:
    if primary_messages:
        if len(primary_messages) > 3:
            raise ValueError("A poster may contain no more than 3 primary messages.")
        messages: list[TeachingMessage] = []
        for index, message in enumerate(primary_messages, 1):
            linked = claims[min(index - 1, len(claims) - 1)].claim_id if claims else None
            messages.append(
                TeachingMessage(
                    message_id=f"message_{index:02d}",
                    headline=message.strip(),
                    supporting_claim_ids=[linked] if linked else [],
                    visual_metaphor=(claims[min(index - 1, len(claims) - 1)].allowed_visual_metaphors[0] if claims else "a symbolic floating nutrition scene"),
                )
            )
        return messages
    return [
        TeachingMessage(
            message_id=f"message_{index:02d}",
            headline=claim.plain_language_message,
            supporting_claim_ids=[claim.claim_id],
            visual_metaphor=claim.allowed_visual_metaphors[0] if claim.allowed_visual_metaphors else "a gentle symbolic nutrition scene",
        )
        for index, claim in enumerate(claims[:3], 1)
    ]
