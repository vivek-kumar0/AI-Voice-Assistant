"""
main.py
--------
Entry point for the AI Voice Assistant application.

Wires together all components (database, speech I/O, AI engine,
automation, information services, and the GUI) and launches the app.
"""

import os
from dotenv import load_dotenv
print("dotenv working")

from utils.logger import get_logger
from database.database import DatabaseManager
from assistant.speech_recognition import SpeechListener
from assistant.text_to_speech import SpeechEngine
from assistant.ai_engine import AIEngine
from assistant.automation import AutomationEngine
from assistant.commands import CommandProcessor
from api.weather import WeatherService
from api.news import NewsService
from gui.interface import AssistantGUI
from pdf_assistant.pdf_qa_engine import PDFQAEngine

logger = get_logger(__name__)


def build_application():
    """Initialize all components and return a ready-to-run GUI instance."""
    load_dotenv()  # Load API keys and config from .env

    logger.info("Initializing AI Voice Assistant...")

    db_manager = DatabaseManager()

    listener = SpeechListener()
    speaker = SpeechEngine(
        rate=int(db_manager.get_setting("voice_rate", 175)),
        volume=float(db_manager.get_setting("voice_volume", 1.0)),
    )

    ai_engine = AIEngine(db_manager, api_key=os.getenv("OPENAI_API_KEY"))
    automation_engine = AutomationEngine()
    weather_service = WeatherService(api_key=os.getenv("OPENWEATHER_API_KEY"))
    news_service = NewsService(api_key=os.getenv("NEWS_API_KEY"))

    command_processor = CommandProcessor(
        db_manager=db_manager,
        ai_engine=ai_engine,
        automation_engine=automation_engine,
        weather_service=weather_service,
        news_service=news_service,
        default_city=os.getenv("WEATHER_DEFAULT_CITY"),
    )

    pdf_qa_engine = PDFQAEngine(ai_engine=ai_engine)

    app = AssistantGUI(
        listener=listener,
        speaker=speaker,
        command_processor=command_processor,
        db_manager=db_manager,
        pdf_qa_engine=pdf_qa_engine,
    )

    logger.info("AI Voice Assistant initialized successfully.")
    return app


def main():
    try:
        app = build_application()
        app.mainloop()
    except Exception as e:
        logger.critical(f"Fatal error while starting the assistant: {e}")
        raise


if __name__ == "__main__":
    main()
