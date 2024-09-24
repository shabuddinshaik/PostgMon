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
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade pip setuptools

RUN pip install --no-cache-dir -r /app/requirements.txt

RUN mkdir -p /app/logs

COPY crontab /etc/cron.d/monitor-cron
RUN chmod 0644 /etc/cron.d/monitor-cron && \
    crontab /etc/cron.d/monitor-cron

RUN touch /var/log/cron.log && \
    ln -sf /dev/stdout /app/logs/monitor.log && \
    ln -sf /dev/stdout /app/logs/cron.log

ENV POSTGRES_URL=""
ENV POSTGRES_HOST="localhost"
ENV POSTGRES_PORT=""
ENV POSTGRES_DB=""
ENV POSTGRES_USER=""
ENV POSTGRES_PASSWORD=""
ENV LOG_LEVEL="DEBUG"

CMD ["crond", "-f"]
