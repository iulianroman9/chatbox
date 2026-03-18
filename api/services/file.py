import uuid
import re
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from db.models import FileContentRecord, FileRecord, UserRecord
from utils.embeddings import get_embeddings, get_query_embedding
from utils.llm import generate_rag_answer

UPLOAD_DIR = Path("files")


async def save_file_for_user(
    file: UploadFile, current_user: UserRecord, db: Session
) -> FileRecord:
    safe_original_name = Path(file.filename).name
    random_name = f"{uuid.uuid4().hex}_{safe_original_name}"

    user_dir = UPLOAD_DIR / str(current_user.id)
    user_dir.mkdir(parents=True, exist_ok=True)

    # write on disk (files/user_id/random_name)
    dest = user_dir / random_name

    try:
        content = await file.read()
        dest.write_bytes(content)
    except Exception as e:
        print(f"Disk Write Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save file to disk.",
        )

    # store file metadata in files table
    db_file = FileRecord(
        user_id=current_user.id,
        original_name=safe_original_name,
        generated_name=random_name,
        content_type=file.content_type or "application/octet-stream",
        size=len(content),
        path=str(dest),
    )

    try:
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
    except Exception as e:
        db.rollback()
        if dest.exists():
            dest.unlink()
        print(f"Database Metadata Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save file metadata to database.",
        )

    # store file in chunks as tsvector and pgvector embedding
    try:
        text_content = content.decode("utf-8", errors="ignore")
        chunks = get_text_chunks(text_content)

        if chunks:
            embeddings = get_embeddings(chunks)

            content_records = []
            for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                content_records.append(
                    FileContentRecord(
                        file_id=db_file.id,
                        chunk_index=index,
                        content_tsv=func.to_tsvector("english", chunk),
                        embedding=embedding,
                    )
                )

            db.add_all(content_records)
            db.commit()

    except Exception as e:
        db.rollback()
        print(f"processing failed for file {db_file.id}: {e}")

    return db_file


def get_files_for_user(user_id: int, db: Session) -> list[FileRecord]:
    return db.query(FileRecord).filter(FileRecord.user_id == user_id).all()


def get_file_by_id(file_id: int, user_id: int, db: Session) -> FileRecord | None:
    return (
        db.query(FileRecord)
        .filter(FileRecord.id == file_id, FileRecord.user_id == user_id)
        .first()
    )


def get_file_for_download(file_id: int, user_id: int, db: Session) -> FileRecord:
    db_file = get_file_by_id(file_id, user_id, db)

    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or access denied.",
        )

    file_path = Path(db_file.path)
    if not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File is missing from the server.",
        )

    return db_file


def search_user_files_embedding(query_string: str, user_id: int, db: Session):
    query_vector = get_query_embedding(query_string)

    similarity = (1 - FileContentRecord.embedding.cosine_distance(query_vector)).label(
        "similarity"
    )

    matching_chunks = (
        db.query(FileContentRecord, similarity)
        .join(FileRecord)
        .filter(FileRecord.user_id == user_id)
        .order_by(similarity.desc())
        .all()
    )

    unique_files = []
    seen_file_ids = set()

    for chunk, chunk_rank in matching_chunks:
        if chunk.file_id not in seen_file_ids:
            file_record = chunk.file

            search_result = {
                "id": file_record.id,
                "original_name": file_record.original_name,
                "generated_name": file_record.generated_name,
                "content_type": file_record.content_type,
                "size": file_record.size,
                "created_at": file_record.created_at,
                "rank": chunk_rank,
                "chunk_index": chunk.chunk_index,
            }

            unique_files.append(search_result)
            seen_file_ids.add(chunk.file_id)

    return unique_files


def search_user_files(query_string: str, user_id: int, db: Session):
    if not query_string.strip():
        return []

    ts_query = func.websearch_to_tsquery("english", query_string)
    rank = func.ts_rank(FileContentRecord.content_tsv, ts_query).label("rank")

    matching_chunks = (
        db.query(FileContentRecord, rank)
        .join(FileRecord)
        .filter(
            FileRecord.user_id == user_id,
            FileContentRecord.content_tsv.op("@@")(ts_query),
        )
        .order_by(desc(rank))
        .all()
    )

    unique_files = []
    seen_file_ids = set()

    for chunk, chunk_rank in matching_chunks:
        if chunk.file_id not in seen_file_ids:
            file_record = chunk.file

            search_result = {
                "id": file_record.id,
                "original_name": file_record.original_name,
                "generated_name": file_record.generated_name,
                "content_type": file_record.content_type,
                "size": file_record.size,
                "created_at": file_record.created_at,
                "rank": chunk_rank,
                "chunk_index": chunk.chunk_index,
            }

            unique_files.append(search_result)
            seen_file_ids.add(chunk.file_id)

    return unique_files


# def get_text_chunks(text: str, chunk_size: int = 100, overlap: int = 20) -> list[str]:
#     if not text:
#         return []

#     chunks = []
#     start = 0

#     while start < len(text):
#         end = start + chunk_size
#         chunks.append(text[start:end])
#         start += chunk_size - overlap

#     return chunks


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


def search_chunks_hybrid(query_string: str, user_id: int, db: Session, limit: int = 5):
    if not query_string.strip():
        return []

    query_vector = get_query_embedding(query_string)
    vector_results = (
        db.query(FileContentRecord)
        .join(FileRecord)
        .filter(FileRecord.user_id == user_id)
        .order_by(FileContentRecord.embedding.cosine_distance(query_vector))
        .limit(60)
        .all()
    )

    ts_query = func.websearch_to_tsquery("english", query_string)
    fts_results = (
        db.query(FileContentRecord)
        .join(FileRecord)
        .filter(
            FileRecord.user_id == user_id,
            FileContentRecord.content_tsv.op("@@")(ts_query),
        )
        .order_by(desc(func.ts_rank(FileContentRecord.content_tsv, ts_query)))
        .limit(60)
        .all()
    )

    k = 60
    rrf_scores = {}
    chunk_map = {}

    for rank, chunk in enumerate(vector_results):
        rrf_scores[chunk.id] = rrf_scores.get(chunk.id, 0) + (1.0 / (k + rank + 1))
        chunk_map[chunk.id] = chunk

    for rank, chunk in enumerate(fts_results):
        rrf_scores[chunk.id] = rrf_scores.get(chunk.id, 0) + (1.0 / (k + rank + 1))
        chunk_map[chunk.id] = chunk

    sorted_chunk_ids = sorted(rrf_scores, key=rrf_scores.get, reverse=True)[:limit]

    return [
        (chunk_map[chunk_id], rrf_scores[chunk_id]) for chunk_id in sorted_chunk_ids
    ]


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


def search_files_hybrid(query_string: str, user_id: int, db: Session, limit: int = 20):
    if not query_string.strip():
        return []

    top_chunks = search_chunks_hybrid(query_string, user_id, db, limit=limit)

    unique_files = []
    seen_file_ids = set()

    for chunk, score in top_chunks:
        if chunk.file_id not in seen_file_ids:
            file_record = chunk.file

            search_result = {
                "id": file_record.id,
                "original_name": file_record.original_name,
                "generated_name": file_record.generated_name,
                "content_type": file_record.content_type,
                "size": file_record.size,
                "created_at": file_record.created_at,
                "best_match_chunk_index": chunk.chunk_index,
                "hybrid_score": round(score, 4),  # The raw RRF math value
                "hybrid_rank": len(unique_files) + 1,
            }

            unique_files.append(search_result)
            seen_file_ids.add(chunk.file_id)

    return unique_files


def generate_answer_from_files(query_string: str, user_id: int, db: Session) -> dict:
    top_chunks_with_scores = search_chunks_hybrid(query_string, user_id, db, limit=5)

    if not top_chunks_with_scores:
        return {
            "answer": "I couldn't find any relevant documents in your files to answer this.",
            "sources": [],
        }

    context_blocks = []
    sources_used = []

    for chunk_record, score in top_chunks_with_scores:
        chunk_text = fetch_chunk_from_disk(
            file_path=chunk_record.file.path, chunk_index=chunk_record.chunk_index
        )

        if chunk_text:
            file_name = chunk_record.file.original_name
            context_blocks.append(f"--- Source: {file_name} ---\n{chunk_text}")

            if not any(s["id"] == chunk_record.file.id for s in sources_used):
                sources_used.append(
                    {
                        "file": file_name,
                        "id": chunk_record.file.id,
                        "hybrid_score": round(score, 4),
                    }
                )

    combined_context = "\n\n".join(context_blocks)
    answer = generate_rag_answer(context_text=combined_context, user_query=query_string)

    return {"answer": answer, "sources": sources_used}
