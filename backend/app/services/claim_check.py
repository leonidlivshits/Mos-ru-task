from __future__ import annotations

from dataclasses import dataclass

from app.services.normalization import normalize_text, tokenize


@dataclass(frozen=True)
class ClaimCheckResult:
    verified: bool
    matched_count: int


class ClaimCheckService:
    def verify(self, answer: str, private_features: list[str]) -> ClaimCheckResult:
        answer_normalized = normalize_text(answer)
        answer_tokens = {token for token in tokenize(answer) if len(token) >= 3}
        matched_count = 0

        for feature in private_features:
            feature_normalized = normalize_text(feature)
            feature_tokens = {token for token in tokenize(feature) if len(token) >= 3}

            if self._matches_feature(
                answer_normalized=answer_normalized,
                answer_tokens=answer_tokens,
                feature_normalized=feature_normalized,
                feature_tokens=feature_tokens,
            ):
                matched_count += 1

        return ClaimCheckResult(verified=matched_count > 0, matched_count=matched_count)

    def _matches_feature(
        self,
        *,
        answer_normalized: str,
        answer_tokens: set[str],
        feature_normalized: str,
        feature_tokens: set[str],
    ) -> bool:
        if not feature_normalized or not answer_normalized:
            return False

        if feature_normalized in answer_normalized:
            return True

        if len(answer_normalized) >= 4 and answer_normalized in feature_normalized:
            return True

        if not feature_tokens:
            return False

        overlap = answer_tokens & feature_tokens
        required_overlap = min(2, len(feature_tokens))
        return len(overlap) >= required_overlap
