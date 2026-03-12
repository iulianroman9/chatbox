from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import UserRecord
from models.file import FileResponse
from api.services.auth import get_current_user
from api.services.file import save_file_for_user

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    current_user: UserRecord = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is required."
        )

    db_file = await save_file_for_user(file, current_user, db)

    # TODO:
    """
    - create remaining routes (list files, retrieve file info, retrieve file content)
    """
    return FileResponse.model_validate(db_file)
