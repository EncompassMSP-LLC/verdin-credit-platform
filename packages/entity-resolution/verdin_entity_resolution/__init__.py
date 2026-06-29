"""Entity resolution engine."""

from verdin_entity_resolution.base import (
    AccountCandidate,
    CaseCandidate,
    EntityResolutionResult,
    EntityResolver,
    ResolutionContext,
)
from verdin_entity_resolution.constants import (
    MatchedEntityType,
    ResolutionMethod,
    ResolutionStatus,
)
from verdin_entity_resolution.registry import list_resolvers, resolve_entities

__all__ = [
    "AccountCandidate",
    "CaseCandidate",
    "EntityResolutionResult",
    "EntityResolver",
    "MatchedEntityType",
    "ResolutionContext",
    "ResolutionMethod",
    "ResolutionStatus",
    "list_resolvers",
    "resolve_entities",
]
