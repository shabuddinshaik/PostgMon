import os
import time
import psycopg2
from psycopg2 import sql
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler("/app/logs/monitor.log"),
    logging.StreamHandler()
])

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "your_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "your_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "your_password")
INTERVAL_MINUTES = int(os.getenv("INTERVAL_MINUTES", "10"))
IDLE_THRESHOLD = os.getenv("IDLE_THRESHOLD", "1 hour")

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "your_email@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your_email_password")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", "recipient_email@gmail.com")

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_RECIPIENT
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_USER, EMAIL_RECIPIENT, text)
        server.quit()
        logging.info("Email sent successfully")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

def terminate_idle_connections():
    try:
        logging.info("Connecting to PostgreSQL database...")
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
        logging.debug(f"Executing query: {query}")
        cur.execute(query)

        idle_connections = cur.fetchall()

        if idle_connections:
            logging.info(f"Found {len(idle_connections)} idle connection(s).")
            for pid, state, duration in idle_connections:
                logging.info(f"Terminating idle connection with PID: {pid}, Duration: {duration}")
                cur.execute(sql.SQL("SELECT pg_terminate_backend(%s);"), [pid])
            send_email(
                "Idle Connections Terminated",
                f"Terminated {len(idle_connections)} idle connection(s)."
            )
        else:
            logging.info("No idle connections found.")

        cur.close()
        conn.close()
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    while True:
        logging.info("Checking for idle connections...")
        terminate_idle_connections()
        logging.info(f"Sleeping for {INTERVAL_MINUTES} minutes...")
        time.sleep(INTERVAL_MINUTES * 60)
