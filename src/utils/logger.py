import logging
import os
from datetime import datetime
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
        
        # Konfigurera konsolhanteraren enbart om den inte redan är aktiv
        if not any(isinstance(handler, logging.StreamHandler) for handler in self.logger.handlers):
            self.setup_console_handler()

    def setup_console_handler(self):
        """
        Konfigurerar en hanterare för att skriva ut till konsolen.
        """
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
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Använd logger-namnet och loggningsnivån för att skapa ett unikt filnamn
        log_file_name = f"{method_name}_{level}_{datetime.now().strftime('%Y-%m-%d')}.log"
        log_file_path = os.path.join(log_dir, log_file_name)
        
        # Använd en unik nyckel för cachen för att separera handlers för olika nivåer
        cache_key = f"{method_name}_{level}"
        
        # Kontrollera om hanteraren redan finns i cachen
        if cache_key not in self.file_handlers:
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(getattr(logging, level))
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            # Förhindrar att log meddelande skrivs till fel fil
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
        
    def info(self, message):
        """En generell info-metod för allmän loggning."""
        self._get_or_create_file_handler('system', 'INFO')
        self.logger.info(message)

# Globala instanser av loggarna

file_logger = Logger('FileReader')
secrets_logger = Logger('SecretsLoader')
movement_logger = Logger('MovementManager')
collision_logger = Logger('CollisionManager')
sensor_logger = Logger('SensorManager')
nuke_logger = Logger('NukeActivation')

if __name__ == '__main__':
    print("--- Testar loggern ---")

    # Detta är de olika nivåerna som finns
    level="INFO","ERROR","WARNING","CRITICAL","DEBUG", "EXCEPTION (borde bara användas vid exception)"
    
    file_logger.file_reader("Detta är ett testmeddelande.", level="INFO")

    # Använd dessa istället för prints för det ni vill ha loggat. Välj "level" som ovan för vilken nivå det ska vara
    file_logger.file_reader
    
    secrets_logger.secret_loader
     
    movement_logger.movement
    
    collision_logger.collision
    
    sensor_logger.sensor_error
    
    nuke_logger.nuke_activation
