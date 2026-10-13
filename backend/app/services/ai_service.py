from google import genai

from app.core.config import settings


# ============================================================
# NOVA SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Nova, a helpful AI voice assistant inside a full-stack web application.

Answer the user's actual question directly and naturally.

You can answer questions about:
- General knowledge
- Python
- JavaScript
- React
- FastAPI
- SQL
- Databases
- Programming
- Coding
- Study
- Career
- Writing
- Mathematics
- Technology
- Everyday topics

Be accurate and clear.

If you are unsure about something, say so instead of inventing facts.

Never claim that you performed an application action unless the application
actually performed that action.

If PDF/document context is provided, use it as the primary source for
document-specific questions.

If the answer is not present in the selected PDF, clearly tell the user
that the answer could not be found in the selected PDF.

Keep answers reasonably concise because responses may also be read aloud
by the browser.
"""


# ============================================================
# PLACEHOLDER API KEYS
# ============================================================

PLACEHOLDER_KEYS = {
    "",
    "your_gemini_api_key_here",
    "your_api_key_here",
    "replace-me",
    "replace_with_your_key",
}


# ============================================================
# CHECK GEMINI CONFIGURATION
# ============================================================

def gemini_configured() -> bool:
    """
    Check whether a real Gemini API key has been configured.
    """

    key = (settings.gemini_api_key or "").strip()

    return key.lower() not in PLACEHOLDER_KEYS


# ============================================================
# AI SERVICE
# ============================================================

class AIService:

    def __init__(self):
        """
        Initialize Gemini client.
        """

        self.client = None

        if gemini_configured():

            self.client = genai.Client(
                api_key=settings.gemini_api_key.strip()
            )


    # ========================================================
    # REPLY
    # ========================================================

    def reply(
        self,
        message: str,
        history: list[dict],
        document_context: str = "",
        document_selected: bool = False,
    ) -> str:

        # ----------------------------------------------------
        # Check Gemini API configuration
        # ----------------------------------------------------

        if not self.client:

            return (
                "Gemini AI is not connected yet. "
                "Please add your Gemini API key to backend/.env "
                "and restart FastAPI."
            )


        # ----------------------------------------------------
        # PDF / DOCUMENT CONTEXT
        # ----------------------------------------------------

        document_block = ""

        if document_selected:

            document_block = (
                "\n\n"
                "SELECTED PDF INSTRUCTIONS:\n"
                "The user has selected a PDF document.\n"
                "Answer the user's document-specific question ONLY "
                "using the PDF context provided below.\n"
                "If the context contains "
                "[NO_RELEVANT_CONTENT_FOUND_IN_SELECTED_PDF], "
                "tell the user that the answer could not be found "
                "in the selected PDF.\n"
                "Do not invent information that is not present in "
                "the PDF context.\n\n"
                "PDF CONTEXT:\n"
                + (document_context or "")
            )


        # ----------------------------------------------------
        # BUILD CHAT HISTORY
        # ----------------------------------------------------

        conversation = []

        for item in history[-12:]:

            role = item.get("role")

            text = item.get("message", "")

            if role in {"user", "assistant"} and text:

                conversation.append(
                    f"{role.upper()}: {text}"
                )


        # ----------------------------------------------------
        # ADD CURRENT USER MESSAGE
        # ----------------------------------------------------

        conversation.append(
            f"USER: {message}"
        )


        # ----------------------------------------------------
        # CREATE FINAL PROMPT
        # ----------------------------------------------------

        prompt = (
            SYSTEM_PROMPT
            + document_block
            + "\n\n"
            + "CONVERSATION HISTORY:\n"
            + "\n".join(conversation)
            + "\n\n"
            + "ASSISTANT:"
        )


        # ----------------------------------------------------
        # SEND REQUEST TO GEMINI
        # ----------------------------------------------------

        try:

            response = self.client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
            )


            # ------------------------------------------------
            # GET GEMINI RESPONSE
            # ------------------------------------------------

            answer = (response.text or "").strip()


            if answer:

                return answer


            return (
                "I received your question, but Gemini did not "
                "return an answer. Please try again."
            )


        # ----------------------------------------------------
        # ERROR HANDLING
        # ----------------------------------------------------

        except Exception as exc:

            # Print actual error in FastAPI terminal.
            # This does NOT print your API key.
            print("\n========== GEMINI ERROR ==========")
            print(repr(exc))
            print("==================================\n")


            error_text = str(exc).lower()


            # ------------------------------------------------
            # API KEY ERROR
            # ------------------------------------------------

            if (
                "401" in error_text
                or "403" in error_text
                or "api key" in error_text
                or "authentication" in error_text
                or "permission" in error_text
            ):

                return (
                    "The Gemini API key was rejected. "
                    "Please check GEMINI_API_KEY in backend/.env "
                    "and restart FastAPI."
                )


            # ------------------------------------------------
            # FREE QUOTA / RATE LIMIT
            # ------------------------------------------------

            if (
                "429" in error_text
                or "quota" in error_text
                or "resource exhausted" in error_text
                or "rate limit" in error_text
            ):

                return (
                    "Gemini's free usage limit has been reached "
                    "temporarily. Please try again later."
                )


            # ------------------------------------------------
            # MODEL ERROR
            # ------------------------------------------------

            if (
                "model" in error_text
                and (
                    "not found" in error_text
                    or "does not exist" in error_text
                    or "unsupported" in error_text
                )
            ):

                return (
                    f"The configured Gemini model "
                    f"'{settings.gemini_model}' is unavailable. "
                    f"Please check GEMINI_MODEL in backend/.env."
                )


            # ------------------------------------------------
            # CONNECTION / TIMEOUT ERROR
            # ------------------------------------------------

            if (
                "timeout" in error_text
                or "timed out" in error_text
                or "connection" in error_text
            ):

                return (
                    "Gemini could not be reached right now. "
                    "Please check your internet connection "
                    "and try again."
                )


            # ------------------------------------------------
            # GENERAL ERROR
            # ------------------------------------------------

            return (
                "I could not get a response from Gemini right now. "
                "Please try again."
            )