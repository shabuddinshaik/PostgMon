FROM ubuntu:20.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    libpq-dev \
    gcc \
    cron

RUN python3 -m venv /app/venv

ENV PATH="/app/venv/bin:$PATH"

COPY monitor.py /app/monitor.py
COPY requirements.txt /app/requirements.txt

RUN /app/venv/bin/pip install --no-cache-dir wheel

RUN /app/venv/bin/pip install --no-cache-dir -r /app/requirements.txt

RUN mkdir -p /app/logs

COPY crontab /etc/cron.d/monitor-cron
RUN chmod 0644 /etc/cron.d/monitor-cron && \
    crontab /etc/cron.d/monitor-cron

RUN touch /var/log/cron.log

ENV POSTGRES_URL=""
ENV POSTGRES_HOST=localhost
ENV POSTGRES_PORT=5432
ENV POSTGRES_DB=mydatabase
ENV POSTGRES_USER=myuser
ENV POSTGRES_PASSWORD=mypassword
ENV LOG_LEVEL=DEBUG

CMD ["cron", "-f"]
