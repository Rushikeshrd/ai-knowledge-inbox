from functools import lru_cache

from groq import Groq, GroqError

from app.config import get_settings
from app.exceptions import LlmError
from app.logging_config import get_logger, log_with_fields

logger = get_logger(__name__)

SYSTEM_PROMPT = (
    "You are a precise assistant answering questions using ONLY the numbered context "
    "snippets provided by the user. Rules:\n"
    "1. Base your answer strictly on the provided context. Do not use outside knowledge.\n"
    "2. When you use a fact from a snippet, cite it inline like [1], [2] matching its number.\n"
    "3. If the context does not contain enough information to answer, say so plainly instead "
    "of guessing.\n"
    "4. Be concise."
)


@lru_cache
def _get_client() -> Groq:
    settings = get_settings()
    if not settings.groq_api_key:
        raise LlmError("GROQ_API_KEY is not configured on the server.")
    return Groq(api_key=settings.groq_api_key)


def generate_answer(question: str, context_snippets: list[str]) -> str:
    settings = get_settings()

    numbered_context = "\n\n".join(f"[{i + 1}] {snippet}" for i, snippet in enumerate(context_snippets))
    user_prompt = f"Context:\n{numbered_context}\n\nQuestion: {question}"

    try:
        client = _get_client()
        completion = client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=800,
        )
    except GroqError as exc:
        raise LlmError(f"Groq API request failed: {exc}") from exc

    answer = completion.choices[0].message.content if completion.choices else None
    if not answer:
        raise LlmError("LLM returned an empty response.")

    log_with_fields(logger, 20, "llm_answer_generated", model=settings.groq_model, answer_chars=len(answer))
    return answer.strip()
