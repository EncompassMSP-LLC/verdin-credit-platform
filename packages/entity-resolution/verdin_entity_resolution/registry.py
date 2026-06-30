"""Entity resolver registry."""

from verdin_entity_resolution.base import EntityResolutionResult, EntityResolver, ResolutionContext
from verdin_entity_resolution.resolvers.account_resolver import AccountResolver
from verdin_entity_resolution.resolvers.case_resolver import CaseResolver
from verdin_entity_resolution.resolvers.organization_resolver import OrganizationResolver
from verdin_entity_resolution.resolvers.person_resolver import PersonResolver

_RESOLVERS: tuple[EntityResolver, ...] = (
    OrganizationResolver(),
    CaseResolver(),
    PersonResolver(),
    AccountResolver(),
)


def list_resolvers() -> tuple[EntityResolver, ...]:
    return _RESOLVERS


def resolve_entities(context: ResolutionContext) -> list[EntityResolutionResult]:
    results: list[EntityResolutionResult] = []
    for resolver in _RESOLVERS:
        result = resolver.resolve(context)
        if result is not None:
            results.append(result)
    return results
