FROM python:3.9-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-dev \
    build-essential \
    libpq-dev \
    gcc \
    cron \
    libffi-dev \
    openssl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /app/venv

ENV PATH="/app/venv/bin:$PATH"

COPY monitor.py /app/monitor.py
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir wheel
RUN pip install --no-cache-dir -r /app/requirements.txt

RUN mkdir -p /app/logs

COPY crontab /etc/cron.d/monitor-cron
RUN chmod 0644 /etc/cron.d/monitor-cron && \
    crontab /etc/cron.d/monitor-cron

RUN touch /var/log/cron.log

RUN ln -sf /dev/stdout /app/logs/monitor.log

ENV POSTGRES_URL=""
ENV POSTGRES_HOST="localhost"
ENV POSTGRES_PORT=""
ENV POSTGRES_DB=""
ENV POSTGRES_USER=""
ENV POSTGRES_PASSWORD=""
ENV LOG_LEVEL="DEBUG"

CMD ["crond", "-f"]
