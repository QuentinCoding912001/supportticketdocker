import sqlite3
import os
from datetime import datetime


class SupportSystem:
    def __init__(self):
        self.db = "it_support.db"
        self._setup_db()

    def _setup_db(self):
        """Initialize the database with a professional schema."""
        with sqlite3.connect(self.db) as conn:
            conn.execute('''
                         CREATE TABLE IF NOT EXISTS tickets
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             subject
                             TEXT
                             NOT
                             NULL,
                             category
                             TEXT
                             CHECK (
                             category
                             IN
                         (
                             'Hardware',
                             'Software',
                             'Network'
                         )),
                             priority TEXT CHECK
                         (
                             priority
                             IN
                         (
                             'Low',
                             'Medium',
                             'High'
                         )),
                             status TEXT DEFAULT 'Open',
                             created_at TEXT
                             )
                         ''')

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title):
        print(f"\n{'=' * 60}")
        print(f"{title.center(60)}")
        print(f"{'=' * 60}\n")

    def log_ticket(self):
        self.print_header("LOG NEW SUPPORT TICKET")
        subject = input("Issue Description: ")

        print("\nCategories: [1] Hardware  [2] Software  [3] Network")
        cat_choice = input("Select Category (1-3): ")
        category = {"1": "Hardware", "2": "Software", "3": "Network"}.get(cat_choice, "Software")

        print("\nPriority: [1] Low  [2] Medium  [3] High")
        pri_choice = input("Select Priority (1-3): ")
        priority = {"1": "Low", "2": "Medium", "3": "High"}.get(pri_choice, "Medium")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        with sqlite3.connect(self.db) as conn:
            conn.execute(
                "INSERT INTO tickets (subject, category, priority, created_at) VALUES (?, ?, ?, ?)",
                (subject, category, priority, timestamp)
            )
        print(f"\n✅ Ticket logged successfully at {timestamp}")
        input("\nPress Enter to return to menu...")

    def view_tickets(self, filter_type=None):
        self.clear_screen()
        title = f"VIEWING {filter_type.upper() if filter_type else 'ALL'} TICKETS"
        self.print_header(title)

        query = "SELECT * FROM tickets"
        params = ()
        if filter_type:
            query += " WHERE category = ?"
            params = (filter_type,)

        with sqlite3.connect(self.db) as conn:
            cursor = conn.execute(query, params)
            tickets = cursor.fetchall()

        if not tickets:
            print("No tickets found in this category.")
        else:
            # Professional Table Header
            print(f"{'ID':<4} | {'category':<10} | {'Priority':<8} | {'Status':<12} | {'Subject'}")
            print("-" * 60)
            for t in tickets:
                # Color-coding logic (text-based for standard CLI)
                status_display = f"[{t[4]}]"
                print(f"{t[0]:<4} | {t[2]:<10} | {t[3]:<8} | {status_display:<12} | {t[1]}")

        print(f"\nTotal Tickets: {len(tickets)}")
        input("\nPress Enter to return to menu...")

    def update_status(self):
        self.print_header("UPDATE TICKET STATUS")
        ticket_id = input("Enter Ticket ID to update: ")

        print("\nNew Status: [1] Open  [2] In Progress  [3] Resolved")
        status_choice = input("Select Status (1-3): ")
        status = {"1": "Open", "2": "In Progress", "3": "Resolved"}.get(status_choice)

        if status:
            with sqlite3.connect(self.db) as conn:
                conn.execute("UPDATE tickets SET status = ? WHERE id = ?", (status, ticket_id))
            print(f"\n✅ Ticket #{ticket_id} updated to {status}")
        else:
            print("\n❌ Invalid selection.")
        input("\nPress Enter to return to menu...")

    def run(self):
        while True:
            self.clear_screen()
            self.print_header("IT SUPPORT TICKET SYSTEM")
            print(" [1] Log New Ticket")
            print(" [2] View All Tickets")
            print(" [3] Filter by Hardware")
            print(" [4] Filter by Software")
            print(" [5] Filter by Network")
            print(" [6] Update Ticket Status")
            print(" [Q] Quit System")

            choice = input("\nSelect an option: ").upper()

            if choice == '1':
                self.log_ticket()
            elif choice == '2':
                self.view_tickets()
            elif choice == '3':
                self.view_tickets("Hardware")
            elif choice == '4':
                self.view_tickets("Software")
            elif choice == '5':
                self.view_tickets("Network")
            elif choice == '6':
                self.update_status()
            elif choice == 'Q':
                break


if __name__ == "__main__":
    app = SupportSystem()
    app.run()