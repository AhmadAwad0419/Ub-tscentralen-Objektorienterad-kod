import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
    
from config.paths import movement_file_path, sensor_file_path
from src.utils.logger import main_logger


class FileReader:

    def load_movements(self, drone_id):
        """ 
        En generator som läser en rörelserapport och returnerar kommandon
        ett i taget baserat på ett specifikt drone_id.
        """
        file_path = movement_file_path(drone_id)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    main_logger.info(f"Börjar läsa in rörelserapport för ubåt: {drone_id}")
                    parts = line.strip().split()
                    if len(parts) == 2:
                        command, value_str = parts
                        try:
                            value = int(value_str)
                            yield (command, value)
                        except ValueError:
                            main_logger.warning(f"Varning: Ogiltigt värde för kommando '{command}' i filen: {file_path}")
                            yield None
                    else:
                        main_logger.warning(f"Varning: Ogiltigt format på raden: '{line.strip()}' i filen: {file_path}")
                        yield None
        except FileNotFoundError:
            main_logger.error(f"Fel: Filen kunde inte hittas: {file_path}")
            yield None
                
    def load_sensor_data(self, drone_id):
        """
        En generator som läser in sensordata och returnerar värdena
        ett i taget baserat på ett specifikt drone_id.
        """
        file_path = sensor_file_path(drone_id)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    main_logger.info(f"Börjar läsa in sensordata för ubåt: {drone_id}")
                    yield line.strip()
        except FileNotFoundError:
            main_logger.error(f"Fel: Filen kunde inte hittas: {file_path}")
            yield None