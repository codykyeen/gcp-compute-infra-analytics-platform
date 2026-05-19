import logging
import os
import time
from datetime import datetime, timezone
from ingestion import config

#Generate a unique timestamp for each log file to ensure logs are isolated per run and do not overwrite previous execution
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

def cleanup_old_logs(log_dir, logger, days=30):
    # Remove log files older than the specified retention window to prevent unbounded disk usage over time
    #Limits logs to 30 days (default)
    cutoff_time = time.time() - (days * 86400)

    for filename in os.listdir(log_dir):
        file_path = os.path.join(log_dir, filename)

        #Ensure only log files are impacted
        if os.path.isfile(file_path) and filename.startswith("ingestion_"):
            file_mtime = os.path.getmtime(file_path)

            if file_mtime < cutoff_time:
                try:
                    os.remove(file_path)
                    logger.info(f"Deleted old log file: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete {file_path}: {e}")


def get_logger():
    #Configures logging and log format

    logger = logging.getLogger("ingestion")
    logger.setLevel(logging.INFO)

    #Prevent adding duplicate handlers when get_logger() is called multiple times
    if logger.handlers:
        return logger

    #Prevent propagation to root logger (avoids duplicate logs)
    logger.propagate = False

    #Log Formatter
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    #Ensure log directory exists
    os.makedirs(config.LOG_DIR, exist_ok=True)

    #Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    #Create a unique log file per run and data sourc
    log_file = os.path.join(config.LOG_DIR, f"ingestion_{config.DATA_SOURCE}_{timestamp}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)



    #Attach Handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    #Clean up old log files
    cleanup_old_logs(config.LOG_DIR, logger, days=30)

    return logger