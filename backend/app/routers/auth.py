from datetime import datetime, timedelta, timezone
import hashlib, secrets
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import PasswordResetToken, User, UserSetting
from app.schemas import *
from app.core.security import create_access_token, get_current_user, hash_password, verify_password
from app.core.config import settings
from app.services.email_service import send_password_reset_email

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

def user_out(u):
    return UserOut.model_validate(u)

@router.post("/register", response_model=TokenResponse)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter((User.username == data.username) | (User.email == data.email)).first():
        raise HTTPException(409, "Username or email is already registered")
    user = User(username=data.username.strip(), email=data.email.lower(), password_hash=hash_password(data.password), full_name=data.full_name.strip())
    db.add(user); db.flush()
    db.add(UserSetting(user_id=user.id))
    db.commit()
    return TokenResponse(access_token=create_access_token(user.id), user=user_out(user))

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username.strip()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid username or password")
    return TokenResponse(access_token=create_access_token(user.id), user=user_out(user))

@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user

@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    # Always return the same message so the endpoint does not reveal whether an email is registered.
    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user:
        return {"message": "If an account exists for this email, a password reset link has been sent."}

    raw_token = secrets.token_urlsafe(48)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)

    # Invalidate older unused links for this account.
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used == False,
    ).update({"used": True}, synchronize_session=False)

    reset = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(reset)
    db.commit()

    reset_url = f"{settings.frontend_url.rstrip('/')}/reset-password?token={raw_token}"
    try:
        send_password_reset_email(user.email, reset_url)
    except Exception as exc:
        db.delete(reset)
        db.commit()
        raise HTTPException(503, "Password reset email could not be sent. Please try again later.") from exc

    return {"message": "If an account exists for this email, a password reset link has been sent."}


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_hash = hashlib.sha256(data.token.encode()).hexdigest()
    reset = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash,
        PasswordResetToken.used == False,
    ).first()

    if not reset or reset.expires_at < datetime.now(timezone.utc):
        raise HTTPException(400, "This password reset link is invalid or has expired.")

    user = db.query(User).filter(User.id == reset.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(400, "This password reset link is invalid or has expired.")

    user.password_hash = hash_password(data.new_password)
    reset.used = True
    db.commit()
    return {"message": "Password updated successfully. You can now log in."}
