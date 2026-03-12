from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pathlib import Path
from db.models import UserRecord
from api.services.auth import get_current_user

UPLOAD_DIR = Path("files")

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...), current_user: UserRecord = Depends(get_current_user)
):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is required."
        )

    safe_name = Path(file.filename).name
    user_dir = UPLOAD_DIR / str(current_user.id)
    user_dir.mkdir(parents=True, exist_ok=True)
    dest = user_dir / safe_name

    content = await file.read()
    dest.write_bytes(content)

    # TODO:
    """
    - extract code in a function (api/services/file.py)
    - generate random file name
    - store a db record for the file
    - create remaining routes (list files, retrieve file info, retrieve file content)
    """

    return {
        "filename": safe_name,
        "content_type": file.content_type or "application/octet-stream",
        "size": len(content),
        "path": str(dest),
    }
