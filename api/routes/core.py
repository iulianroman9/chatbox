from fastapi import APIRouter

router = APIRouter(tags=["Core"])


@router.get("/")
def root():
    return {"message": "Chatbox API is running ok.", "version": "0.1.0"}


@router.get("/healthz")
def healthz():
    return {"status": "ok"}
