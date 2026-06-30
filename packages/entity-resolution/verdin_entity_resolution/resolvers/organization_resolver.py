"""Organization resolver — document always belongs to an organization."""

from verdin_entity_resolution.base import EntityResolutionResult, ResolutionContext
from verdin_entity_resolution.constants import (
    MatchedEntityType,
    ResolutionMethod,
    ResolutionStatus,
)


class OrganizationResolver:
    name = "organization"

    def resolve(self, context: ResolutionContext) -> EntityResolutionResult | None:
        return EntityResolutionResult(
            entity_type=MatchedEntityType.ORGANIZATION,
            matched_entity_id=context.organization_id,
            confidence_score=1.0,
            resolution_status=ResolutionStatus.MATCHED,
            resolution_method=ResolutionMethod.RULES,
            reasoning="Document is scoped to organization tenancy",
        )
