import logging
import os
from datetime import datetime
from functools import wraps
from typing import Dict

class ExactLevelFilter(logging.Filter):
    def __init__(self, level):
        super().__init__()
        self._level = level

    def filter(self, record):
        return record.levelno == self._level
    
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

    def _get_or_create_file_handler(self, method_name: str, level: str):
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
        log_file_name = f"{method_name}_{level}_{datetime.now().strftime('%Y-%m-%d')}.log"
        log_file_path = os.path.join(log_dir, log_file_name)
        
        # Använd en unik nyckel för cachen för att separera handlers för olika nivåer
        cache_key = f"{method_name}_{level}"
        
        # Kontrollera om hanteraren redan finns i cachen
        if cache_key not in self.file_handlers:
            file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
            file_handler.setLevel(getattr(logging, level))
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            # Lägg till filtret som endast tillåter exakt matchande nivåer
            file_handler.addFilter(ExactLevelFilter(getattr(logging, level)))
            self.file_handlers[cache_key] = file_handler
            self.logger.addHandler(file_handler)
            
        return self.file_handlers[cache_key]

    # Loggmetoder
    
    def file_reader(self, message, level="INFO"):
        self._get_or_create_file_handler('file_reader', level)
        getattr(self.logger, level.lower())(message)

    def secret_loader(self, message, level="INFO"):
        self._get_or_create_file_handler('secret_loader', level)
        getattr(self.logger, level.lower())(message)

    def movement(self, message, level="INFO"):
        self._get_or_create_file_handler('movement', level)
        getattr(self.logger, level.lower())(message)

    def collision(self, message, level="INFO"):
        self._get_or_create_file_handler('collision', level)
        getattr(self.logger, level.lower())(message)

    def sensor_error(self, message, level="INFO"):
        self._get_or_create_file_handler('sensor_error', level)
        getattr(self.logger, level.lower())(message)
          
    def nuke_activation(self, message, level="INFO"):
        self._get_or_create_file_handler('nuke_activation', level)
        getattr(self.logger, level.lower())(message)
        
    def info(self, message, level="INFO"):
        """En generell info-metod för allmän loggning."""
        self._get_or_create_file_handler('system', level)
        self.logger.info(message)

# Globala instanser av loggarna
main_logger = Logger('Ubåtssystem')
file_logger = Logger('FileReader')
secrets_logger = Logger('SecretsLoader')
movement_logger = Logger('MovementManager')
collision_logger = Logger('CollisionManager')
sensor_logger = Logger('SensorManager')
nuke_logger = Logger('NukeActivation')

def log_calls(func):
    """
    Dekorator som loggar när en funktion anropas och när den är klar.
    Loggar också eventuella undantag.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        main_logger.info(f"Startar funktionen '{func.__name__}'")
        try:
            result = func(*args, **kwargs)
            main_logger.info(f"Funktionen '{func.__name__}' är klar.")
            return result
        except Exception as e:
            main_logger.info(f"Ett undantag uppstod i funktionen '{func.__name__}': {e}", level="ERROR")
            raise  # Viktigt: Skickar undantaget vidare så att programmet kraschar som vanligt

    return wrapper
