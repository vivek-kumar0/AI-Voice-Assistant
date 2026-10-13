import re
from datetime import datetime
from urllib.parse import quote_plus
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models import Note, Reminder, User
from app.services.integrations import weather, news, wikipedia_summary, dictionary_definition
from app.services.ai_service import AIService

class CommandService:
    def __init__(self):
        self.ai = AIService()

    def process(self, db: Session, user: User, text: str, history: list[dict], document_context: str = "", document_selected: bool = False):
        t = text.strip()
        low = t.lower()

        # Web-safe actions: frontend performs navigation after receiving the URL.
        m = re.match(r"(?:search|google)(?: for)? (.+?)(?: on google)?$", low)
        if m:
            q = m.group(1).strip()
            return {"response": f"Opening Google results for {q}.", "action": {"type": "open_url", "url": f"https://www.google.com/search?q={quote_plus(q)}"}}

        m = re.match(r"(?:play|search) (.+?)(?: on youtube)?$", low)
        if m and ("youtube" in low or low.startswith("play ")):
            q = m.group(1).strip()
            return {"response": f"Opening YouTube results for {q}.", "action": {"type": "open_url", "url": f"https://www.youtube.com/results?search_query={quote_plus(q)}"}}

        if re.search(r"\b(time|date)\b", low) and any(x in low for x in ["what", "current", "today"]):
            return {"response": datetime.now().strftime("It is %I:%M %p on %A, %B %d, %Y."), "action": None}

        m = re.search(r"\bweather\s+(?:in|for|at)\s+(.+)", low)
        if m:
            return {"response": weather(m.group(1).strip()), "action": None}
        if "weather" in low:
            return {"response": weather(settings.weather_default_city), "action": None}
        if "news" in low and len(low) < 80:
            return {"response": news(), "action": None}

        m = re.search(r"\bwikipedia\s+(.+)", low)
        if m:
            return {"response": wikipedia_summary(m.group(1).strip()), "action": None}

        m = re.search(r"(?:define|meaning of)\s+(.+)", low)
        if m:
            return {"response": dictionary_definition(m.group(1).strip()), "action": None}

        m = re.search(r"(?:take a note|note(?: that)?):?\s+(.+)", low)
        if m:
            note = Note(user_id=user.id, content=m.group(1).strip())
            db.add(note); db.commit()
            return {"response": "Got it. I saved that note.", "action": None}

        if re.search(r"\b(read|show) (?:my )?notes\b", low):
            notes = db.query(Note).filter(Note.user_id == user.id).order_by(Note.id.desc()).limit(5).all()
            if not notes:
                return {"response": "You do not have any saved notes yet.", "action": None}
            return {"response": "Here are your latest notes: " + "; ".join(n.content for n in notes), "action": None}

        m = re.search(r"remind me to (.+?) at (.+)", low)
        if m:
            db.add(Reminder(user_id=user.id, title=m.group(1).strip(), remind_at=m.group(2).strip()))
            db.commit()
            return {"response": f"Reminder saved for {m.group(2).strip()}.", "action": None}

        # Desktop-only actions cannot be safely executed by a remote browser backend.
        m = re.match(r"open (.+)", low)
        if m and m.group(1).strip() not in {"website", "site"}:
            return {"response": "Desktop app launching is available in the preserved legacy desktop version. In the web version I can safely open websites, Google and YouTube.", "action": None}

        return {"response": self.ai.reply(text, history, document_context, document_selected=document_selected), "action": None}
