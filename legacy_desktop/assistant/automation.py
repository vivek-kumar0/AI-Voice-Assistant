"""
automation.py
---------------
Desktop automation features for the assistant: opening applications,
websites, YouTube/Google searches, files/folders, system info, and
sending emails via SMTP.
"""

import os
import subprocess
import webbrowser
import smtplib
import platform
from email.mime.text import MIMEText
from datetime import datetime

from utils.logger import get_logger

logger = get_logger(__name__)


class AutomationEngine:
    """Executes desktop-automation tasks requested by voice command."""

    # Common application shortcuts, mapped per OS where relevant
    APP_COMMANDS = {
        "windows": {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "file explorer": "explorer.exe",
        },
        "darwin": {  # macOS
            "calculator": "Calculator",
            "notes": "Notes",
            "finder": "Finder",
            "terminal": "Terminal",
        },
        "linux": {
            "calculator": "gnome-calculator",
            "files": "nautilus",
            "terminal": "gnome-terminal",
        },
    }

    def __init__(self):
        self.os_name = platform.system().lower()

    # ---------------------------------------------------------------
    # Applications
    # ---------------------------------------------------------------
    def open_application(self, app_name: str) -> str:
        """Attempt to open a named desktop application."""
        app_name = app_name.lower().strip()
        os_key = "windows" if "windows" in self.os_name else (
            "darwin" if "darwin" in self.os_name else "linux"
        )
        command = self.APP_COMMANDS.get(os_key, {}).get(app_name)

        if not command:
            return f"Sorry, I don't know how to open '{app_name}' on this system."

        try:
            if os_key == "windows":
                os.startfile(command)  # type: ignore[attr-defined]
            elif os_key == "darwin":
                subprocess.Popen(["open", "-a", command])
            else:
                subprocess.Popen([command])
            logger.info(f"Opened application: {app_name}")
            return f"Opening {app_name}."
        except Exception as e:
            logger.error(f"Failed to open application {app_name}: {e}")
            return f"I couldn't open {app_name}. Error: {e}"

    # ---------------------------------------------------------------
    # Web / Search
    # ---------------------------------------------------------------
    def open_website(self, url: str) -> str:
        if not url.startswith("http"):
            url = f"https://{url}"
        webbrowser.open(url)
        logger.info(f"Opened website: {url}")
        return f"Opening {url}"

    def google_search(self, query: str) -> str:
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Here are the Google results for {query}."

    def play_youtube(self, query: str) -> str:
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Playing {query} on YouTube."

    # ---------------------------------------------------------------
    # Files / Folders
    # ---------------------------------------------------------------
    def open_path(self, path: str) -> str:
        """Open a file or folder using the default OS handler."""
        if not os.path.exists(path):
            return f"I couldn't find the path: {path}"
        try:
            if "windows" in self.os_name:
                os.startfile(path)  # type: ignore[attr-defined]
            elif "darwin" in self.os_name:
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
            return f"Opening {path}"
        except Exception as e:
            logger.error(f"Failed to open path {path}: {e}")
            return f"I couldn't open {path}. Error: {e}"

    # ---------------------------------------------------------------
    # System Info
    # ---------------------------------------------------------------
    @staticmethod
    def get_current_datetime() -> str:
        now = datetime.now()
        return f"It is currently {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')}."

    # ---------------------------------------------------------------
    # Email
    # ---------------------------------------------------------------
    @staticmethod
    def send_email(sender_email: str, sender_password: str, to_email: str,
                    subject: str, body: str, smtp_server: str = "smtp.gmail.com",
                    smtp_port: int = 587) -> str:
        """Send an email using SMTP (e.g. Gmail with an app password)."""
        try:
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = sender_email
            msg["To"] = to_email

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, [to_email], msg.as_string())

            logger.info(f"Email sent to {to_email}")
            return f"Email sent successfully to {to_email}."
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return f"Sorry, I couldn't send the email. Error: {e}"
