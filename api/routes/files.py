from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Query
from fastapi.responses import FileResponse as FastAPIFileResponse
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import UserRecord
from models.file import FileResponse, FileSearchResponse
from models.llm import LlmResponse
from api.services.auth import get_current_user
from api.services.file import (
    save_file_for_user,
    get_file_by_id,
    get_files_for_user,
    get_file_for_download,
    search_user_files,
    search_user_files_embedding,
    search_files_hybrid,
    generate_answer_from_files,
)

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
    return FileResponse.model_validate(db_file)


@router.get("/", response_model=list[FileResponse])
async def list_files(
    current_user: UserRecord = Depends(get_current_user), db: Session = Depends(get_db)
):
    files = get_files_for_user(current_user.id, db)
    return [FileResponse.model_validate(f) for f in files]


@router.get("/search", response_model=list[FileSearchResponse])
async def search_files(
    query: str = Query(..., description="Search query string"),
    current_user: UserRecord = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        results = search_user_files(query, current_user.id, db)
        return results

    except Exception as e:
        print(f"Error during file search: {e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while searching your files.",
        )


@router.get("/search-embedding", response_model=list[FileSearchResponse])
async def search_files_embedding(
    query: str = Query(..., description="Search query string"),
    current_user: UserRecord = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        results = search_user_files_embedding(query, current_user.id, db)
        return results

    except Exception as e:
        print(f"Error during file search: {e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while searching your files.",
        )


@router.get("/search-combined")
async def search_my_files(
    query: str = Query(..., description="The search query"),
    current_user: UserRecord = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        results = search_files_hybrid(query, current_user.id, db)
        return results
    except Exception as e:
        print(f"Search Error: {e}")
        raise HTTPException(
            status_code=500, detail="An error occurred while searching files."
        )


@router.get("/search-to-llm", response_model=LlmResponse)
async def answer_from_files(
    query: str = Query(..., description="The user's question about their files"),
    current_user: UserRecord = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        result = generate_answer_from_files(query, current_user.id, db)
        return LlmResponse.model_validate(result)

    except Exception as e:
        print(f"RAG Endpoint Error: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to generate an AI answer from the files."
        )


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


@router.get("/{file_id}/content", response_class=FastAPIFileResponse)
async def download_file(
    file_id: int,
    current_user: UserRecord = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_file = get_file_for_download(file_id, current_user.id, db)

    return FastAPIFileResponse(
        path=db_file.path,
        filename=db_file.original_name,
        media_type=db_file.content_type,
    )
