import logging
import json
import re
from datetime import datetime, timezone

SENSITIVE_PATTERNS = [
    re.compile(r"password['\"]?\s*[:=]\s*['\"]?([^'\",\s]+)", re.IGNORECASE),
    re.compile(r"api[-_]?key['\"]?\s*[:=]\s*['\"]?([^'\",\s]+)", re.IGNORECASE),
    re.compile(r"bearer\s+([a-zA-Z0-9_\-\.]+)", re.IGNORECASE),
]

def sanitize_log_message(msg: str) -> str:
    """Redact passwords, tokens, and API keys from log strings."""
    redacted = msg
    for pat in SENSITIVE_PATTERNS:
        redacted = pat.sub(r"[REDACTED]", redacted)
    return redacted

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": sanitize_log_message(record.getMessage())
        }
        if hasattr(record, "trace_id"):
            log_obj["trace_id"] = getattr(record, "trace_id")
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

def setup_logger(name: str = "veritas") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

logger = setup_logger()
