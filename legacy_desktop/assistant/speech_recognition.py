"""
speech_recognition.py
----------------------
Handles converting the user's spoken voice into text.

Wraps Python's `SpeechRecognition` library with:
- Ambient noise calibration
- Timeout / error handling
- A simple, reusable SpeechListener class
"""

import speech_recognition as sr
from utils.logger import get_logger

logger = get_logger(__name__)


class SpeechListener:
    """Captures audio from the microphone and converts it to text."""

    def __init__(self, energy_threshold: int = 300, pause_threshold: float = 0.8):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.pause_threshold = pause_threshold
        self.recognizer.dynamic_energy_threshold = True

    def calibrate_for_ambient_noise(self, source, duration: float = 1.0):
        """Adjusts recognizer sensitivity to the current background noise level."""
        logger.info("Calibrating microphone for ambient noise...")
        self.recognizer.adjust_for_ambient_noise(source, duration=duration)

    def listen_once(self, timeout: int = 8, phrase_time_limit: int = 15) -> str:
        """
        Listen for a single voice command and return recognized text.

        Args:
            timeout (int): Seconds to wait for speech to start before giving up.
            phrase_time_limit (int): Max seconds allowed for a single phrase.

        Returns:
            str: Recognized text, or an empty string if nothing usable was heard.
        """
        try:
            with sr.Microphone() as source:
                self.calibrate_for_ambient_noise(source)
                logger.info("Listening for a command...")
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_time_limit
                )

            text = self.recognizer.recognize_google(audio)
            logger.info(f"Recognized speech: {text}")
            return text.lower().strip()

        except sr.WaitTimeoutError:
            logger.warning("Listening timed out - no speech detected.")
            return ""
        except sr.UnknownValueError:
            logger.warning("Could not understand audio.")
            return ""
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            return ""
        except OSError as e:
            # Raised when no microphone is available / permission denied
            logger.error(f"Microphone error: {e}")
            return ""
        except Exception as e:
            logger.error(f"Unexpected error while listening: {e}")
            return ""

    def listen_continuous(self, callback, stop_flag):
        """
        Continuously listen for commands until stop_flag() returns True.

        Args:
            callback (callable): Function called with each recognized text string.
            stop_flag (callable): Function returning True when listening should stop.
        """
        logger.info("Starting continuous listening mode.")
        while not stop_flag():
            text = self.listen_once()
            if text:
                callback(text)
