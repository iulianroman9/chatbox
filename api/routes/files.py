from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse as FastAPIFileResponse
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import UserRecord
from models.file import FileResponse
from api.services.auth import get_current_user
from api.services.file import save_file_for_user, get_file_by_id, get_files_for_user

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
    - create remaining routes (retrieve file content)
    """
    return FileResponse.model_validate(db_file)


@router.get("/", response_model=list[FileResponse])
async def list_files(
    current_user: UserRecord = Depends(get_current_user), db: Session = Depends(get_db)
):
    files = get_files_for_user(current_user.id, db)
    return [FileResponse.model_validate(f) for f in files]


@router.get("/{file_id}", response_model=FileResponse)
async def get_file_info(
    file_id: int,
    current_user: UserRecord = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_file = get_file_by_id(file_id, current_user.id, db)

    if not db_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or access denied.",
        )

    return FileResponse.model_validate(db_file)
