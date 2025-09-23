import logging
import os
from datetime import datetime

# Skapa loggmapp
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def create_logger(name: str, filename: str, level=logging.INFO) -> logging.Logger:
    """Skapar en logger med egen fil."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        log_path = os.path.join(LOG_DIR, filename)
        handler = logging.FileHandler(log_path, encoding="utf-8")
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

# === Projektets loggers ===
file_logger         = create_logger("file_logger",         "movement_files.log")
movement_logger     = create_logger("movement_logger",     "movements.log")
collision_logger    = create_logger("collision_logger",    "collisions.log")
sensor_logger       = create_logger("sensor_logger",       "sensor.log")
sensor_file_logger  = create_logger("sensor_file_logger",  "sensor_files.log")
nuke_logger         = create_logger("nuke_logger",         "nukes.log")
secrets_logger    = create_logger("secrets_logger",    "secrets.log")
torpedo_logger    = create_logger("torpedos_logger",    "torpedos.log")


# === Decorator för att logga funktionsanrop ===
def log_calls(logger: logging.Logger, category: str, context_args=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                context = {}
                if context_args:
                    import inspect
                    bound = inspect.signature(func).bind(*args, **kwargs)
                    bound.apply_defaults()
                    for arg_name in context_args:
                        if arg_name in bound.arguments:
                            context[arg_name] = bound.arguments[arg_name]
                logger.info(f"[{category}] {func.__name__} called with {context}")
                return result
            except Exception as e:
                logger.error(f"[{category}] Exception in {func.__name__}: {e}")
                raise
        return wrapper
    return decorator

