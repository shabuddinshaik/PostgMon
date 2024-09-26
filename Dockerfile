FROM python:3.11-slim-buster


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


WORKDIR /app


COPY app/ /app/


RUN useradd -ms /bin/bash appuser


RUN mkdir -p /app/logs && chown appuser:appuser /app/logs

USER appuser


ENV POSTGRES_URL="postgres://user:password@localhost:5432/mydb" \
    POSTGRES_HOST="localhost" \
    POSTGRES_PORT="5432" \
    POSTGRES_DB="your_db" \
    POSTGRES_USER="your_user" \
    POSTGRES_PASSWORD="your_password" \
    POSTGRES_USERNAME="your_username" \
    IDLE_THRESHOLD="1 hour" \
    LOG_LEVEL="INFO" \
    SCHEDULE_INTERVAL_MINUTES="10"


ENTRYPOINT ["python", "/app/scheduler.py"]
