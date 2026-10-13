# Conversion notes

## Original project audit

The original project was a Python desktop assistant using CustomTkinter. Its core modules are useful and have been preserved in `legacy_desktop/`.

### Issues found

1. A complete local virtual environment was included in the ZIP. This makes the project unnecessarily huge and platform-specific.
2. Python cache files were included.
3. A SQLite database and log file were included.
4. The `.env` contained a credential-like value. The new project intentionally does not copy it.
5. PDF Q&A was implemented in the desktop UI but was disabled in the old `main.py` comment path in some versions; the new web version wires it into the API.
6. Desktop automation cannot safely be performed by a remote web server. Web-safe URL actions are now handled by the React client.
7. The old database was global to one machine. The new schema isolates conversations, notes, reminders and documents by authenticated user.
8. The new project separates frontend and backend responsibilities.

## Feature mapping

| Original | Full-stack version |
|---|---|
| SpeechRecognition | Browser Web Speech API |
| pyttsx3 | Browser SpeechSynthesis |
| CustomTkinter | React responsive UI |
| OpenAI | FastAPI AI service |
| SQLite | SQLAlchemy + SQLite/PostgreSQL |
| Notes | Authenticated REST CRUD |
| Reminders | Authenticated REST CRUD |
| Weather | Backend integration |
| News | Backend integration |
| Wikipedia | Backend integration |
| Dictionary | Backend integration |
| PDF TF-IDF | Backend document search + AI context |
| Google/YouTube | API action + browser navigation |
| Desktop app launching | Preserved in legacy desktop app |
| Settings | Per-user REST settings |
| Chat history | Per-user database history |
