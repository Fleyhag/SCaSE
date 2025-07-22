import contextvars

logger_ctx = contextvars.ContextVar("workflow_logger", default=None)

def set_logger(logger):
    logger_ctx.set(logger)

def get_logger():
    return logger_ctx.get()