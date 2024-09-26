from apscheduler.schedulers.blocking import BlockingScheduler
from monitor import terminate_idle_connections
import logging
import os


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


SCHEDULE_INTERVAL_MINUTES = int(os.getenv("SCHEDULE_INTERVAL_MINUTES", "10"))

def start_scheduler():
    """Start the APScheduler to run the monitor every SCHEDULE_INTERVAL_MINUTES."""
    scheduler = BlockingScheduler()


    scheduler.add_job(terminate_idle_connections, 'interval', minutes=SCHEDULE_INTERVAL_MINUTES)
    logging.info(f"Scheduler started. Running the monitor job every {SCHEDULE_INTERVAL_MINUTES} minutes.")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Scheduler stopped.")

if __name__ == "__main__":
    start_scheduler()
