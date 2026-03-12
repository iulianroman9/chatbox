import uuid
from pathlib import Path
from fastapi import UploadFile
from sqlalchemy.orm import Session
from db.models import FileRecord, UserRecord

UPLOAD_DIR = Path("files")


async def save_file_for_user(
    file: UploadFile, current_user: UserRecord, db: Session
) -> FileRecord:
    safe_original_name = Path(file.filename).name
    random_name = f"{uuid.uuid4().hex}_{safe_original_name}"

    user_dir = UPLOAD_DIR / str(current_user.id)
    user_dir.mkdir(parents=True, exist_ok=True)

    dest = user_dir / random_name

    content = await file.read()
    dest.write_bytes(content)

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

    return db_file
