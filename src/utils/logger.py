
import logging
import os
from datetime import datetime

class Logger:
    def __init__(self, name: str):
        """
        Initierar loggern och konfigurerar den centrala loggaren.
        
        Parametrar:
        name (str): Namnet på loggern, t.ex. __name__.
        """
        self.logger = logging.getLogger(name)
        # Ändra till logging.DEBUG för mer detaljer
        self.logger.setLevel(logging.INFO) 

        # Förhindrar att loggen konfigureras flera gånger
        if not self.logger.handlers:
            self.setup_handlers()
            
    def setup_handlers(self):
        """
        Konfigurerar fil- och konsolhanterare för loggaren.
        """
        # Sökväg till loggfilen
        log_dir = os.path.join(
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
            "logs"
        )
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file_path = os.path.join(log_dir, f"system_{datetime.now().strftime('%Y-%m-%d')}.log")

        # Filhanterare: Skriver alla meddelanden till en loggfil
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(file_handler)

        # Konsolhanterare: Skriver ut meddelanden till terminalen
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(console_handler)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)

main_logger = Logger('Ubåtssystem')

if __name__ == '__main__':

    print("--- Testar logger.py-skriptet ---")
    
    # Använd main_logger-instansen för att logga meddelanden
    main_logger.info("Loggern har startat och är redo att logga.")
    
    # Exempel på olika loggningsnivåer
    main_logger.info("Detta är ett informationsmeddelande.")
    main_logger.warning("Detta är en varning, något kan vara fel.")
    main_logger.error("Detta är ett felmeddelande, en kritisk händelse inträffade.")
    
    # Ställ in loggern till DEBUG för att se debug-meddelanden
    main_logger.logger.setLevel(logging.DEBUG)
    main_logger.debug("Detta är ett debug-meddelande. Det syns bara när loggningsnivån är DEBUG.")

    print("\nKontrollera filen 'logs/system_yyyy-mm-dd.log' för att se all loggning.")