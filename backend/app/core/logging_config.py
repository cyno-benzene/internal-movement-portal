import logging
from logging.handlers import TimedRotatingFileHandler
import sys
from pathlib import Path

# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent.parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

# --- API Logger ---
api_log_file = log_dir / "api.log"
api_logger = logging.getLogger("api")
api_logger.setLevel(logging.INFO)
# Rotate log file every day at midnight, keep 7 old files
api_handler = TimedRotatingFileHandler(api_log_file, when="midnight", interval=1, backupCount=7)
api_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
api_handler.setFormatter(api_formatter)
api_logger.addHandler(api_handler)

# --- Error Logger ---
error_log_file = log_dir / "error.log"
error_logger = logging.getLogger("error")
error_logger.setLevel(logging.ERROR)
# Rotate log file every day at midnight, keep 7 old files
error_handler = TimedRotatingFileHandler(error_log_file, when="midnight", interval=1, backupCount=7)
error_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - [in %(pathname)s:%(lineno)d]')
error_handler.setFormatter(error_formatter)
error_logger.addHandler(error_handler)

# --- Console Logger for Uvicorn/FastAPI ---
console_logger = logging.getLogger("uvicorn")
console_logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
console_logger.addHandler(console_handler)

def get_api_logger():
    return api_logger

def get_error_logger():
    return error_logger
