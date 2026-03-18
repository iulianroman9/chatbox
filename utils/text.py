import re


def get_text_chunks(
    text: str, max_sentences_per_chunk=3, overlap_sentences=1
) -> list[str]:
    if not text or not text.strip():
        return []

    if overlap_sentences >= max_sentences_per_chunk:
        raise ValueError(
            "overlap_sentences must be strictly less than max_sentences_per_chunk"
        )

    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s for s in sentences if s]

    chunks = []
    start_idx = 0

    while start_idx < len(sentences):
        end_idx = min(start_idx + max_sentences_per_chunk, len(sentences))
        chunks.append(" ".join(sentences[start_idx:end_idx]))
        start_idx += max_sentences_per_chunk - overlap_sentences

    return chunks
