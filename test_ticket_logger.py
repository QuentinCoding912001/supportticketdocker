import pytest

from python_ticket_logger import SupportSystem


@pytest.fixture
def system(tmp_path):
    return SupportSystem(db_path=str(tmp_path / "tickets.db"))


def test_create_ticket_returns_id_and_defaults_to_open(system):
    ticket_id = system.create_ticket("Printer jammed", "Hardware", "Low")
    tickets = system.get_tickets()
    assert ticket_id == 1
    assert tickets[0]["subject"] == "Printer jammed"
    assert tickets[0]["status"] == "Open"


def test_empty_description_is_rejected(system):
    with pytest.raises(ValueError):
        system.create_ticket("   ", "Software", "High")


def test_invalid_category_is_rejected(system):
    with pytest.raises(ValueError):
        system.create_ticket("Laptop overheating", "Plumbing", "High")


def test_filter_by_category_and_search(system):
    system.create_ticket("Wi-Fi drops on floor 2", "Network", "High")
    system.create_ticket("Excel keeps crashing", "Software", "Medium")
    assert [t["subject"] for t in system.get_tickets("Network")] == ["Wi-Fi drops on floor 2"]
    assert [t["subject"] for t in system.get_tickets(search="excel")] == ["Excel keeps crashing"]


def test_resolving_a_ticket_records_the_time(system):
    ticket_id = system.create_ticket("VPN will not connect", "Network", "High")
    assert system.set_status(ticket_id, "Resolved") is True
    ticket = system.get_tickets()[0]
    assert ticket["status"] == "Resolved"
    assert ticket["resolved_at"] is not None


def test_updating_a_missing_ticket_returns_false(system):
    assert system.set_status(999, "Resolved") is False
