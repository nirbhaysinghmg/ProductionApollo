import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Create main logger
apollo_logger = logging.getLogger("apollo_logger")
apollo_logger.setLevel(logging.INFO)

# Info log file handler (daily rotation)
info_log_path = os.path.join(LOG_DIR, "llm_logs.log")
info_handler = TimedRotatingFileHandler(info_log_path, when="midnight", backupCount=14, encoding="utf-8")
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
apollo_logger.addHandler(info_handler)

# Error log file handler (daily rotation)
error_log_path = os.path.join(LOG_DIR, "llm_errors.log")
error_handler = TimedRotatingFileHandler(error_log_path, when="midnight", backupCount=14, encoding="utf-8")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
apollo_logger.addHandler(error_handler)

# Console handler (for development)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
apollo_logger.addHandler(console_handler)

# Utility for logging LLM queries and errors

def log_query(user_id, user_input, normalized_input, category, context, full_response, response_time, error=None, exc_info=None):
    """Logs LLM queries, responses, and errors. If error, logs at ERROR level with optional stack trace."""
    log_message = (
        f"UserID: {user_id} | User Input: {user_input} | Normalized Input: {normalized_input} | "
        f"Category: {category} | Context: {context[:100]} | Response Time: {response_time:.2f}s | "
        f"Response: {full_response[:200]}..."  # Limit response preview
    )
    if error:
        log_message += f" | ERROR: {error}"
        apollo_logger.error(log_message, exc_info=exc_info)
    else:
        apollo_logger.info(log_message)

# For compatibility with previous imports
logger = apollo_logger
error_logger = apollo_logger
