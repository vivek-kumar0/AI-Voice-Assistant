# 🎙️ AI Voice Assistant (Python)

A modular, AI-powered desktop voice assistant built in Python. It listens to voice
commands, converts speech to text, understands intent, performs desktop
automation, fetches live information (weather/news/Wikipedia), manages notes
and reminders, and replies with natural speech — all through a modern
CustomTkinter GUI.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## 📌 Table of Contents

- [Features](#-features)
- [Architecture](#-project-architecture)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration-env)
- [Usage](#-usage)
- [Screenshots](#-screenshots)
- [Tech Stack](#-tech-stack)
- [Design Decisions](#-design-decisions)
- [Future Improvements](#-future-improvements)
- [License](#-license)

---

## ✨ Features

| Category | Capabilities |
|---|---|
| **Voice Input** | Microphone capture, ambient-noise calibration, timeout & error handling, continuous listening mode |
| **Voice Output** | Natural offline text-to-speech with adjustable rate & volume (pyttsx3) |
| **AI Conversation** | OpenAI-powered Q&A with persisted conversation history and graceful offline fallback |
| **Desktop Automation** | Open apps, open websites, Google search, YouTube search/play, open files/folders, current date & time |
| **Information Services** | Live weather (OpenWeatherMap), news headlines (NewsAPI), Wikipedia summaries, dictionary definitions |
| **Personal Assistant** | Voice-created notes, note playback, reminders, persisted user preferences |
| **Email Automation** | Send emails via SMTP directly from a voice command |
| **Database** | SQLite persistence for commands, chat history, notes, reminders, and settings |
| **GUI** | Modern dark-mode CustomTkinter interface with mic button, live status indicator, chat log, and settings panel |
| **Reliability** | Centralized logging, layered exception handling, safe API-failure fallbacks |

---

## 🏗 Project Architecture

The project follows a **layered, modular architecture** so each concern is
isolated and independently testable:

```
┌─────────────────────────────────────────────────────────┐
│                      GUI Layer (gui/)                     │
│   CustomTkinter window · mic button · chat log · settings │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│               Command Processor (assistant/commands.py)   │
│   Parses intent from text → routes to the right handler   │
└───┬───────────┬────────────┬────────────┬────────────┬───┘
    │           │            │            │            │
┌───▼───┐  ┌────▼────┐  ┌────▼─────┐ ┌────▼────┐ ┌─────▼─────┐
│Speech │  │   AI     │  │Automation│ │ Weather /│ │ Database  │
│ I/O   │  │ Engine   │  │  Engine  │ │  News    │ │ Manager   │
└───────┘  └──────────┘  └──────────┘ └──────────┘ └───────────┘
```

**Flow of a voice command:**
1. `SpeechListener` captures audio and converts it to text (Google Speech API via `SpeechRecognition`).
2. `CommandProcessor` matches the text against a set of intent patterns (regex-based).
3. Matched intents are routed to `AutomationEngine`, `WeatherService`, `NewsService`, or personal-assistant handlers.
4. Unmatched text is passed to `AIEngine`, which calls the OpenAI API with recent conversation context.
5. Every command and response is persisted via `DatabaseManager` (SQLite).
6. `SpeechEngine` (pyttsx3) speaks the final response aloud, and the GUI updates the chat log and status indicator in real time.

This design follows **separation of concerns** and **dependency injection**:
`main.py` constructs each component and injects it into the ones that need
it (e.g., `CommandProcessor` receives the database, AI engine, and
automation engine as constructor arguments), which makes every class easy
to unit test in isolation using mocks.

---

## 📂 Project Structure

```
AI-Voice-Assistant/
│
├── main.py                    # Application entry point — wires everything together
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── .env.example                # Template for API keys / secrets
├── .gitignore
│
├── assistant/
│   ├── speech_recognition.py  # Voice → text (SpeechListener)
│   ├── text_to_speech.py      # Text → voice (SpeechEngine)
│   ├── commands.py            # Intent parsing & dispatch (CommandProcessor)
│   ├── ai_engine.py           # AI conversation (AIEngine, OpenAI integration)
│   ├── automation.py          # Desktop automation (AutomationEngine)
│
├── database/
│   ├── database.py            # SQLite persistence layer (DatabaseManager)
│   └── assistant.db           # Auto-created on first run
│
├── gui/
│   └── interface.py           # CustomTkinter GUI (AssistantGUI, SettingsWindow)
│
├── api/
│   ├── weather.py             # OpenWeatherMap client (WeatherService)
│   └── news.py                # NewsAPI client (NewsService)
│
└── utils/
    └── logger.py              # Centralized rotating logger
```

---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/AI-Voice-Assistant.git
cd AI-Voice-Assistant
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

> **Note on PyAudio:** PyAudio can require extra system libraries.
> - **Windows:** `pip install pyaudio` usually works directly, or use `pipwin install pyaudio` if it fails.
> - **macOS:** `brew install portaudio` before `pip install pyaudio`.
> - **Linux (Debian/Ubuntu):** `sudo apt-get install portaudio19-dev python3-pyaudio` before installing the pip package.

### 4. Configure environment variables
```bash
cp .env.example .env
```
Then open `.env` and add your API keys (see [Configuration](#-configuration-env)).

### 5. Run the application
```bash
python main.py
```

---

## 🔑 Configuration (.env)

| Variable | Purpose | Required? |
|---|---|---|
| `OPENAI_API_KEY` | Enables the AI conversation feature | Optional (offline fallback used if missing) |
| `OPENWEATHER_API_KEY` | Enables live weather lookups | Optional |
| `NEWS_API_KEY` | Enables news headline lookups | Optional |
| `EMAIL_ADDRESS` / `EMAIL_APP_PASSWORD` | Enables sending emails via voice | Optional |

The app is designed to **degrade gracefully** — if a key is missing, that
specific feature returns a friendly message instead of crashing.

---

## 🚀 Usage

Once running, click **🎤 Speak** (or type into the text box) and try commands like:

- "What's the time?"
- "Open notepad"
- "Search for python tutorials on Google"
- "Play lofi hip hop on YouTube"
- "What's the weather in Delhi?"
- "Tell me the news"
- "Wikipedia Albert Einstein"
- "Define serendipity"
- "Take a note: buy groceries tomorrow"
- "Read my notes"
- "Remind me to call mom at 6pm"
- "What is the capital of France?" *(routed to the AI engine)*

---

## 📸 Screenshots

> Add screenshots of the running application here before publishing to GitHub.

| Main Window | Settings Panel |
|---|---|
| `screenshots/main_window.png` | `screenshots/settings_panel.png` |

---

## 🧰 Tech Stack

- **Language:** Python 3.10+
- **Speech Recognition:** `SpeechRecognition` (Google Speech-to-Text backend)
- **Text-to-Speech:** `pyttsx3` (offline)
- **Audio I/O:** `PyAudio`
- **AI:** OpenAI Chat Completions API
- **GUI:** `customtkinter`
- **Database:** SQLite3 (standard library)
- **HTTP:** `requests`
- **APIs:** OpenWeatherMap, NewsAPI.org, Wikipedia, dictionaryapi.dev
- **Automation:** `os`, `subprocess`, `webbrowser`, `smtplib`

---

## 🧠 Design Decisions

- **OOP throughout:** Every capability (speech, AI, automation, database,
  weather, news) is its own class with a single responsibility, making the
  codebase easy to extend or swap (e.g., replacing OpenAI with Gemini only
  requires changes inside `AIEngine`).
- **Dependency injection:** `main.py` builds each component and passes it
  into the ones that need it, instead of components reaching for globals —
  this keeps classes unit-testable with mocks (see the test snippets used
  during development).
- **Regex-based intent parsing with an AI fallback:** Deterministic commands
  (open app, get weather, set a reminder) are handled instantly and
  offline, while open-ended questions fall through to the AI engine — this
  keeps the assistant fast and cheap for routine tasks.
- **Graceful degradation:** Every external integration (AI, weather, news,
  email) checks for a configured API key/credential and returns a helpful
  message instead of throwing an unhandled exception if it's missing.
- **Background threading in the GUI:** Voice listening and command
  processing run on a separate thread so the CustomTkinter main loop never
  freezes while waiting on the microphone or an API call.

---

## 🔮 Future Improvements

- Wake-word detection ("Hey Assistant") instead of button-triggered listening
- Multi-language speech recognition support
- Google/Outlook calendar integration for reminders
- Packaging as a standalone executable (PyInstaller)
- Unit test suite with `pytest` and CI via GitHub Actions

---

## 📄 License

This project is licensed under the MIT License — feel free to use it as a
learning reference or portfolio piece.
