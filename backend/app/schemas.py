from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(default="", max_length=120)

class LoginRequest(BaseModel):
    username: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=32, max_length=256)
    new_password: str = Field(min_length=8, max_length=128)

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str
    created_at: datetime

    model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)
    document_id: int | None = None

class ChatResponse(BaseModel):
    response: str
    action: dict | None = None

class NoteCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10000)

class NoteOut(BaseModel):
    id: int
    content: str
    created_at: datetime
    model_config = {"from_attributes": True}

class ReminderCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    remind_at: str = Field(min_length=1, max_length=100)

class ReminderOut(BaseModel):
    id: int
    title: str
    remind_at: str
    is_done: bool
    created_at: datetime
    model_config = {"from_attributes": True}

class SettingsUpdate(BaseModel):
    theme: str | None = None
    voice_rate: int | None = None
    voice_enabled: bool | None = None
