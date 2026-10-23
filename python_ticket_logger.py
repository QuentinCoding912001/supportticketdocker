import os
import sqlite3
from datetime import datetime

CATEGORIES = ("Hardware", "Software", "Network")
PRIORITIES = ("Low", "Medium", "High")
STATUSES = ("Open", "In Progress", "Resolved")


class SupportSystem:
    """A small IT help desk: log tickets, view them and track their status."""

    def __init__(self, db_path=None):
        # The database path can be set with the TICKETS_DB environment variable (useful in Docker)
        self.db = db_path or os.environ.get("TICKETS_DB", "it_support.db")
        self._setup_db()

    # ---------- Data layer ----------

    def _connect(self):
        return sqlite3.connect(self.db)

    def _setup_db(self):
        """Create the tickets table if it does not exist yet."""
        folder = os.path.dirname(self.db)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tickets (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject     TEXT NOT NULL CHECK (length(trim(subject)) > 0),
                    category    TEXT CHECK (category IN ('Hardware', 'Software', 'Network')),
                    priority    TEXT CHECK (priority IN ('Low', 'Medium', 'High')),
                    status      TEXT DEFAULT 'Open',
                    created_at  TEXT,
                    resolved_at TEXT
                )
                """
            )
            # Older databases were created without resolved_at; add it if missing
            columns = [row[1] for row in conn.execute("PRAGMA table_info(tickets)")]
            if "resolved_at" not in columns:
                conn.execute("ALTER TABLE tickets ADD COLUMN resolved_at TEXT")

    def create_ticket(self, subject, category, priority):
        """Save a new ticket and return its ID."""
        subject = (subject or "").strip()
        if not subject:
            raise ValueError("The issue description cannot be empty.")
        if category not in CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(CATEGORIES)}.")
        if priority not in PRIORITIES:
            raise ValueError(f"Priority must be one of: {', '.join(PRIORITIES)}.")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO tickets (subject, category, priority, created_at) VALUES (?, ?, ?, ?)",
                (subject, category, priority, timestamp),
            )
            return cursor.lastrowid

    def get_tickets(self, category=None, search=None):
        """Return tickets as dictionaries, optionally filtered by category or a search term."""
        query = "SELECT id, subject, category, priority, status, created_at, resolved_at FROM tickets"
        conditions, params = [], []
        if category:
            conditions.append("category = ?")
            params.append(category)
        if search:
            conditions.append("subject LIKE ?")
            params.append(f"%{search}%")
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY id"

        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(query, params)]

    def set_status(self, ticket_id, status):
        """Update a ticket's status. Returns False if no ticket has that ID."""
        if status not in STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(STATUSES)}.")
        resolved_at = datetime.now().strftime("%Y-%m-%d %H:%M") if status == "Resolved" else None
        with self._connect() as conn:
            cursor = conn.execute(
                "UPDATE tickets SET status = ?, resolved_at = ? WHERE id = ?",
                (status, resolved_at, ticket_id),
            )
            return cursor.rowcount > 0

    # ---------- Command-line interface ----------

    @staticmethod
    def clear_screen():
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def print_header(title):
        print(f"\n{'=' * 70}")
        print(f"{title.center(70)}")
        print(f"{'=' * 70}\n")

    @staticmethod
    def pause():
        input("\nPress Enter to return to the menu...")

    @staticmethod
    def choose(prompt, options):
        """Ask until the user picks a valid numbered option, then return it."""
        menu = "  ".join(f"[{i}] {option}" for i, option in enumerate(options, start=1))
        while True:
            print(f"\n{menu}")
            choice = input(f"{prompt} (1-{len(options)}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(options):
                return options[int(choice) - 1]
            print("Please enter one of the numbers shown.")

    def log_ticket(self):
        self.clear_screen()
        self.print_header("LOG NEW SUPPORT TICKET")

        subject = input("Issue description: ").strip()
        while not subject:
            print("The description cannot be empty.")
            subject = input("Issue description: ").strip()

        category = self.choose("Select category", CATEGORIES)
        priority = self.choose("Select priority", PRIORITIES)

        ticket_id = self.create_ticket(subject, category, priority)
        print(f"\nTicket #{ticket_id} logged successfully.")
        self.pause()

    def view_tickets(self, category=None, search=None):
        self.clear_screen()
        if search:
            title = f'TICKETS MATCHING "{search.upper()}"'
        else:
            title = f"VIEWING {category.upper() if category else 'ALL'} TICKETS"
        self.print_header(title)

        tickets = self.get_tickets(category, search)
        if not tickets:
            print("No tickets found.")
        else:
            print(f"{'ID':<4} | {'Category':<9} | {'Priority':<8} | {'Status':<13} | {'Created':<16} | Subject")
            print("-" * 70)
            for t in tickets:
                print(
                    f"{t['id']:<4} | {t['category']:<9} | {t['priority']:<8} | "
                    f"{'[' + t['status'] + ']':<13} | {t['created_at'] or '':<16} | {t['subject']}"
                )

        print(f"\nTotal tickets: {len(tickets)}")
        self.pause()

    def update_status(self):
        self.clear_screen()
        self.print_header("UPDATE TICKET STATUS")

        ticket_id = input("Enter the ticket ID to update: ").strip()
        if not ticket_id.isdigit():
            print("\nTicket IDs are whole numbers, for example 3.")
            self.pause()
            return

        status = self.choose("Select new status", STATUSES)
        if self.set_status(int(ticket_id), status):
            print(f"\nTicket #{ticket_id} updated to {status}.")
        else:
            print(f"\nNo ticket found with ID {ticket_id}.")
        self.pause()

    def run(self):
        actions = {
            "1": self.log_ticket,
            "2": self.view_tickets,
            "3": lambda: self.view_tickets("Hardware"),
            "4": lambda: self.view_tickets("Software"),
            "5": lambda: self.view_tickets("Network"),
            "6": lambda: self.view_tickets(search=input("Search for: ").strip() or None),
            "7": self.update_status,
        }
        while True:
            self.clear_screen()
            self.print_header("IT SUPPORT TICKET SYSTEM")
            print(" [1] Log new ticket")
            print(" [2] View all tickets")
            print(" [3] Filter by Hardware")
            print(" [4] Filter by Software")
            print(" [5] Filter by Network")
            print(" [6] Search tickets")
            print(" [7] Update ticket status")
            print(" [Q] Quit")

            choice = input("\nSelect an option: ").strip().upper()
            if choice == "Q":
                print("Goodbye.")
                break
            action = actions.get(choice)
            if action:
                action()


if __name__ == "__main__":
    SupportSystem().run()
