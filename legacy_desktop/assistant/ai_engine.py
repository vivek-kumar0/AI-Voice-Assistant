"""
ai_engine.py
-------------
Provides general-purpose AI conversation capability for the assistant,
using the OpenAI API (default) with conversation history stored via
the DatabaseManager. Designed so the underlying LLM provider can be
swapped out easily (OpenAI, Gemini, or a local fallback).
"""

import os
from utils.logger import get_logger

logger = get_logger(__name__)

# Optional import - project still runs without the OpenAI package installed,
# falling back to a simple offline response.
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AIEngine:
    """Handles AI-powered conversational responses and history tracking."""

    SYSTEM_PROMPT = (
        "You are a helpful, concise voice assistant. Keep answers short "
        "and conversational, suitable for being read aloud."
    )

    def __init__(self, db_manager, api_key: str = None, model: str = "gpt-4o-mini"):
        self.db = db_manager
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None

        if OPENAI_AVAILABLE and self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info("AI engine initialized with OpenAI client.")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        else:
            logger.warning(
                "OpenAI client not available (missing package or API key). "
                "AI engine will use offline fallback responses."
            )

    def _build_message_history(self, user_message: str, history_limit: int = 10):
        """Builds a chat-formatted message list from recent DB history."""
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        history = self.db.get_conversation_history(limit=history_limit)
        for entry in history:
            role = "assistant" if entry["role"] == "assistant" else "user"
            messages.append({"role": role, "content": entry["message"]})

        messages.append({"role": "user", "content": user_message})
        return messages

    def get_response(self, user_message: str) -> str:
        """
        Get an AI-generated response to the user's message, storing both
        the question and answer in the conversation history.

        Args:
            user_message (str): The user's spoken/typed input.

        Returns:
            str: The assistant's reply.
        """
        self.db.add_message("user", user_message)

        if not self.client:
            reply = self._offline_fallback(user_message)
        else:
            try:
                messages = self._build_message_history(user_message)
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=300,
                    temperature=0.7,
                )
                reply = response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"AI API call failed: {e}")
                reply = "Sorry, I couldn't reach the AI service right now. Please try again."

        self.db.add_message("assistant", reply)
        return reply

    @staticmethod
    def _offline_fallback(user_message: str) -> str:
        """Basic offline fallback so the assistant remains usable without an API key."""
        return (
            "I don't have AI access configured right now, but I heard you say: "
            f"'{user_message}'. Add an OpenAI API key in your .env file to enable "
            "smart answers."
        )

    def answer_with_context(self, question: str, context: str) -> str:
        """
        Answer a question using ONLY the provided context (e.g. passages
        retrieved from an uploaded PDF), instead of general knowledge or
        the normal rolling conversation history. Used by the PDF Q&A
        feature (pdf_assistant/pdf_qa_engine.py).

        Args:
            question (str): The user's question.
            context (str): Retrieved text passages to ground the answer in.

        Returns:
            str: A concise, context-grounded answer.
        """
        if not self.client:
            return self._offline_fallback(question)

        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Answer the user's question using ONLY the context "
                        "provided below. If the answer isn't in the context, "
                        "say you couldn't find it in the document. Keep the "
                        "answer concise and suitable for being read aloud.\n\n"
                        f"CONTEXT:\n{context}"
                    ),
                },
                {"role": "user", "content": question},
            ]
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=350,
                temperature=0.3,  # lower temperature: stick closely to the source
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"AI API call failed (PDF context mode): {e}")
            return "Sorry, I couldn't reach the AI service to answer that right now."
