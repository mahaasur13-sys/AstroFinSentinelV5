"""core/logging.py -- Structured logging with OpenTelemetry trace context."""
import logging
import sys
from typing import Any

from opentelemetry import trace as otel_trace


class TraceContextFilter(logging.Filter):
    """Inject trace_id and span_id into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        span = otel_trace.get_current_span()
        if span.get_span_context().is_valid:
            sc = span.get_span_context()
            record.trace_id = format(sc.trace_id, "032x")
            record.span_id = format(sc.span_id, "016x")
        else:
            record.trace_id = "00000000000000000000000000000000"
            record.span_id = "0000000000000000"
        return True


def setup_logging(level: int = logging.INFO):
    """Configure structured logging with trace context."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s "
        "{trace_id=%(trace_id)s span_id=%(span_id)s}"
    )
    handler.setFormatter(formatter)
    handler.addFilter(TraceContextFilter())

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)