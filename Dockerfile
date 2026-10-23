FROM python:3.12-slim

# Run as a normal user rather than root
RUN useradd --create-home app && mkdir /data && chown app /data

WORKDIR /app
COPY ticket_store.py python_ticket_logger.py ./

# Keep the database in a volume so tickets survive container restarts
ENV TICKETS_DB=/data/it_support.db
VOLUME ["/data"]

USER app
CMD ["python", "python_ticket_logger.py"]
