# IT Support Ticket Logger

A command-line help desk tool written in Python. It logs IT support tickets to a SQLite database, lets you filter and search them, and tracks each one from **Open** to **Resolved**. It runs directly with Python or inside a Docker container.

```
======================================================================
                       VIEWING ALL TICKETS
======================================================================

ID   | Category  | Priority | Status        | Created          | Subject
----------------------------------------------------------------------
1    | Network   | High     | [Resolved]    | 2026-10-23 09:14 | Wi-Fi drops on floor 2
2    | Software  | Medium   | [In Progress] | 2026-10-23 10:02 | Excel keeps crashing
3    | Hardware  | Low      | [Open]        | 2026-10-23 11:30 | Printer jammed

Total tickets: 3
```

## Features

- Log tickets with a description, category (Hardware, Software, Network) and priority (Low, Medium, High)
- View all tickets, filter by category or search by keyword
- Update a ticket's status to Open, In Progress or Resolved, with the resolution time recorded
- Input validation: empty descriptions, invalid menu choices and unknown ticket IDs are caught
- Data stored in SQLite, with constraints enforced at the database level
- Unit tests with pytest
- Docker image with the database kept in a volume

## Tech stack

Python 3, SQLite, pytest, Docker

## Run with Python

No third-party packages are needed to run the app.

```bash
python python_ticket_logger.py
```

Tickets are saved to `it_support.db` in the current folder. To use a different file, set `TICKETS_DB`:

```bash
TICKETS_DB=~/tickets.db python python_ticket_logger.py
```

## Run with Docker

```bash
docker build -t ticket-logger .
docker run -it -v tickets:/data ticket-logger
```

The `tickets` volume keeps your tickets between runs.

## Run the tests

```bash
pip install -r requirements-dev.txt
python -m pytest
```

## Project structure

```
python_ticket_logger.py   App: data layer and command-line menu
test_ticket_logger.py     Unit tests
Dockerfile                Container image
requirements-dev.txt      Test dependencies
```

## Author

**Quentin Bombande**, web developer in Accra, Ghana

[Portfolio](https://quentincoding912001.github.io/quentin-portfolio/) · [LinkedIn](https://www.linkedin.com/in/quentin-bombande-3b3965221/) · [GitHub](https://github.com/QuentinCoding912001)
