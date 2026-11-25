"""
ClauseLens — Severity Priors
Initial expert-set severity weights from the ClauseLens research paper.

IMPORTANT: These are prior probability weights reflecting how risk-relevant
each clause CATEGORY is on average, NOT personalised risk scores.
Member 5 is responsible for computing personalized relevance scores using
these priors as inputs.

Do NOT confuse category severity with final per-user risk.
"""
from __future__ import annotations

from typing import Final

# Category name → severity prior (0.0 – 1.0)
SEVERITY_PRIORS: Final[dict[str, float]] = {
    "Arbitration and Jurisdiction":        0.90,
    "Liability Limitation":                0.85,
    "Children and Age":                    0.85,
    "Data Sharing with Third Parties":     0.80,
    "Unilateral Change of Terms":          0.75,
    "Auto-renewal and Fees":               0.70,
    "Content License":                     0.60,
    "Account Termination":                 0.60,
    "Data Retention":                      0.55,
    "Data Collection":                     0.50,
    "Other":                               0.10,
}

DEFAULT_SEVERITY: Final[float] = 0.10  # fallback for unknown categories


def get_severity(category_name: str) -> float:
    """
    Return the severity prior for the given category name.
    Returns DEFAULT_SEVERITY if the category is not found.
    """
    return SEVERITY_PRIORS.get(category_name, DEFAULT_SEVERITY)


def get_all_priors() -> dict[str, float]:
    """Return a copy of the full severity prior mapping."""
    return dict(SEVERITY_PRIORS)
