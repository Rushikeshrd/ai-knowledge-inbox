"""
Chunking strategy: fixed-size character windows with overlap, splitting on
paragraph/sentence boundaries where possible.

Why this approach (vs. token-based or semantic chunking):
- Single-user, low-volume inbox -> optimizing for simplicity and predictability
  beats squeezing out the last bit of retrieval quality.
- Character-based sizing needs no tokenizer dependency and is "close enough"
  to token count for English text (~4 chars/token) for our purposes.
- Overlap preserves context across chunk boundaries so an answer-relevant
  sentence split across two windows isn't lost entirely from either chunk.
- Preferring to break on paragraph/sentence boundaries (instead of a hard
  character cut) keeps each chunk semantically coherent, which matters more
  for embedding quality than hitting an exact size.
"""

from app.config import get_settings

SENTENCE_BREAKS = (". ", "! ", "? ", "\n")


def chunk_text(text: str) -> list[str]:
    settings = get_settings()
    size = settings.chunk_size_chars
    overlap = settings.chunk_overlap_chars

    text = text.strip()
    if not text:
        return []

    if len(text) <= size:
        return [text]

    chunks: list[str] = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + size, text_len)

        if end < text_len:
            window = text[start:end]
            best_break = -1
            for marker in SENTENCE_BREAKS:
                idx = window.rfind(marker)
                if idx > best_break:
                    best_break = idx + len(marker)
            # Only use the soft break if it doesn't shrink the chunk too much.
            if best_break > size * 0.4:
                end = start + best_break

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_len:
            break
        start = max(end - overlap, start + 1)

    return chunks
