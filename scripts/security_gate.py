import re
from dataclasses import dataclass
from pathlib import Path


INJECTION_PATTERNS = (
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(all\s+)?instructions",
    r"reveal\s+(the\s+)?system\s+prompt",
    r"email\s+password(s)?\s+in\s+plain\s+text",
    r"mfa\s+not\s+required",
    r"disable\s+(mfa|multi[- ]factor authentication)",
)


@dataclass(frozen=True)
class GateDecision:
    accepted: bool
    score: float
    reasons: tuple[str, ...]


def evaluate_document(path: Path, text: str) -> GateDecision:
    """Apply cheap pre-index checks before a document becomes a vector."""
    reasons: list[str] = []
    lowered = text.lower()

    if path.parent.name != "trusted":
        reasons.append("source is outside the trusted corpus")

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            reasons.append(f"matched suspicious instruction: {pattern}")

    if "http://" in lowered or "setup.zip" in lowered:
        reasons.append("contains an unsafe link or archive reference")

    score = min(1.0, 0.25 * len(reasons))
    return GateDecision(accepted=not reasons, score=score, reasons=tuple(reasons))