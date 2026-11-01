"""Input Guardrails: PII Redaction and Prompt Injection Detection."""

import re
from typing import Tuple


def sanitize_input(text: str) -> Tuple[bool, str, str]:
    """Sanitizes user input by screening for jailbreaks and masking sensitive PII.

    Returns:
        (is_safe: bool, sanitized_text: str, reason: str)
    """
    if not text or not text.strip():
        return False, "", "Empty input provided."

    # 1. Jailbreak / Injection Detection
    injection_patterns = [
        r"ignore (all|previous|prior) instructions",
        r"system prompt override",
        r"you are now in developer mode",
        r"act as an unrestricted ai",
        r"bypass security filters",
    ]
    for pattern in injection_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False, text, "Prompt injection detected. Input blocked by security guardrails."

    sanitized = text

    # 2. PII Masking: Credit Cards (13-16 digits with optional dashes/spaces)
    sanitized = re.sub(
        r"\b(?:\d[ -]*?){13,16}\b",
        "[REDACTED_CREDIT_CARD]",
        sanitized
    )

    # 3. PII Masking: CVV (3 or 4 digits preceded by CVV/CVC)
    sanitized = re.sub(
        r"(?i)\b(cvv|cvc)\s*[:=]?\s*\d{3,4}\b",
        "[REDACTED_CVV]",
        sanitized
    )

    # 4. PII Masking: Social Security Numbers / National IDs
    sanitized = re.sub(
        r"\b\d{3}-\d{2}-\d{4}\b",
        "[REDACTED_SSN]",
        sanitized
    )

    return True, sanitized, "Input verified and passed guardrails."
