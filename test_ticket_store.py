import sqlite3

import pytest

from ticket_store import TicketStore


@pytest.fixture
def store(tmp_path):
    return TicketStore(db_path=str(tmp_path / "tickets.db"))


def test_create_ticket_returns_id_and_defaults_to_open(store):
    ticket_id = store.create_ticket("Printer jammed", "Hardware", "Low")
    ticket = store.get_tickets()[0]
    assert ticket_id == 1
    assert ticket["subject"] == "Printer jammed"
    assert ticket["status"] == "Open"
    assert ticket["created_at"].endswith("UTC")


@pytest.mark.parametrize(
    ("subject", "category", "priority"),
    [
        ("   ", "Software", "High"),
        ("Laptop overheating", "Plumbing", "High"),
        ("Laptop overheating", "Hardware", "Urgent"),
    ],
)
def test_invalid_input_is_rejected(store, subject, category, priority):
    with pytest.raises(ValueError):
        store.create_ticket(subject, category, priority)


def test_invalid_status_is_rejected(store):
    ticket_id = store.create_ticket("Mouse not working", "Hardware", "Low")
    with pytest.raises(ValueError):
        store.set_status(ticket_id, "Closed")


def test_database_rejects_bad_status_written_directly(store):
    store.create_ticket("Mouse not working", "Hardware", "Low")
    with sqlite3.connect(store.db_path) as conn, pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE tickets SET status = 'Closed' WHERE id = 1")


def test_filter_by_category_and_search(store):
    store.create_ticket("Wi-Fi drops on floor 2", "Network", "High")
    store.create_ticket("Excel keeps crashing", "Software", "Medium")
    assert [t["subject"] for t in store.get_tickets("Network")] == ["Wi-Fi drops on floor 2"]
    assert [t["subject"] for t in store.get_tickets(search="excel")] == ["Excel keeps crashing"]


def test_search_treats_wildcards_literally(store):
    store.create_ticket("Disk at 100% usage", "Hardware", "High")
    store.create_ticket("Disk at 1000 errors", "Hardware", "High")
    assert [t["subject"] for t in store.get_tickets(search="100%")] == ["Disk at 100% usage"]
    assert store.get_tickets(search="_") == []


def test_resolving_records_time_once(store):
    ticket_id = store.create_ticket("VPN will not connect", "Network", "High")
    assert store.set_status(ticket_id, "Resolved") is True
    first = store.get_tickets()[0]["resolved_at"]
    assert first is not None

    store.set_status(ticket_id, "Resolved")
    assert store.get_tickets()[0]["resolved_at"] == first


def test_reopening_clears_resolved_time(store):
    ticket_id = store.create_ticket("VPN will not connect", "Network", "High")
    store.set_status(ticket_id, "Resolved")
    store.set_status(ticket_id, "Open")
    assert store.get_tickets()[0]["resolved_at"] is None


def test_updating_a_missing_ticket_returns_false(store):
    assert store.set_status(999, "Resolved") is False


def test_upgrades_a_version_1_database(tmp_path):
    db_path = tmp_path / "old.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE tickets (id INTEGER PRIMARY KEY AUTOINCREMENT, subject TEXT NOT NULL, "
            "category TEXT, priority TEXT, status TEXT DEFAULT 'Open', created_at TEXT)"
        )
        conn.execute(
            "INSERT INTO tickets (subject, category, priority, created_at) "
            "VALUES ('Old ticket', 'Software', 'Low', '2025-01-01 09:00')"
        )

    store = TicketStore(db_path=str(db_path))
    ticket = store.get_tickets()[0]
    assert ticket["subject"] == "Old ticket"
    assert "resolved_at" in ticket
    assert store.set_status(ticket["id"], "Resolved") is True
