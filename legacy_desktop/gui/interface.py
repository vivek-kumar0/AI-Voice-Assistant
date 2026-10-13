"""
interface.py
-------------

Modern desktop GUI for the AI Voice Assistant, built with CustomTkinter.

Features:
- Microphone button to trigger listening
- Live status indicator (Idle / Listening / Thinking / Speaking)
- Scrollable chat history window
- Settings panel (voice rate/volume, dark/light mode)
- Runs voice processing on a background thread so the UI never freezes
"""

import threading
from tkinter import filedialog

import customtkinter as ctk

from utils.logger import get_logger


logger = get_logger(__name__)

ctk.set_default_color_theme("blue")


class AssistantGUI(ctk.CTk):
    """Main application window for the AI Voice Assistant."""

    def __init__(
        self,
        listener,
        speaker,
        command_processor,
        db_manager,
        pdf_qa_engine=None,
    ):
        super().__init__()

        self.listener = listener
        self.speaker = speaker
        self.command_processor = command_processor
        self.db = db_manager
        self.pdf_qa_engine = pdf_qa_engine

        self.is_listening = False

        # When True, questions go to the PDF instead of normal commands
        self.pdf_mode = False

        self.title("AI Voice Assistant")
        self.geometry("650x700")

        ctk.set_appearance_mode("dark")

        self._build_layout()

        # Note:
        # Chat window starts empty on each launch.
        # Old messages are still saved in SQLite.
        # Call self._load_history() here if you want
        # them to reappear when the application opens.

    # ============================================================
    # UI CONSTRUCTION
    # ============================================================

    def _build_layout(self):
        """Build the main application interface."""

        # --------------------------------------------------------
        # Header / Status
        # --------------------------------------------------------

        self.status_label = ctk.CTkLabel(
            self,
            text="● Idle",
            font=ctk.CTkFont(
                size=16,
                weight="bold",
            ),
            text_color="gray",
        )

        self.status_label.pack(
            pady=(15, 5)
        )

        # --------------------------------------------------------
        # Chat History Box
        # --------------------------------------------------------

        self.chat_box = ctk.CTkTextbox(
            self,
            width=600,
            height=400,
            wrap="word",
        )

        self.chat_box.pack(
            padx=15,
            pady=10,
            fill="both",
            expand=True,
        )

        self.chat_box.configure(
            state="disabled"
        )

        # --------------------------------------------------------
        # PDF Panel
        # --------------------------------------------------------

        # Upload a PDF and toggle
        # "Ask about this PDF" mode

        pdf_frame = ctk.CTkFrame(self)

        pdf_frame.pack(
            padx=15,
            pady=(0, 5),
            fill="x",
        )

        # Upload PDF Button

        self.upload_pdf_button = ctk.CTkButton(
            pdf_frame,
            text="📄 Upload PDF",
            width=140,
            command=self._on_upload_pdf,
        )

        self.upload_pdf_button.pack(
            side="left",
            padx=10,
            pady=10,
        )

        # PDF Status

        self.pdf_status_label = ctk.CTkLabel(
            pdf_frame,
            text="No PDF loaded",
            text_color="gray",
        )

        self.pdf_status_label.pack(
            side="left",
            padx=10,
            pady=10,
            fill="x",
            expand=True,
        )

        # PDF Mode Switch

        self.pdf_mode_switch = ctk.CTkSwitch(
            pdf_frame,
            text="Ask about PDF",
            command=self._toggle_pdf_mode,
        )

        self.pdf_mode_switch.pack(
            side="right",
            padx=10,
            pady=10,
        )

        # Disable PDF controls if PDF engine
        # is not connected in main.py

        if self.pdf_qa_engine is None:

            self.upload_pdf_button.configure(
                state="disabled"
            )

            self.pdf_mode_switch.configure(
                state="disabled"
            )

            self.pdf_status_label.configure(
                text="PDF feature not enabled"
            )

        # --------------------------------------------------------
        # Bottom Control Bar
        # --------------------------------------------------------

        control_frame = ctk.CTkFrame(self)

        control_frame.pack(
            pady=10,
            padx=15,
            fill="x",
        )

        # Microphone Button

        self.mic_button = ctk.CTkButton(
            control_frame,
            text="🎤 Speak",
            width=140,
            height=45,
            command=self._on_mic_click,
        )

        self.mic_button.pack(
            side="left",
            padx=10,
            pady=10,
        )

        # Text Entry

        self.text_entry = ctk.CTkEntry(
            control_frame,
            placeholder_text="Type a command...",
        )

        self.text_entry.pack(
            side="left",
            padx=10,
            pady=10,
            fill="x",
            expand=True,
        )

        self.text_entry.bind(
            "<Return>",
            lambda event: self._on_text_submit(),
        )

        # Send Button

        send_button = ctk.CTkButton(
            control_frame,
            text="Send",
            width=80,
            command=self._on_text_submit,
        )

        send_button.pack(
            side="left",
            padx=10,
            pady=10,
        )

        # --------------------------------------------------------
        # Settings Button
        # --------------------------------------------------------

        settings_button = ctk.CTkButton(
            self,
            text="⚙ Settings",
            width=120,
            command=self._open_settings,
        )

        settings_button.pack(
            side="left",
            padx=(15, 5),
            pady=(0, 15),
        )

        # --------------------------------------------------------
        # Clear Chat Button
        # --------------------------------------------------------

        clear_button = ctk.CTkButton(
            self,
            text="🗑 Clear Chat",
            width=120,
            fg_color="gray30",
            command=self._clear_chat,
        )

        clear_button.pack(
            side="left",
            padx=5,
            pady=(0, 15),
        )

    # ============================================================
    # LOAD CHAT HISTORY
    # ============================================================

    def _load_history(self):
        """Populate chat box with recent conversation history from DB."""

        history = self.db.get_conversation_history(
            limit=20
        )

        for entry in history:

            speaker_label = (
                "You"
                if entry["role"] == "user"
                else "Assistant"
            )

            self._append_chat(
                f"{speaker_label}: {entry['message']}"
            )

    # ============================================================
    # EVENT HANDLERS
    # ============================================================

    def _on_mic_click(self):
        """Start voice listening in a background thread."""

        if self.is_listening:
            return

        threading.Thread(
            target=self._listen_and_respond,
            daemon=True,
        ).start()

    # ------------------------------------------------------------
    # Text Submit
    # ------------------------------------------------------------

    def _on_text_submit(self):
        """Process text entered by the user."""

        text = self.text_entry.get().strip()

        if not text:
            return

        self.text_entry.delete(
            0,
            "end",
        )

        threading.Thread(
            target=self._process_command,
            args=(text,),
            daemon=True,
        ).start()

    # ------------------------------------------------------------
    # Voice Listening
    # ------------------------------------------------------------

    def _listen_and_respond(self):
        """Listen for voice input and process the command."""

        self.is_listening = True

        self._set_status(
            "Listening...",
            "orange",
        )

        text = self.listener.listen_once()

        self.is_listening = False

        if not text:

            self._set_status(
                "Idle",
                "gray",
            )

            self._append_chat(
                "Assistant: Sorry, I didn't catch that."
            )

            return

        self._process_command(text)

    # ------------------------------------------------------------
    # Process Command
    # ------------------------------------------------------------

    def _process_command(self, text: str):
        """Process normal commands or PDF questions."""

        self._append_chat(
            f"You: {text}"
        )

        self._set_status(
            "Thinking...",
            "yellow",
        )

        # --------------------------------------------------------
        # PDF Question Answering
        # --------------------------------------------------------

        if (
            self.pdf_mode
            and self.pdf_qa_engine
            and self.pdf_qa_engine.is_loaded
        ):

            response = self.pdf_qa_engine.ask(
                text
            )

            # Keep the chat log consistent
            # by storing PDF Q&A in history

            self.db.add_message(
                "user",
                text,
            )

            self.db.add_message(
                "assistant",
                response,
            )

        # --------------------------------------------------------
        # Normal Command Processing
        # --------------------------------------------------------

        else:

            response = self.command_processor.process(
                text
            )

        # --------------------------------------------------------
        # Display Response
        # --------------------------------------------------------

        self._append_chat(
            f"Assistant: {response}"
        )

        self._set_status(
            "Speaking...",
            "green",
        )

        self.speaker.speak(
            response
        )

        self._set_status(
            "Idle",
            "gray",
        )

    # ============================================================
    # PDF HANDLING
    # ============================================================

    def _on_upload_pdf(self):
        """Open file dialog and allow the user to select a PDF."""

        file_path = filedialog.askopenfilename(
            title="Select a PDF",
            filetypes=[
                ("PDF files", "*.pdf")
            ],
        )

        if not file_path:
            return

        self.pdf_status_label.configure(
            text="Indexing PDF...",
            text_color="orange",
        )

        threading.Thread(
            target=self._load_pdf_thread,
            args=(file_path,),
            daemon=True,
        ).start()

    # ------------------------------------------------------------
    # Load PDF
    # ------------------------------------------------------------

    def _load_pdf_thread(self, file_path: str):
        """Load and process the selected PDF."""

        result_message = self.pdf_qa_engine.load_pdf(
            file_path
        )

        if self.pdf_qa_engine.is_loaded:

            self.pdf_status_label.configure(
                text=(
                    f"📄 "
                    f"{self.pdf_qa_engine.loaded_filename}"
                ),
                text_color="green",
            )

            self.pdf_mode_switch.select()

            self.pdf_mode = True

        else:

            self.pdf_status_label.configure(
                text="Failed to load PDF",
                text_color="red",
            )

        self._append_chat(
            f"Assistant: {result_message}"
        )

    # ------------------------------------------------------------
    # Toggle PDF Mode
    # ------------------------------------------------------------

    def _toggle_pdf_mode(self):
        """Enable or disable PDF question-answering mode."""

        self.pdf_mode = bool(
            self.pdf_mode_switch.get()
        )

        if (
            self.pdf_mode
            and not (
                self.pdf_qa_engine
                and self.pdf_qa_engine.is_loaded
            )
        ):

            self._append_chat(
                "Assistant: Upload a PDF first, "
                "then I can answer questions about it."
            )

    # ============================================================
    # CHAT
    # ============================================================

    def _clear_chat(self):
        """Clear the visible chat and database history."""

        self.chat_box.configure(
            state="normal"
        )

        self.chat_box.delete(
            "1.0",
            "end",
        )

        self.chat_box.configure(
            state="disabled"
        )

        self.db.clear_conversation_history()

    # ============================================================
    # SETTINGS
    # ============================================================

    def _open_settings(self):
        """Open the settings window."""

        SettingsWindow(
            self,
            self.speaker,
            self.db,
        )

    # ============================================================
    # HELPERS
    # ============================================================

    def _append_chat(self, message: str):
        """Add a message to the chat window."""

        self.chat_box.configure(
            state="normal"
        )

        self.chat_box.insert(
            "end",
            message + "\n\n",
        )

        self.chat_box.configure(
            state="disabled"
        )

        self.chat_box.see(
            "end"
        )

    # ------------------------------------------------------------
    # Status
    # ------------------------------------------------------------

    def _set_status(
        self,
        text: str,
        color: str,
    ):
        """Update the assistant status indicator."""

        self.status_label.configure(
            text=f"● {text}",
            text_color=color,
        )


# =================================================================
# SETTINGS WINDOW
# =================================================================

class SettingsWindow(ctk.CTkToplevel):
    """Settings panel for adjusting voice properties and appearance."""

    def __init__(
        self,
        parent,
        speaker,
        db_manager,
    ):
        super().__init__(parent)

        self.speaker = speaker
        self.db = db_manager

        self.title("Settings")
        self.geometry("400x350")

        # --------------------------------------------------------
        # Voice Rate
        # --------------------------------------------------------

        ctk.CTkLabel(
            self,
            text="Voice Rate",
        ).pack(
            pady=(20, 0)
        )

        self.rate_slider = ctk.CTkSlider(
            self,
            from_=100,
            to=250,
            command=self._update_rate,
        )

        self.rate_slider.set(
            175
        )

        self.rate_slider.pack(
            pady=10,
            padx=20,
            fill="x",
        )

        # --------------------------------------------------------
        # Voice Volume
        # --------------------------------------------------------

        ctk.CTkLabel(
            self,
            text="Voice Volume",
        ).pack(
            pady=(10, 0)
        )

        self.volume_slider = ctk.CTkSlider(
            self,
            from_=0,
            to=1,
            command=self._update_volume,
        )

        self.volume_slider.set(
            1.0
        )

        self.volume_slider.pack(
            pady=10,
            padx=20,
            fill="x",
        )

        # --------------------------------------------------------
        # Appearance Mode
        # --------------------------------------------------------

        ctk.CTkLabel(
            self,
            text="Appearance Mode",
        ).pack(
            pady=(10, 0)
        )

        self.appearance_menu = ctk.CTkOptionMenu(
            self,
            values=[
                "Dark",
                "Light",
                "System",
            ],
            command=self._change_appearance,
        )

        self.appearance_menu.pack(
            pady=10
        )

        # --------------------------------------------------------
        # Close Button
        # --------------------------------------------------------

        ctk.CTkButton(
            self,
            text="Close",
            command=self.destroy,
        ).pack(
            pady=20
        )

    # ============================================================
    # SETTINGS HANDLERS
    # ============================================================

    def _update_rate(self, value):
        """Update voice speaking rate."""

        rate = int(value)

        self.speaker.set_rate(
            rate
        )

        self.db.set_setting(
            "voice_rate",
            str(rate),
        )

    # ------------------------------------------------------------

    def _update_volume(self, value):
        """Update voice volume."""

        volume = float(value)

        self.speaker.set_volume(
            volume
        )

        self.db.set_setting(
            "voice_volume",
            str(volume),
        )

    # ------------------------------------------------------------

    def _change_appearance(self, mode: str):
        """Change application appearance mode."""

        ctk.set_appearance_mode(
            mode
        )

        self.db.set_setting(
            "appearance_mode",
            mode,
        )