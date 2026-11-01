"""Output Guardrails: Anti-hallucination and Financial Commitment Validation."""

import re
from typing import Tuple


def validate_output(response_text: str, kb_sources: str) -> Tuple[bool, str]:
    """Validates generated agent response against policy guardrails.

    Returns:
        (is_valid: bool, feedback_or_reason: str)
    """
    # 1. Check for unauthorized financial commitments ($100+ without human sign-off)
    unauthorized_money_patterns = [
        r"\$\s*\d{3,}",
        r"wire transfer",
        r"direct bank deposit of",
    ]
    for pattern in unauthorized_money_patterns:
        if re.search(pattern, response_text, re.IGNORECASE):
            return False, "Response committed to unauthorized monetary payout. Escalation required."

    # 2. Check for policy contradiction (our return policy strictly states 14 calendar days / 48 hrs)
    fabricated_days = re.findall(r"(\d+)\s*(?:-|\s)?day\s*(?:return|refund)", response_text, re.IGNORECASE)
    for day in fabricated_days:
        if int(day) not in [14, 48]:
            return False, f"Response referenced an unauthorized {day}-day return window not matching policy."

    return True, "Response cleared output safety checks."
