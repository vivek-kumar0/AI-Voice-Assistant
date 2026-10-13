from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import Note, User
from app.schemas import NoteCreate, NoteOut

router = APIRouter(prefix="/api/notes", tags=["Notes"])

@router.get("", response_model=list[NoteOut])
def list_notes(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Note).filter(Note.user_id == user.id).order_by(Note.id.desc()).all()

@router.post("", response_model=NoteOut)
def create_note(data: NoteCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    note = Note(user_id=user.id, content=data.content.strip())
    db.add(note); db.commit(); db.refresh(note)
    return note

@router.delete("/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user.id).first()
    if not note: raise HTTPException(404, "Note not found")
    db.delete(note); db.commit()
    return {"message": "Note deleted"}
