from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import Conversation, Document, User
from app.schemas import ChatRequest, ChatResponse
from app.services.command_service import CommandService
from app.services.pdf_service import search

router = APIRouter(prefix="/api/chat", tags=["Chat"])
service = CommandService()

@router.get("/status")
def ai_status():
    from app.core.config import settings
    from app.services.ai_service import gemini_configured
    return {"connected": gemini_configured(), "model": settings.gemini_model}

@router.get("/history")
def history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Conversation).filter(Conversation.user_id == user.id).order_by(Conversation.id.asc()).limit(100).all()
    return [{"id": x.id, "role": x.role, "message": x.message, "created_at": x.created_at} for x in rows]

@router.delete("/history")
def clear_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db.query(Conversation).filter(Conversation.user_id == user.id).delete()
    db.commit()
    return {"message": "Conversation cleared"}

@router.post("/message", response_model=ChatResponse)
def message(data: ChatRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    history_rows = db.query(Conversation).filter(Conversation.user_id == user.id).order_by(Conversation.id.desc()).limit(12).all()
    history_rows.reverse()
    history = [{"role": x.role, "message": x.message} for x in history_rows]
    context = ""
    document_selected = False
    if data.document_id:
        doc = db.query(Document).filter(Document.id == data.document_id, Document.user_id == user.id).first()
        if not doc:
            return {"response": "That PDF is no longer available. Please select an uploaded PDF from the Chat dropdown.", "action": None}
        document_selected = True
        matches = search(doc.extracted_text, data.message)
        useful = [x[0] for x in matches if x[1] > 0.03]
        if useful:
            context = "\n\n---\n\n".join(useful)
        else:
            context = "[NO_RELEVANT_CONTENT_FOUND_IN_SELECTED_PDF]"
    result = service.process(db, user, data.message, history, context, document_selected=document_selected)
    db.add(Conversation(user_id=user.id, role="user", message=data.message))
    db.add(Conversation(user_id=user.id, role="assistant", message=result["response"]))
    db.commit()
    return result
