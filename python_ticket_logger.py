"""Command-line menu for the IT support ticket logger."""

import os
from collections.abc import Sequence

from ticket_store import CATEGORIES, PRIORITIES, STATUSES, TicketStore

WIDTH = 78


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def print_header(title: str) -> None:
    print(f"\n{'=' * WIDTH}")
    print(title.center(WIDTH))
    print(f"{'=' * WIDTH}\n")


def pause() -> None:
    input("\nPress Enter to return to the menu...")


def choose(prompt: str, options: Sequence[str]) -> str:
    """Ask until the user picks a valid numbered option, then return it."""
    menu = "  ".join(f"[{i}] {option}" for i, option in enumerate(options, start=1))
    while True:
        print(f"\n{menu}")
        choice = input(f"{prompt} (1-{len(options)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print("Please enter one of the numbers shown.")


class TicketCLI:
    """Interactive menu that reads input and calls the TicketStore."""

    def __init__(self, store: TicketStore) -> None:
        self.store = store

    def log_ticket(self) -> None:
        clear_screen()
        print_header("LOG NEW SUPPORT TICKET")

        subject = input("Issue description: ").strip()
        while not subject:
            print("The description cannot be empty.")
            subject = input("Issue description: ").strip()

        category = choose("Select category", CATEGORIES)
        priority = choose("Select priority", PRIORITIES)

        ticket_id = self.store.create_ticket(subject, category, priority)
        print(f"\nTicket #{ticket_id} logged successfully.")
        pause()

    def view_tickets(self, category: str | None = None, search: str | None = None) -> None:
        clear_screen()
        if search:
            title = f'TICKETS MATCHING "{search.upper()}"'
        else:
            title = f"VIEWING {category.upper() if category else 'ALL'} TICKETS"
        print_header(title)

        tickets = self.store.get_tickets(category, search)
        if not tickets:
            print("No tickets found.")
        else:
            print(
                f"{'ID':<4} | {'Category':<9} | {'Priority':<8} | {'Status':<13} | {'Created':<20} | Subject"
            )
            print("-" * WIDTH)
            for t in tickets:
                status = f"[{t['status']}]"
                print(
                    f"{t['id']:<4} | {t['category']:<9} | {t['priority']:<8} | "
                    f"{status:<13} | {t['created_at'] or '':<20} | {t['subject']}"
                )

        print(f"\nTotal tickets: {len(tickets)}")
        pause()

    def update_status(self) -> None:
        clear_screen()
        print_header("UPDATE TICKET STATUS")

        ticket_id = input("Enter the ticket ID to update: ").strip()
        if not ticket_id.isdigit():
            print("\nTicket IDs are whole numbers, for example 3.")
            pause()
            return

        status = choose("Select new status", STATUSES)
        if self.store.set_status(int(ticket_id), status):
            print(f"\nTicket #{ticket_id} updated to {status}.")
        else:
            print(f"\nNo ticket found with ID {ticket_id}.")
        pause()

    def search(self) -> None:
        term = input("Search for: ").strip()
        self.view_tickets(search=term or None)

    def run(self) -> None:
        actions = {
            "1": self.log_ticket,
            "2": self.view_tickets,
            "3": lambda: self.view_tickets("Hardware"),
            "4": lambda: self.view_tickets("Software"),
            "5": lambda: self.view_tickets("Network"),
            "6": self.search,
            "7": self.update_status,
        }
        while True:
            clear_screen()
            print_header("IT SUPPORT TICKET SYSTEM")
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


def main() -> None:
    TicketCLI(TicketStore()).run()


if __name__ == "__main__":
    main()
