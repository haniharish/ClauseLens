"""
ClauseLens — Summarization Prompts
System and user prompts for the AI summarization step.
"""
from __future__ import annotations

SYSTEM_PROMPT = """You are a legal document assistant for ClauseLens, an AI platform that
helps everyday users understand Terms & Conditions and Privacy Policies.

Your role is to convert complex legal language into clear, plain English
so that users can quickly understand what a clause means for them.

Rules you MUST follow:
1. Explain the clause in simple, friendly English that a non-lawyer can understand.
2. Preserve the original meaning — do NOT add, invent, or omit important facts.
3. Focus on what the COMPANY is allowed or required to do, and what it means for the USER.
4. Keep your explanation concise: 2–4 sentences maximum.
5. Do NOT provide legal advice.
6. Always end your response with this exact disclaimer on a new line:
   ⚠️ This is an AI-generated explanation for informational purposes, not legal advice.
7. Do NOT repeat the original clause verbatim.
8. Use active voice and present tense where possible."""

USER_PROMPT_TEMPLATE = """Please explain the following clause in simple English:

Category: {category}

Original Clause:
\"\"\"{clause_text}\"\"\"

Provide a 2–4 sentence plain-English explanation followed by the disclaimer."""

CONTEXT_EXPLANATION_PROMPT_TEMPLATE = """Please explain why the following clause may matter for a user with this profile context, in simple English:

Category: {category}
User Context: {user_context}

Original Clause:
\"\"\"{clause_text}\"\"\"

Rules:
- Focus only on facts present in the clause and how they relate to the stated user context.
- Do NOT invent legal rights or provide legal advice.
- Keep it to 2–4 concise sentences, followed by the disclaimer."""


def build_user_prompt(clause_text: str, category: str = "Unknown") -> str:
    return USER_PROMPT_TEMPLATE.format(
        clause_text=clause_text.strip(),
        category=category,
    )


def build_context_explanation_prompt(
    clause_text: str,
    category: str = "Unknown",
    user_context: dict[str, str] | None = None,
) -> str:
    context_str = (
        ", ".join(f"{k}: {v}" for k, v in user_context.items() if v)
        if user_context
        else "General user"
    )
    return CONTEXT_EXPLANATION_PROMPT_TEMPLATE.format(
        clause_text=clause_text.strip(),
        category=category,
        user_context=context_str,
    )
