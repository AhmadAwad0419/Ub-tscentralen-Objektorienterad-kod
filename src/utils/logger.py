import logging
import os
from datetime import datetime
from functools import wraps
from typing import Dict

class ExactLevelCategoryFilter(logging.Filter):
    def __init__(self, level, category):
        super().__init__()
        self._level = level
        self._category = category

    def filter(self, record):
        # Jämför både nivå och kategori
        return record.levelno == self._level and getattr(record, "category", None) == self._category
    
class Logger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        # Sätter loggnivån till DEBUG för att fånga alla meddelanden
        self.logger.setLevel(logging.DEBUG) 
        self.file_handlers: Dict[str, logging.FileHandler] = {}
        
        # Konfigurerar konsolhanteraren enbart om den inte redan är aktiv
        if not any(isinstance(handler, logging.StreamHandler) for handler in self.logger.handlers):
            self.setup_console_handler()

    def setup_console_handler(self):
        """Konfigurerar en hanterare för att skriva ut till konsolen."""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
        # Kommentera ut raden under för att slippa utskrifter i terminalen
        self.logger.addHandler(console_handler)

    def log(self, category: str, message: str, level: str = "INFO"):
        """En generell loggmetod där `category` styr filnamnet."""
        self._get_or_create_file_handler(category, level)
        extra = {"category": category}   # skickas till filtret
        getattr(self.logger, level.lower())(message, extra=extra)

    def _get_or_create_file_handler(self, category: str, level: str):
        """
        Hjälpmetod för att hämta eller skapa en filhanterare för en specifik nivå.
        Använder cache för att undvika att skapa samma hanterare flera gånger.
        """
        # Skapar sökvägen till loggmappen
        log_dir = os.path.join(
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
            "logs"
        )
        os.makedirs(log_dir, exist_ok=True)

        # Använd logger-namnet och loggningsnivån för att skapa ett unikt filnamn
        log_file_name = f"{category}_{level}_{datetime.now().strftime('%Y-%m-%d')}.log"
        log_file_path = os.path.join(log_dir, log_file_name)
        
        # Använd en unik nyckel för cachen för att separera handlers för olika nivåer
        cache_key = f"{category}_{level}"
        
        # Kontrollera om hanteraren redan finns i cachen
        if cache_key not in self.file_handlers:
            file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
            file_handler.setLevel(getattr(logging, level))
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            # Filter som endast tillåter exakt matchande nivåer och kategorier
            file_handler.addFilter(ExactLevelCategoryFilter(getattr(logging, level), category))
            self.file_handlers[cache_key] = file_handler
            self.logger.addHandler(file_handler)
            
        return self.file_handlers[cache_key]

# Globala instanser av loggarna
main_logger = Logger('Ubåtssystem')
file_logger = Logger('FileReader')
secrets_logger = Logger('SecretsLoader')
movement_logger = Logger('MovementManager')
collision_logger = Logger('CollisionManager')
sensor_logger = Logger('SensorManager')
nuke_logger = Logger('NukeActivation')

def log_calls(logger, category: str, context_args: list[str] = None):
    """
    Dekorator som loggar funktionsanrop till en viss kategori, med valfri extra kontext.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Bygg extra kontext från funktionens parametrar
            context = []
            if context_args:
                from inspect import signature
                sig = signature(func)
                bound = sig.bind(*args, **kwargs)
                bound.apply_defaults()
                for c_arg in context_args:
                    if c_arg in bound.arguments:
                        context.append(f"{c_arg}={bound.arguments[c_arg]}")

            context_str = f" | Context: {', '.join(context)}" if context else ""

            logger.log(category, f"Starting function '{func.__name__}'{context_str}")
            try:
                result = func(*args, **kwargs)
                logger.log(category, f"Function '{func.__name__}' finished successfully.{context_str}")
                return result
            except RuntimeError as e:
                logger.log(category, f"Runtime Error in '{func.__name__}': {e}{context_str}", level="ERROR")
                raise
            except FileNotFoundError as e:
                logger.log(category, f"File Not Found Error in '{func.__name__}': {e}{context_str}", level="ERROR")
                raise
            except ValueError as e:
                logger.log(category, f"Value Error in '{func.__name__}': {e}{context_str}", level="ERROR")
                raise
            except TypeError as e:
                logger.log(category, f"Type Error in '{func.__name__}': {e}{context_str}", level="ERROR")
                raise
            except Exception as e:
                logger.log(category, f"Unexpected error in '{func.__name__}': {e}{context_str}", level="CRITICAL")
                raise
        return wrapper
    return decorator
