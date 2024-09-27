from apscheduler.schedulers.blocking import BlockingScheduler
from monitor import terminate_idle_connections
import logging
import os
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'message': record.getMessage(),
        }
        return json.dumps(log_obj)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler("/app/logs/scheduler.json")

json_formatter = JsonFormatter()
stream_handler.setFormatter(json_formatter)
file_handler.setFormatter(json_formatter)

logging.basicConfig(level=LOG_LEVEL, handlers=[stream_handler, file_handler])

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
