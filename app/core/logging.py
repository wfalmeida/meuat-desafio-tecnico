import logging
import sys
import json
from datetime import datetime


class JsonFormatter(logging.Formatter):
    """Formatter para logs estruturados em JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "time": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Contexto adicional (quando disponível)
        if hasattr(record, "method"):
            log_record["method"] = record.method
        if hasattr(record, "path"):
            log_record["path"] = record.path
        if hasattr(record, "status_code") and record.status_code is not None:
            log_record["status_code"] = record.status_code
        if hasattr(record, "duration_ms"):
            log_record["duration_ms"] = record.duration_ms

        # Extra data arbitrária
        if hasattr(record, "extra_data"):
            log_record.update(record.extra_data)

        return json.dumps(log_record)


class RequestContextFilter(logging.Filter):
    """
    Garante que campos de contexto existam no LogRecord.
    Sempre que um log não tiver esses campos, preenche com valores padrão.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.method = getattr(record, "method", "-")
        record.path = getattr(record, "path", "-")
        record.status_code = getattr(record, "status_code", None)
        record.duration_ms = getattr(record, "duration_ms", None)
        record.extra_data = getattr(record, "extra_data", {})
        return True


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configura logging global da aplicação:
    - Saída em stdout
    - Formato JSON estruturado
    - Filter de contexto de request
    """

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Evita duplicação de handlers (ex: reload do Uvicorn)
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.addHandler(handler)
    root_logger.addFilter(RequestContextFilter())

    root_logger.info("Logging configurado com sucesso")
