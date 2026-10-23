FROM python:3.12-slim

WORKDIR /app
COPY python_ticket_logger.py .

# Keep the database in a volume so tickets survive container restarts
ENV TICKETS_DB=/data/it_support.db
VOLUME ["/data"]

CMD ["python", "python_ticket_logger.py"]
