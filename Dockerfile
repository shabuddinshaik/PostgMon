FROM ubuntu:latest

WORKDIR /app


RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    build-essential \
    libpq-dev \
    gcc \
    cron \
    && rm -rf /var/lib/apt/lists/*


COPY monitor.py /app/monitor.py
COPY requirements.txt /app/requirements.txt


RUN pip3 install --no-cache-dir -r requirements.txt


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
