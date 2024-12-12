import logging
import os
import sys
from datetime import datetime, timezone, timedelta

CHINA_TZ = timezone(timedelta(hours=8))
class ChinaFormatter(logging.Formatter):

    def formatTime(self, record, datefmt=None):
        ct = datetime.fromtimestamp(record.created, CHINA_TZ)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s

logging_backend = os.getenv("LOGGING_BACKEND", "stdout")

def configure_logging():
    """
    Configure logging backend
    """
    excluded_loggers = ("LiteLLM", "LiteLLM Router", "uvicorn.access")
    for _ in excluded_loggers:
        logging.getLogger(_).setLevel(logging.ERROR)

    if logging_backend == "google":
        pass
    else:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.INFO)

        # Configure the logging format to include timestamp in China timezone
        formatter = ChinaFormatter(
            fmt="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        stdout_handler.setFormatter(formatter)

        logging.basicConfig(level=logging.INFO, handlers=[stdout_handler])

        logging.info("Using stdout logging")

configure_logging()

logging.info("This is an info message with a timestamp.")