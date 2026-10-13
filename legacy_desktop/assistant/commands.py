"""
commands.py
------------
Central command processor. Parses recognized text into an intent and
dispatches it to the appropriate handler (automation, information
services, personal-assistant features, or the AI engine as a fallback).

This module is the "brain" that decides what the assistant should do
with a given voice command.
"""

import re
import wikipedia
import requests

from utils.logger import get_logger

logger = get_logger(__name__)


class CommandProcessor:
    """Parses user commands and routes them to the correct handler."""

    def __init__(self, db_manager, ai_engine, automation_engine,
                 weather_service, news_service, default_city: str = None):
        self.db = db_manager
        self.ai_engine = ai_engine
        self.automation = automation_engine
        self.weather = weather_service
        self.news = news_service
        # Fallback city used when the user asks for weather without naming
        # one (e.g. "what's the weather today?"). Configure via .env
        # WEATHER_DEFAULT_CITY, or the assistant will politely ask instead.
        self.default_city = default_city

        # Ordered list of (regex pattern, handler function name).
        # More SPECIFIC patterns must come before more GENERAL ones,
        # otherwise the general pattern will swallow the match first.
        self.intent_patterns = [
            (r"\bopen (?:the )?(?:website|site) (.+)", self._handle_open_website),
            (r"\bopen (.+)", self._handle_open_application),
            (r"\bsearch (?:for )?(.+) on google", self._handle_google_search),
            (r"\bgoogle (.+)", self._handle_google_search),
            (r"\bplay (.+) on youtube", self._handle_youtube),
            (r"\bplay (.+)", self._handle_youtube),
            (r"\bwhat(?:'s| is) the time\b|\bcurrent time\b", self._handle_datetime),
            (r"\bwhat(?:'s| is) the date\b|\btoday's date\b", self._handle_datetime),
            (r"\bweather (?:in|for|at) (.+)", self._handle_weather),
            # General weather catch-all (no city named) — must stay AFTER
            # the specific "weather in/for <city>" pattern above.
            (r"\bweather\b", self._handle_weather_general),
            (r"\bnews\b", self._handle_news),
            (r"\bwikipedia (.+)", self._handle_wikipedia),
            (r"\bdefine (.+)|\bmeaning of (.+)", self._handle_dictionary),
            (r"\btake a note[:]? (.+)|\bnote (?:that )?(.+)", self._handle_add_note),
            (r"\bread (?:my )?notes\b", self._handle_read_notes),
            (r"\bremind me to (.+) at (.+)", self._handle_add_reminder),
        ]

    def process(self, text: str) -> str:
        """
        Process a recognized command string and return the assistant's reply.

        Args:
            text (str): Recognized speech, already lower-cased.

        Returns:
            str: Response text to be spoken / shown to the user.
        """
        if not text:
            return "I didn't catch that. Could you please repeat?"

        self.db.log_command(text)
        logger.info(f"Processing command: {text}")

        for pattern, handler in self.intent_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    groups = [g for g in match.groups() if g]
                    # Reminder handler needs both captured groups (task + time).
                    # Bound methods must be compared with == (not `is`), since
                    # accessing self.method creates a new bound-method object
                    # each time.
                    if handler == self._handle_add_reminder:
                        return handler(tuple(groups))
                    return handler(groups[0] if groups else None)
                except Exception as e:
                    logger.error(f"Error handling command '{text}': {e}")
                    return "Something went wrong while handling that command."

        # Fallback: no automation intent matched -> ask the AI engine
        return self.ai_engine.get_response(text)

    # ---------------------------------------------------------------
    # Automation handlers
    # ---------------------------------------------------------------
    def _handle_open_website(self, url: str) -> str:
        return self.automation.open_website(url.strip())

    def _handle_open_application(self, app_name: str) -> str:
        return self.automation.open_application(app_name.strip())

    def _handle_google_search(self, query: str) -> str:
        return self.automation.google_search(query.strip())

    def _handle_youtube(self, query: str) -> str:
        return self.automation.play_youtube(query.strip())

    def _handle_datetime(self, _unused) -> str:
        return self.automation.get_current_datetime()

    # ---------------------------------------------------------------
    # Information service handlers
    # ---------------------------------------------------------------
    def _handle_weather(self, city: str) -> str:
        return self.weather.get_weather(city.strip())

    def _handle_weather_general(self, _unused) -> str:
        """Handles 'what's the weather' / 'weather today' with no city named."""
        if self.default_city:
            return self.weather.get_weather(self.default_city)
        return "Sure — which city would you like the weather for?"

    def _handle_news(self, _unused) -> str:
        return self.news.get_top_headlines()

    def _handle_wikipedia(self, query: str) -> str:
        query = query.strip()
        try:
            summary = wikipedia.summary(query, sentences=2)
            return f"According to Wikipedia: {summary}"
        except wikipedia.exceptions.DisambiguationError:
            return f"That's a bit ambiguous. Could you be more specific about '{query}'?"
        except wikipedia.exceptions.PageError:
            return f"I couldn't find a Wikipedia page for '{query}'."
        except Exception as e:
            logger.error(f"Wikipedia lookup failed: {e}")
            return "Sorry, I couldn't reach Wikipedia right now."

    def _handle_dictionary(self, word: str) -> str:
        word = word.strip()
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                return f"I couldn't find a definition for '{word}'."
            data = response.json()
            meaning = data[0]["meanings"][0]["definitions"][0]["definition"]
            return f"{word.capitalize()} means: {meaning}"
        except Exception as e:
            logger.error(f"Dictionary lookup failed: {e}")
            return "Sorry, I couldn't reach the dictionary service right now."

    # ---------------------------------------------------------------
    # Personal assistant handlers
    # ---------------------------------------------------------------
    def _handle_add_note(self, content: str) -> str:
        content = content.strip()
        self.db.add_note(content)
        return "Got it, I've saved that note."

    def _handle_read_notes(self, _unused) -> str:
        notes = self.db.get_notes()
        if not notes:
            return "You don't have any saved notes."
        spoken = "; ".join(note["content"] for note in notes[:5])
        return f"Here are your notes: {spoken}"

    def _handle_add_reminder(self, groups) -> str:
        # When two groups are captured by the regex, `groups` will only hold
        # the first non-empty one due to filtering in `process`; handle both
        # single-string and tuple cases defensively.
        if isinstance(groups, tuple):
            title, remind_at = groups
        else:
            title, remind_at = groups, "unspecified time"
        self.db.add_reminder(title.strip(), remind_at.strip())
        return f"Reminder set: {title.strip()} at {remind_at.strip()}."
