from pathlib import Path
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import Document, User
from app.services.pdf_service import extract_pdf

router = APIRouter(prefix="/api/documents", tags=["Documents"])
UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("")
def list_documents(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Document).filter(Document.user_id == user.id).order_by(Document.id.desc()).all()
    return [{"id": d.id, "filename": d.filename, "created_at": d.created_at} for d in rows]

@router.post("/upload")
async def upload(file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported")
    data = await file.read()
    if len(data) > 15 * 1024 * 1024:
        raise HTTPException(413, "PDF must be 15 MB or smaller")
    safe = f"{uuid.uuid4().hex}.pdf"
    path = UPLOAD_DIR / safe
    path.write_bytes(data)
    try:
        text = extract_pdf(str(path))
    except Exception as exc:
        path.unlink(missing_ok=True)
        raise HTTPException(400, f"The PDF could not be read: {exc}")
    if not text.strip():
        path.unlink(missing_ok=True)
        raise HTTPException(400, "This PDF contains no selectable text. Scanned/image-only PDFs are not supported yet.")
    doc = Document(user_id=user.id, filename=file.filename, stored_path=str(path), extracted_text=text)
    db.add(doc); db.commit(); db.refresh(doc)
    return {"id": doc.id, "filename": doc.filename, "pages_text_length": len(text)}

@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == user.id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    Path(doc.stored_path).unlink(missing_ok=True)
    db.delete(doc); db.commit()
    return {"message": "Document deleted"}
