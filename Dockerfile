FROM python:3.9-alpine

WORKDIR /app

RUN apk update && apk add --no-cache \
    python3-dev \
    build-base \
    libpq \
    postgresql-dev \
    gcc \
    musl-dev \
    linux-headers \
    libffi-dev \
    openssl-dev \
    && rm -rf /var/cache/apk/*

RUN python3 -m venv /app/venv

ENV PATH="/app/venv/bin:$PATH"

COPY monitor.py /app/monitor.py
COPY scheduler.py /app/scheduler.py

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools
RUN pip install --no-cache-dir -r /app/requirements.txt

RUN mkdir -p /app/logs

RUN ln -sf /dev/stdout /app/logs/monitor.log && \
    ln -sf /dev/stdout /app/logs/scheduler.log

ENV POSTGRES_URL=""
ENV POSTGRES_HOST="localhost"
ENV POSTGRES_PORT=""
ENV POSTGRES_DB=""
ENV POSTGRES_USER=""
ENV POSTGRES_PASSWORD=""
ENV LOG_LEVEL="DEBUG"
ENV SCHEDULE_INTERVAL_MINUTES="10"
ENV IDLE_THRESHOLD="1 hour"
ENV IDLE_THRESHOLD_SPIKE="10 minutes"
ENV SPIKE_THRESHOLD="70"

RUN apk add --no-cache shadow && useradd -u 1000 myuser
USER root
RUN chown -R 1000:1000 /app
RUN chmod +x /app/scheduler.py /app/monitor.py

USER myuser

CMD ["python", "/app/scheduler.py"]