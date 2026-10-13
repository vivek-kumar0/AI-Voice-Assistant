"""
text_to_speech.py
-------------------
Handles converting the assistant's text responses into spoken audio
using the pyttsx3 offline text-to-speech engine.
"""

import pyttsx3
from utils.logger import get_logger

logger = get_logger(__name__)


class SpeechEngine:
    """Wraps pyttsx3 to provide simple, configurable text-to-speech output."""

    def __init__(self, rate: int = 175, volume: float = 1.0, voice_gender: str = "female"):
        self.engine = pyttsx3.init()
        self.set_rate(rate)
        self.set_volume(volume)
        self.set_voice(voice_gender)

    def set_rate(self, rate: int):
        """Set speaking speed (words per minute)."""
        self.engine.setProperty("rate", rate)

    def set_volume(self, volume: float):
        """Set speaking volume, range 0.0 to 1.0."""
        volume = max(0.0, min(1.0, volume))
        self.engine.setProperty("volume", volume)

    def set_voice(self, gender: str = "female"):
        """Select a system voice matching the requested gender, if available."""
        voices = self.engine.getProperty("voices")
        for voice in voices:
            if gender.lower() in voice.name.lower() or gender.lower() in (voice.id or "").lower():
                self.engine.setProperty("voice", voice.id)
                return
        # Fall back to the first available voice
        if voices:
            self.engine.setProperty("voice", voices[0].id)

    def speak(self, text: str):
        """Speak the given text aloud and log it."""
        if not text:
            return
        try:
            logger.info(f"Speaking: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Text-to-speech failed: {e}")
