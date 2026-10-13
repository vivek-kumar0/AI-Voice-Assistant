from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import Reminder, User
from app.schemas import ReminderCreate, ReminderOut

router = APIRouter(prefix="/api/reminders", tags=["Reminders"])

@router.get("", response_model=list[ReminderOut])
def list_reminders(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Reminder).filter(Reminder.user_id == user.id).order_by(Reminder.id.desc()).all()

@router.post("", response_model=ReminderOut)
def create_reminder(data: ReminderCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    r = Reminder(user_id=user.id, title=data.title.strip(), remind_at=data.remind_at.strip())
    db.add(r); db.commit(); db.refresh(r)
    return r

@router.patch("/{reminder_id}/complete")
def complete(reminder_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    r = db.query(Reminder).filter(Reminder.id == reminder_id, Reminder.user_id == user.id).first()
    if not r: raise HTTPException(404, "Reminder not found")
    r.is_done = True; db.commit()
    return {"message": "Reminder completed"}

@router.delete("/{reminder_id}")
def delete_reminder(reminder_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    r = db.query(Reminder).filter(Reminder.id == reminder_id, Reminder.user_id == user.id).first()
    if not r: raise HTTPException(404, "Reminder not found")
    db.delete(r); db.commit()
    return {"message": "Reminder deleted"}
