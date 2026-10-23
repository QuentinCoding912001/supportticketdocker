# IT Support Ticket Logger

[![CI](https://github.com/QuentinCoding912001/supportticketdocker/actions/workflows/ci.yml/badge.svg)](https://github.com/QuentinCoding912001/supportticketdocker/actions/workflows/ci.yml) ![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![License: MIT](https://img.shields.io/badge/license-MIT-green)

A command-line help desk tool written in Python. It logs IT support tickets to a SQLite database, lets you filter and search them, and tracks each one from **Open** to **Resolved**. It runs directly with Python or inside a Docker container.

```
==============================================================================
                             VIEWING ALL TICKETS
==============================================================================

ID   | Category  | Priority | Status        | Created              | Subject
------------------------------------------------------------------------------
1    | Network   | High     | [Resolved]    | 2026-10-23 09:14 UTC | Wi-Fi drops on floor 2
2    | Software  | Medium   | [In Progress] | 2026-10-23 10:02 UTC | Excel keeps crashing
3    | Hardware  | Low      | [Open]        | 2026-10-23 11:30 UTC | Printer jammed

Total tickets: 3
```

## Features

- Log tickets with a description, category (Hardware, Software, Network) and priority (Low, Medium, High)
- View all tickets, filter by category or search by keyword
- Update a ticket's status to Open, In Progress or Resolved; the first resolution time is recorded in UTC
- Input validation in the app, plus CHECK constraints in the database
- Upgrades databases created by older versions automatically
- Runs with plain Python or in Docker (as a non-root user, with data in a volume)

## Tech stack

Python 3.10+, SQLite, pytest, Ruff, Docker, GitHub Actions

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

## Development

```bash
pip install -r requirements-dev.txt
pytest                          # 12 tests
ruff check . && ruff format .   # lint and format
```

GitHub Actions runs the linter and tests on Python 3.10 and 3.12, and builds the Docker image, on every push and pull request.

## Project structure

```
ticket_store.py            Data layer: all SQLite access and validation
python_ticket_logger.py    Command-line menu built on TicketStore
test_ticket_store.py       Unit tests, including the database upgrade path
Dockerfile                 Container image
pyproject.toml             Project metadata, Ruff and pytest settings
.github/workflows/ci.yml   Lint, test and Docker build on every push
```

## Author

**Quentin Bombande**, web developer in Accra, Ghana

[Portfolio](https://quentincoding912001.github.io/quentin-portfolio/) · [LinkedIn](https://www.linkedin.com/in/quentin-bombande-3b3965221/) · [GitHub](https://github.com/QuentinCoding912001)
