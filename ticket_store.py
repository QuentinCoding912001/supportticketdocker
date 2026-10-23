"""Data layer for the IT support ticket logger.

All database access lives here so it can be tested without the command-line menu.
"""

import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone

CATEGORIES = ("Hardware", "Software", "Network")
PRIORITIES = ("Low", "Medium", "High")
STATUSES = ("Open", "In Progress", "Resolved")


def _now() -> str:
    """Current time in UTC, so times are unambiguous inside Docker and across machines."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _escape_like(term: str) -> str:
    """Make % and _ in a search term match literally instead of acting as wildcards."""
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


class TicketStore:
    """Stores support tickets in a SQLite database."""

    def __init__(self, db_path: str | None = None) -> None:
        # The path can be set with the TICKETS_DB environment variable (useful in Docker)
        self.db_path = db_path or os.environ.get("TICKETS_DB", "it_support.db")
        self._setup()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _setup(self) -> None:
        """Create the tickets table, or upgrade a database made by an older version."""
        folder = os.path.dirname(self.db_path)
        if folder:
            os.makedirs(folder, exist_ok=True)

        with closing(self._connect()) as conn, conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tickets (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject     TEXT NOT NULL CHECK (length(trim(subject)) > 0),
                    category    TEXT NOT NULL CHECK (category IN ('Hardware', 'Software', 'Network')),
                    priority    TEXT NOT NULL CHECK (priority IN ('Low', 'Medium', 'High')),
                    status      TEXT NOT NULL DEFAULT 'Open'
                                CHECK (status IN ('Open', 'In Progress', 'Resolved')),
                    created_at  TEXT,
                    resolved_at TEXT
                )
                """
            )
            # Version 1 databases have no resolved_at column; add it if missing
            columns = [row["name"] for row in conn.execute("PRAGMA table_info(tickets)")]
            if "resolved_at" not in columns:
                conn.execute("ALTER TABLE tickets ADD COLUMN resolved_at TEXT")

    def create_ticket(self, subject: str, category: str, priority: str) -> int:
        """Save a new ticket and return its ID."""
        subject = (subject or "").strip()
        if not subject:
            raise ValueError("The issue description cannot be empty.")
        if category not in CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(CATEGORIES)}.")
        if priority not in PRIORITIES:
            raise ValueError(f"Priority must be one of: {', '.join(PRIORITIES)}.")

        with closing(self._connect()) as conn, conn:
            cursor = conn.execute(
                "INSERT INTO tickets (subject, category, priority, created_at) VALUES (?, ?, ?, ?)",
                (subject, category, priority, _now()),
            )
            return int(cursor.lastrowid)

    def get_tickets(self, category: str | None = None, search: str | None = None) -> list[dict]:
        """Return tickets, optionally filtered by category and/or a search term."""
        query = "SELECT id, subject, category, priority, status, created_at, resolved_at FROM tickets"
        conditions: list[str] = []
        params: list[str] = []
        if category:
            conditions.append("category = ?")
            params.append(category)
        if search:
            conditions.append("subject LIKE ? ESCAPE '\\'")
            params.append(f"%{_escape_like(search)}%")
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY id"

        with closing(self._connect()) as conn:
            return [dict(row) for row in conn.execute(query, params)]

    def set_status(self, ticket_id: int, status: str) -> bool:
        """Update a ticket's status. Returns False if no ticket has that ID.

        The first time a ticket is resolved, the time is recorded. Resolving it again keeps
        the original time; moving it back to Open or In Progress clears it.
        """
        if status not in STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(STATUSES)}.")

        with closing(self._connect()) as conn, conn:
            if status == "Resolved":
                cursor = conn.execute(
                    "UPDATE tickets SET status = ?, resolved_at = COALESCE(resolved_at, ?) WHERE id = ?",
                    (status, _now(), ticket_id),
                )
            else:
                cursor = conn.execute(
                    "UPDATE tickets SET status = ?, resolved_at = NULL WHERE id = ?",
                    (status, ticket_id),
                )
            return cursor.rowcount > 0
