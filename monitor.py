import os
import time
import psycopg2
from psycopg2 import sql
import logging


LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("/app/logs/monitor.log"),
    logging.StreamHandler()
])


POSTGRES_URL = os.getenv("POSTGRES_URL")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "your_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "your_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "your_password")
INTERVAL_MINUTES = int(os.getenv("INTERVAL_MINUTES", "10"))
IDLE_THRESHOLD = os.getenv("IDLE_THRESHOLD", "1 hour")
IDLE_CONNECTION_LIMIT = int(os.getenv("IDLE_CONNECTION_LIMIT", "50"))

def terminate_idle_connections():
    try:
        logging.info("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(POSTGRES_URL) if POSTGRES_URL else psycopg2.connect(
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT
        )
        conn.autocommit = True
        cur = conn.cursor()

        query = f"""
            SELECT pid, state, now() - query_start AS duration
            FROM pg_stat_activity
            WHERE state = 'idle' AND (now() - query_start) > interval '{IDLE_THRESHOLD}';
        """
        logging.debug(f"Executing query: {query}")
        cur.execute(query)

        idle_connections = cur.fetchall()
        num_idle_connections = len(idle_connections)

        logging.info(f"Checked for idle connections: {num_idle_connections} found.")

        if num_idle_connections >= IDLE_CONNECTION_LIMIT:
            logging.info(f"Idle connection limit reached ({IDLE_CONNECTION_LIMIT}). Terminating connections...")
            for pid, state, duration in idle_connections:
                logging.info(f"Terminating idle connection with PID: {pid}, Duration: {duration}")
                cur.execute(sql.SQL("SELECT pg_terminate_backend(%s);"), [pid])
            logging.info(f"Terminated {num_idle_connections} idle connection(s).")
        else:
            logging.info("Idle connections are below the threshold. No connections terminated.")

        cur.close()
        conn.close()
        logging.info("Database connection closed.")
    except psycopg2.OperationalError as oe:
        logging.error(f"Operational error: {oe}")
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    while True:
        logging.info("Checking for idle connections...")
        terminate_idle_connections()
        logging.info(f"Sleeping for {INTERVAL_MINUTES} minutes...")
        time.sleep(INTERVAL_MINUTES * 60)
