"""
ClauseLens — Clause Taxonomy
The 11-category taxonomy from the ClauseLens research paper.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class ClauseCategory:
    id: int
    name: str
    description: str
    keywords: tuple[str, ...]


CATEGORIES: Final[list[ClauseCategory]] = [
    ClauseCategory(
        id=1,
        name="Data Collection",
        description="How and what personal data is collected from users.",
        keywords=(
            "collect", "gather", "obtain", "receive", "acquire", "record",
            "personal information", "personal data", "user data", "usage data",
            "cookies", "tracking", "log data", "device information",
        ),
    ),
    ClauseCategory(
        id=2,
        name="Data Sharing with Third Parties",
        description="How personal data is shared with external organizations.",
        keywords=(
            "share", "disclose", "transfer", "provide to", "sell", "rent",
            "third party", "third-party", "partner", "affiliate", "vendor",
            "service provider", "advertiser", "advertis", "marketing partner",
        ),
    ),
    ClauseCategory(
        id=3,
        name="Data Retention",
        description="How long personal data is stored and when it is deleted.",
        keywords=(
            "retain", "retention", "store", "keep", "delete", "deletion",
            "erasure", "purge", "archiv", "how long", "duration", "period",
            "destroy", "remove your data",
        ),
    ),
    ClauseCategory(
        id=4,
        name="Arbitration and Jurisdiction",
        description="Dispute resolution mechanisms and applicable law.",
        keywords=(
            "arbitration", "arbitrate", "dispute", "jurisdiction", "governing law",
            "class action", "waiver", "binding", "mediation", "forum", "venue",
            "applicable law", "legal proceedings", "court",
        ),
    ),
    ClauseCategory(
        id=5,
        name="Liability Limitation",
        description="Limits on the company's legal liability.",
        keywords=(
            "liability", "liable", "limitation", "disclaim", "disclaimer",
            "warranty", "warranties", "indemnif", "consequential damages",
            "indirect damages", "loss", "not responsible", "no guarantee",
            "as is", "as-is",
        ),
    ),
    ClauseCategory(
        id=6,
        name="Unilateral Change of Terms",
        description="Company's right to modify terms without prior consent.",
        keywords=(
            "modify", "amend", "change", "update", "revise", "reserves the right",
            "at our discretion", "at any time", "without notice", "sole discretion",
            "unilateral", "new terms", "updated terms",
        ),
    ),
    ClauseCategory(
        id=7,
        name="Auto-renewal and Fees",
        description="Automatic subscription renewals and billing practices.",
        keywords=(
            "auto-renew", "automatically renew", "subscription", "billing",
            "charge", "fee", "payment", "refund", "cancel", "cancellation",
            "recurring", "credit card", "payment method", "price change",
        ),
    ),
    ClauseCategory(
        id=8,
        name="Content License",
        description="Rights the company obtains over user-generated content.",
        keywords=(
            "license", "licence", "content", "intellectual property", "copyright",
            "royalt", "grant", "sublicense", "perpetual", "irrevocable",
            "worldwide", "user content", "post", "upload",
        ),
    ),
    ClauseCategory(
        id=9,
        name="Account Termination",
        description="Conditions under which accounts may be suspended or deleted.",
        keywords=(
            "terminat", "suspend", "deactivat", "close account", "delete account",
            "ban", "block", "remove access", "right to terminate", "account closure",
        ),
    ),
    ClauseCategory(
        id=10,
        name="Children and Age",
        description="Age restrictions and policies regarding minors.",
        keywords=(
            "children", "child", "minor", "age", "13", "16", "18", "coppa",
            "parental consent", "guardian", "under 13", "underage",
        ),
    ),
    ClauseCategory(
        id=11,
        name="Other",
        description="Clauses that do not fit into the above categories.",
        keywords=(),
    ),
]

# Fast lookup maps
CATEGORY_BY_NAME: Final[dict[str, ClauseCategory]] = {c.name: c for c in CATEGORIES}
CATEGORY_BY_ID: Final[dict[int, ClauseCategory]] = {c.id: c for c in CATEGORIES}
CATEGORY_NAMES: Final[list[str]] = [c.name for c in CATEGORIES]
OTHER_CATEGORY: Final[ClauseCategory] = CATEGORY_BY_NAME["Other"]
