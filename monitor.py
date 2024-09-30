import os
import psycopg2
from psycopg2 import sql
import logging
import time
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'message': record.getMessage(),
        }
        return json.dumps(log_obj)

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler("/app/logs/monitor.json")

json_formatter = JsonFormatter()
stream_handler.setFormatter(json_formatter)
file_handler.setFormatter(json_formatter)

logging.basicConfig(level=LOG_LEVEL, handlers=[stream_handler, file_handler])

POSTGRES_URL = os.getenv("POSTGRES_URL")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "your_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "your_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "your_password")
POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME", "your_username")

IDLE_THRESHOLD_NORMAL = os.getenv("IDLE_THRESHOLD_NORMAL", "1 hour")

IDLE_THRESHOLD_SPIKE = os.getenv("IDLE_THRESHOLD_SPIKE", "10 minutes")

SPIKE_THRESHOLD = int(os.getenv("SPIKE_THRESHOLD", 70))

def log_message(message, level="INFO"):
    logging.log(getattr(logging, level), message)

def connect_to_database():
    if POSTGRES_URL:
        log_message("Using POSTGRES_URL for connection")
        conn = psycopg2.connect(POSTGRES_URL)
    else:
        log_message(f"Connecting using host: {POSTGRES_HOST}, port: {POSTGRES_PORT}")
        conn = psycopg2.connect(
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT
        )
    return conn

def terminate_idle_connections():
    try:
        log_message("Welcome to PostGMon! Starting idle connection monitor...")

        conn = connect_to_database()
        log_message("Successfully connected to the database.")
        conn.autocommit = True
        cur = conn.cursor()

        query = f"""
            SELECT pid, state, now() - query_start AS duration
            FROM pg_stat_activity
            WHERE state = 'idle'
              AND usename = %s
              AND state_change < NOW() - interval %s;
        """

        log_message(f"Executing query for normal idle threshold: {IDLE_THRESHOLD_NORMAL}")
        cur.execute(query, (POSTGRES_USERNAME, IDLE_THRESHOLD_NORMAL))
        idle_connections_normal = cur.fetchall()

        log_message("Checking for total idle connections.")
        cur.execute(f"""
            SELECT COUNT(*) FROM pg_stat_activity
            WHERE state = 'idle'
              AND usename = %s;
        """, (POSTGRES_USERNAME,))
        total_idle_connections = cur.fetchone()[0]

        log_message(f"Total idle connections found: {total_idle_connections}")

        if total_idle_connections > SPIKE_THRESHOLD:
            log_message(f"Spike detected! Idle connections exceed {SPIKE_THRESHOLD}. Applying spike threshold of {IDLE_THRESHOLD_SPIKE}.")
            cur.execute(query, (POSTGRES_USERNAME, IDLE_THRESHOLD_SPIKE))
            idle_connections_spike = cur.fetchall()
        else:
            idle_connections_spike = []

        idle_connections = list(set(idle_connections_normal + idle_connections_spike))
        num_idle_connections = len(idle_connections)

        log_message(f"Checked for idle connections: {num_idle_connections} found.")

        if num_idle_connections > 0:
            log_message("Idle connections found. Terminating connections...")
            for pid, state, duration in idle_connections:
                log_message(f"Terminating idle connection with PID: {pid}, Duration: {duration}")
                cur.execute(sql.SQL("SELECT pg_terminate_backend(%s);"), [pid])
            log_message(f"Terminated {num_idle_connections} idle connection(s).")
        else:
            log_message("No idle connections found.")

        cur.close()
        conn.close()
        log_message("Database connection closed.")

    except psycopg2.OperationalError as oe:
        log_message(f"Operational error: {oe}", level="ERROR")
    except Exception as e:
        log_message(f"Error: {e}", level="ERROR")

if __name__ == "__main__":
    log_message("Running idle connection monitor...")

    while True:
        log_message("Starting script execution")
        terminate_idle_connections()
        log_message("Script execution completed")
        log_message("Sleeping for 10 minutes")
        time.sleep(600)
