from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import Conversation, Document, Note, Reminder, User

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats")
def stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return {
        "conversations": db.query(Conversation).filter(Conversation.user_id == user.id).count(),
        "notes": db.query(Note).filter(Note.user_id == user.id).count(),
        "reminders": db.query(Reminder).filter(Reminder.user_id == user.id, Reminder.is_done == False).count(),
        "documents": db.query(Document).filter(Document.user_id == user.id).count(),
    }
