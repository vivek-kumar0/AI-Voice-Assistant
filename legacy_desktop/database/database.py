"""
database.py
------------
SQLite database manager for the AI Voice Assistant.

Responsible for persisting:
- Command history
- Conversation (chat) history with the AI engine
- User notes
- Reminders
- User preferences / settings

Uses a single DatabaseManager class (OOP) that wraps all CRUD operations,
so the rest of the app never has to write raw SQL directly.
"""

import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

from utils.logger import get_logger

logger = get_logger(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assistant.db")


class DatabaseManager:
    """Handles all database operations for the assistant."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._initialize_database()

    @contextmanager
    def _get_connection(self):
        """Context manager that yields a SQLite connection and guarantees closure."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def _initialize_database(self):
        """Create all required tables if they do not already exist."""
        schema = """
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command_text TEXT NOT NULL,
            timestamp TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            remind_at TEXT NOT NULL,
            is_done INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """
        with self._get_connection() as conn:
            conn.executescript(schema)
        logger.info("Database initialized successfully.")

    # ---------------------------------------------------------------
    # Commands
    # ---------------------------------------------------------------
    def log_command(self, command_text: str):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO commands (command_text, timestamp) VALUES (?, ?)",
                (command_text, datetime.now().isoformat()),
            )

    def get_recent_commands(self, limit: int = 20):
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM commands ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(row) for row in rows]

    # ---------------------------------------------------------------
    # Conversations
    # ---------------------------------------------------------------
    def add_message(self, role: str, message: str):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO conversations (role, message, timestamp) VALUES (?, ?, ?)",
                (role, message, datetime.now().isoformat()),
            )

    def get_conversation_history(self, limit: int = 50):
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM conversations ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(row) for row in reversed(rows)]

    def clear_conversation_history(self):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM conversations")

    # ---------------------------------------------------------------
    # Notes
    # ---------------------------------------------------------------
    def add_note(self, content: str):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO notes (content, created_at) VALUES (?, ?)",
                (content, datetime.now().isoformat()),
            )

    def get_notes(self):
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM notes ORDER BY id DESC").fetchall()
        return [dict(row) for row in rows]

    def delete_note(self, note_id: int):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))

    # ---------------------------------------------------------------
    # Reminders
    # ---------------------------------------------------------------
    def add_reminder(self, title: str, remind_at: str):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO reminders (title, remind_at, created_at) VALUES (?, ?, ?)",
                (title, remind_at, datetime.now().isoformat()),
            )

    def get_pending_reminders(self):
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM reminders WHERE is_done = 0 ORDER BY remind_at ASC"
            ).fetchall()
        return [dict(row) for row in rows]

    def mark_reminder_done(self, reminder_id: int):
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE reminders SET is_done = 1 WHERE id = ?", (reminder_id,)
            )

    # ---------------------------------------------------------------
    # Settings / Preferences
    # ---------------------------------------------------------------
    def set_setting(self, key: str, value: str):
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )

    def get_setting(self, key: str, default=None):
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT value FROM settings WHERE key = ?", (key,)
            ).fetchone()
        return row["value"] if row else default
