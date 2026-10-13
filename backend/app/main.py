from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import Base, engine
from app.routers import auth, chat, documents, notes, reminders, dashboard, settings as settings_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    description="Full-stack AI Voice Assistant API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(notes.router)
app.include_router(reminders.router)
app.include_router(dashboard.router)
app.include_router(settings_router.router)

@app.get("/")
def root():
    return {"name": settings.app_name, "status": "online", "docs": "/docs"}

@app.get("/api/health")
def health():
    return {"status": "healthy"}
