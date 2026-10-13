from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import User, UserSetting
from app.schemas import SettingsUpdate

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.get("")
def get_settings(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = db.query(UserSetting).filter(UserSetting.user_id == user.id).first()
    if not s:
        s = UserSetting(user_id=user.id); db.add(s); db.commit(); db.refresh(s)
    return {"theme": s.theme, "voice_rate": s.voice_rate, "voice_enabled": s.voice_enabled}

@router.put("")
def update_settings(data: SettingsUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = db.query(UserSetting).filter(UserSetting.user_id == user.id).first()
    if not s:
        s = UserSetting(user_id=user.id); db.add(s)
    if data.theme in {"dark", "light"}: s.theme = data.theme
    if data.voice_rate is not None: s.voice_rate = max(80, min(260, data.voice_rate))
    if data.voice_enabled is not None: s.voice_enabled = data.voice_enabled
    db.commit()
    return {"theme": s.theme, "voice_rate": s.voice_rate, "voice_enabled": s.voice_enabled}
