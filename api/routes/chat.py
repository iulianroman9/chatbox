from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db.database import get_db
from db.models import UserRecord
from api.services.auth import get_current_user
from utils.llm import run_agent_chat

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str


@router.post("/")
async def agentic_chat(
    request: ChatRequest,
    current_user: UserRecord = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reply = run_agent_chat(user_message=request.message, user_id=current_user.id, db=db)
    return {"reply": reply}
