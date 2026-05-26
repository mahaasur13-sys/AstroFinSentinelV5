import structlog

def _add_correlation_id(logger, method_name, event_dict):
    """Подставляет correlation_id из контекста structlog."""
    ctx = structlog.contextvars.get_contextvars()
    cid = ctx.get("correlation_id") or "unknown"
    if "correlation_id" not in event_dict:
        event_dict["correlation_id"] = cid
    return event_dict

def setup_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            _add_correlation_id,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.BoundLogger,
    )

def get_logger(name: str) -> structlog.BoundLogger:
    return structlog.get_logger(name)
