import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.models import FileContentRecord, FileRecord, UserRecord

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

    content = await file.read()
    dest.write_bytes(content)

    # store file metadata in files table
    db_file = FileRecord(
        user_id=current_user.id,
        original_name=safe_original_name,
        generated_name=random_name,
        content_type=file.content_type or "application/octet-stream",
        size=len(content),
        path=str(dest),
    )

    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    # store file content as tsvector in postgres
    text_content = content.decode("utf-8", errors="ignore")
    content_record = FileContentRecord(
        file_id=db_file.id, content_tsv=func.to_tsvector("english", text_content)
    )

    db.add(content_record)
    db.commit()

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
