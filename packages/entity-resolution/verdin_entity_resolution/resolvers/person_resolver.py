"""Person resolver — consumer identity matched to case client name."""

from verdin_entity_resolution.base import EntityResolutionResult, ResolutionContext
from verdin_entity_resolution.constants import (
    MatchedEntityType,
    ResolutionMethod,
    ResolutionStatus,
)
from verdin_entity_resolution.helpers import name_similarity

_MATCH_THRESHOLD = 0.65


class PersonResolver:
    name = "person"

    def resolve(self, context: ResolutionContext) -> EntityResolutionResult | None:
        consumer_name = context.metadata.get("consumer_name")
        if not isinstance(consumer_name, str) or not consumer_name.strip():
            return None

        document_case = next(
            (case for case in context.cases if case.id == context.document_case_id),
            None,
        )
        if document_case is None:
            return EntityResolutionResult(
                entity_type=MatchedEntityType.PERSON,
                matched_entity_id=None,
                confidence_score=0.0,
                resolution_status=ResolutionStatus.UNMATCHED,
                resolution_method=ResolutionMethod.RULES,
                reasoning="Document case not found in candidate set",
            )

        score = name_similarity(consumer_name, document_case.client_name)
        if score < _MATCH_THRESHOLD:
            return EntityResolutionResult(
                entity_type=MatchedEntityType.PERSON,
                matched_entity_id=None,
                confidence_score=score,
                resolution_status=ResolutionStatus.UNMATCHED,
                resolution_method=ResolutionMethod.RULES,
                reasoning="Extracted consumer name does not match case client",
            )

        return EntityResolutionResult(
            entity_type=MatchedEntityType.PERSON,
            matched_entity_id=document_case.id,
            confidence_score=score,
            resolution_status=ResolutionStatus.MATCHED,
            resolution_method=ResolutionMethod.RULES,
            reasoning="Consumer name matches case client on linked case",
        )
