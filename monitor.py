import os
import psycopg2
from psycopg2 import sql
import logging


LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)

file_handler = logging.FileHandler("/app/logs/monitor.log")
file_handler.setFormatter(log_formatter)

logging.basicConfig(level=LOG_LEVEL, handlers=[stream_handler, file_handler])


POSTGRES_URL = os.getenv("POSTGRES_URL")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "your_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "your_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "your_password")
IDLE_THRESHOLD = os.getenv("IDLE_THRESHOLD", "1 hour")
POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME", "your_username")

def terminate_idle_connections():
    try:
        logging.info("Welcome to PostGMon! Starting idle connection monitor...")
        
        if POSTGRES_URL:
            logging.info("Using POSTGRES_URL for connection")
            conn = psycopg2.connect(POSTGRES_URL)
        else:
            logging.info(f"Connecting using host: {POSTGRES_HOST}, port: {POSTGRES_PORT}")
            conn = psycopg2.connect(
                dbname=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                host=POSTGRES_HOST,
                port=POSTGRES_PORT
            )
        
        logging.info("Successfully connected to the database.")
        conn.autocommit = True
        cur = conn.cursor()

        query = f"""
            SELECT pid, state, now() - query_start AS duration
            FROM pg_stat_activity
            WHERE state = 'idle' 
              AND usename = '{POSTGRES_USERNAME}'
              AND state_change < NOW() - interval '{IDLE_THRESHOLD}';
        """
        logging.debug(f"Executing query: {query}")
        cur.execute(query)

        idle_connections = cur.fetchall()
        num_idle_connections = len(idle_connections)

        logging.info(f"Checked for idle connections: {num_idle_connections} found.")

        if num_idle_connections > 0:
            logging.info("Idle connections found. Terminating connections...")
            for pid, state, duration in idle_connections:
                logging.info(f"Terminating idle connection with PID: {pid}, Duration: {duration}")
                cur.execute(sql.SQL("SELECT pg_terminate_backend(%s);"), [pid])
            logging.info(f"Terminated {num_idle_connections} idle connection(s).")
        else:
            logging.info("No idle connections found.")

        cur.close()
        conn.close()
        logging.info("Database connection closed.")
    except psycopg2.OperationalError as oe:
        logging.error(f"Operational error: {oe}")
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__": 
    logging.info("Running idle connection monitor...")
    terminate_idle_connections()
