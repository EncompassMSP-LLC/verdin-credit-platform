"""Account resolver — match creditor, bureau, and masked account number."""

from verdin_entity_resolution.base import AccountCandidate, EntityResolutionResult, ResolutionContext
from verdin_entity_resolution.constants import (
    MatchedEntityType,
    ResolutionMethod,
    ResolutionStatus,
)
from verdin_entity_resolution.helpers import creditor_similarity, last_four_digits, normalize_text

_MATCH_THRESHOLD = 0.7
_AMBIGUITY_GAP = 0.1


class AccountResolver:
    name = "account"

    def _score_account(
        self,
        context: ResolutionContext,
        account: AccountCandidate,
    ) -> float:
        score = 0.0
        creditor = context.metadata.get("creditor")
        collection_agency = context.metadata.get("collection_agency")
        bureau = context.metadata.get("bureau")
        account_number = context.metadata.get("account_number_masked")

        creditor_value = creditor if isinstance(creditor, str) else None
        agency_value = collection_agency if isinstance(collection_agency, str) else None
        creditor_score = max(
            creditor_similarity(creditor_value, account.creditor_name),
            creditor_similarity(agency_value, account.creditor_name),
        )
        score += creditor_score * 0.45

        if isinstance(bureau, str) and normalize_text(bureau) == normalize_text(account.bureau):
            score += 0.2

        extracted_last4 = last_four_digits(
            account_number if isinstance(account_number, str) else None
        )
        account_last4 = last_four_digits(account.account_number_masked)
        if extracted_last4 and account_last4 and extracted_last4 == account_last4:
            score += 0.35

        balance = context.metadata.get("balance")
        if isinstance(balance, (int, float)) and account.balance is not None:
            if abs(float(balance) - account.balance) < 1.0:
                score += 0.1

        return min(score, 0.99)

    def resolve(self, context: ResolutionContext) -> EntityResolutionResult | None:
        if not context.accounts:
            return EntityResolutionResult(
                entity_type=MatchedEntityType.ACCOUNT,
                matched_entity_id=None,
                confidence_score=0.0,
                resolution_status=ResolutionStatus.UNMATCHED,
                resolution_method=ResolutionMethod.RULES,
                reasoning="No accounts available for case",
            )

        scored: list[tuple[AccountCandidate, float]] = [
            (account, self._score_account(context, account)) for account in context.accounts
        ]
        scored.sort(key=lambda item: item[1], reverse=True)
        best_account, best_score = scored[0]
        candidates = tuple(
            account.id for account, score in scored if score >= _MATCH_THRESHOLD * 0.8
        )[:5]

        if best_score < _MATCH_THRESHOLD:
            return EntityResolutionResult(
                entity_type=MatchedEntityType.ACCOUNT,
                matched_entity_id=None,
                confidence_score=best_score,
                resolution_status=ResolutionStatus.UNMATCHED,
                resolution_method=ResolutionMethod.RULES,
                reasoning="No account met match threshold",
                candidate_entity_ids=candidates,
            )

        if len(scored) > 1 and (best_score - scored[1][1]) < _AMBIGUITY_GAP:
            return EntityResolutionResult(
                entity_type=MatchedEntityType.ACCOUNT,
                matched_entity_id=None,
                confidence_score=best_score,
                resolution_status=ResolutionStatus.AMBIGUOUS,
                resolution_method=ResolutionMethod.RULES,
                reasoning="Multiple accounts scored similarly",
                candidate_entity_ids=candidates,
            )

        return EntityResolutionResult(
            entity_type=MatchedEntityType.ACCOUNT,
            matched_entity_id=best_account.id,
            confidence_score=best_score,
            resolution_status=ResolutionStatus.MATCHED,
            resolution_method=ResolutionMethod.RULES,
            reasoning=f"Matched account '{best_account.creditor_name}'",
            candidate_entity_ids=candidates,
        )
