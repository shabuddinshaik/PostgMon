FROM ubuntu:20.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    libpq-dev \
    gcc \
    cron \
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

ENV POSTGRES_URL=""
ENV POSTGRES_HOST=""
ENV POSTGRES_PORT=""
ENV POSTGRES_DB=""
ENV POSTGRES_USER=""
ENV POSTGRES_PASSWORD=""
ENV LOG_LEVEL="DEBUG"

CMD ["cron", "-f"]
