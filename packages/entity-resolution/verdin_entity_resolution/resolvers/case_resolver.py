"""Case resolver — match consumer name to case client records."""

from verdin_entity_resolution.base import CaseCandidate, EntityResolutionResult, ResolutionContext
from verdin_entity_resolution.constants import (
    MatchedEntityType,
    ResolutionMethod,
    ResolutionStatus,
)
from verdin_entity_resolution.helpers import name_similarity

_MATCH_THRESHOLD = 0.65
_AMBIGUITY_GAP = 0.08


class CaseResolver:
    name = "case"

    def resolve(self, context: ResolutionContext) -> EntityResolutionResult | None:
        consumer_name = context.metadata.get("consumer_name")
        if not isinstance(consumer_name, str) or not consumer_name.strip():
            return EntityResolutionResult(
                entity_type=MatchedEntityType.CASE,
                matched_entity_id=context.document_case_id,
                confidence_score=0.55,
                resolution_status=ResolutionStatus.MATCHED,
                resolution_method=ResolutionMethod.RULES,
                reasoning="Document linked to case; no consumer name to verify",
            )

        scored: list[tuple[CaseCandidate, float]] = []
        for case in context.cases:
            score = name_similarity(consumer_name, case.client_name)
            if score > 0:
                scored.append((case, score))

        if not scored:
            return EntityResolutionResult(
                entity_type=MatchedEntityType.CASE,
                matched_entity_id=None,
                confidence_score=0.1,
                resolution_status=ResolutionStatus.UNMATCHED,
                resolution_method=ResolutionMethod.RULES,
                reasoning="No case client name matched extracted consumer name",
            )

        scored.sort(key=lambda item: item[1], reverse=True)
        best_case, best_score = scored[0]
        candidates = tuple(case.id for case, _ in scored[:5])

        if best_score < _MATCH_THRESHOLD:
            return EntityResolutionResult(
                entity_type=MatchedEntityType.CASE,
                matched_entity_id=None,
                confidence_score=best_score,
                resolution_status=ResolutionStatus.UNMATCHED,
                resolution_method=ResolutionMethod.RULES,
                reasoning="Consumer name similarity below match threshold",
                candidate_entity_ids=candidates,
            )

        if len(scored) > 1 and (best_score - scored[1][1]) < _AMBIGUITY_GAP:
            return EntityResolutionResult(
                entity_type=MatchedEntityType.CASE,
                matched_entity_id=None,
                confidence_score=best_score,
                resolution_status=ResolutionStatus.AMBIGUOUS,
                resolution_method=ResolutionMethod.RULES,
                reasoning="Multiple cases have similar client names",
                candidate_entity_ids=candidates,
            )

        return EntityResolutionResult(
            entity_type=MatchedEntityType.CASE,
            matched_entity_id=best_case.id,
            confidence_score=best_score,
            resolution_status=ResolutionStatus.MATCHED,
            resolution_method=ResolutionMethod.RULES,
            reasoning=f"Consumer name matched case client '{best_case.client_name}'",
            candidate_entity_ids=candidates,
        )
