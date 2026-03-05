"""CloudWatch-compatible structured JSON logging."""

import json
import logging
import sys
from datetime import datetime, timezone


class StructuredFormatter(logging.Formatter):
    """Formats log records as JSON for CloudWatch compatibility."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra_data"):
            log_entry["data"] = record.extra_data
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


class TicketLogger:
    """Structured logger for the QR Ticket Manager system.

    Produces JSON-formatted log entries compatible with AWS CloudWatch Logs.

    Attributes:
        logger: The underlying Python logger instance.
    """

    def __init__(self, name: str = "qr_ticket_manager", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(StructuredFormatter())
            self.logger.addHandler(handler)

    def _log(self, level: int, message: str, **kwargs):
        extra_data = kwargs if kwargs else None
        record = self.logger.makeRecord(
            self.logger.name, level, "(file)", 0, message, (), None
        )
        if extra_data:
            record.extra_data = extra_data
        self.logger.handle(record)

    def info(self, message: str, **kwargs):
        self._log(logging.INFO, message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log(logging.ERROR, message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._log(logging.WARNING, message, **kwargs)

    def debug(self, message: str, **kwargs):
        self._log(logging.DEBUG, message, **kwargs)
