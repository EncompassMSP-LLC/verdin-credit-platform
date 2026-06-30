"""Entity resolution contracts."""

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from verdin_entity_resolution.constants import (
    MatchedEntityType,
    ResolutionMethod,
    ResolutionStatus,
)


@dataclass(frozen=True, slots=True)
class AccountCandidate:
    id: str
    creditor_name: str
    account_number_masked: str | None
    bureau: str
    balance: float | None


@dataclass(frozen=True, slots=True)
class CaseCandidate:
    id: str
    client_name: str
    case_number: str | None


@dataclass(frozen=True, slots=True)
class ResolutionContext:
    organization_id: str
    document_case_id: str
    metadata: dict[str, str | float | list[str] | None]
    cases: tuple[CaseCandidate, ...]
    accounts: tuple[AccountCandidate, ...]


@dataclass(frozen=True, slots=True)
class EntityResolutionResult:
    entity_type: MatchedEntityType
    matched_entity_id: str | None
    confidence_score: float
    resolution_status: ResolutionStatus
    resolution_method: ResolutionMethod = ResolutionMethod.RULES
    reasoning: str = ""
    candidate_entity_ids: tuple[str, ...] = field(default_factory=tuple)


@runtime_checkable
class EntityResolver(Protocol):
    name: str

    def resolve(self, context: ResolutionContext) -> EntityResolutionResult | None: ...
