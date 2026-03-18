from pathlib import Path
from utils.text import get_text_chunks


def save_to_disk(directory: Path, filename: str, content: bytes) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    dest = directory / filename
    dest.write_bytes(content)
    return dest


def fetch_chunk_from_disk(file_path: str, chunk_index: int) -> str | None:
    path = Path(file_path)
    if not path.is_file():
        return None

    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        chunks = get_text_chunks(text, max_sentences_per_chunk=3, overlap_sentences=1)
        if 0 <= chunk_index < len(chunks):
            return chunks[chunk_index]
        return None
    except Exception as e:
        print(f"Failed to read chunk from disk for {file_path}: {e}")
        return None
