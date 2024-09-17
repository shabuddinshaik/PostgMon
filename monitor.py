import os
import time
import psycopg2
from psycopg2 import sql


POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "your_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "your_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "your_password")
INTERVAL_MINUTES = int(os.getenv("INTERVAL_MINUTES", "10"))


IDLE_THRESHOLD = os.getenv("IDLE_THRESHOLD", "1 hour")

def terminate_idle_connections():
    try:
        conn = psycopg2.connect(
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
        cur.execute(query)

        idle_connections = cur.fetchall()

        for pid, state, duration in idle_connections:
            print(f"Terminating idle connection with PID: {pid}, Duration: {duration}")
            cur.execute(sql.SQL("SELECT pg_terminate_backend(%s);"), [pid])

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    while True:
        print("Checking for idle connections...")
        terminate_idle_connections()
        print(f"Sleeping for {INTERVAL_MINUTES} minutes...")
        time.sleep(INTERVAL_MINUTES * 60)
