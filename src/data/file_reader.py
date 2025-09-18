# src/data/file_reader.py
import os
from typing import Generator
from src.config.paths import movement_file_path, sensor_file_path
from src.utils.logger import movement_logger, sensor_logger

class FileReader:
    """Synchronous version: yields movements from file line by line."""

    def load_movements(self, drone_id: str) -> Generator[tuple[str,int], None, None]:
        file_path = movement_file_path(drone_id)

        if not os.path.exists(file_path):
            movement_logger.movement(f"Rörelsefil saknas för ubåt {drone_id}: {file_path}", level="ERROR")
            return

        movement_logger.movement(f"Läser rörelserapport för ubåt: {drone_id}", level="INFO")

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    command, value_str = parts
                    try:
                        value = int(value_str)
                        yield command, value
                    except ValueError:
                        movement_logger.movement(f"Ogiltigt värde för kommando '{command}' i filen: {file_path}", level="WARNING")
                        continue
                else:
                    movement_logger.movement(f"Ogiltigt format på raden: '{line.strip()}' i filen: {file_path}", level="WARNING")
                    continue
                
    def load_sensor_data(self, drone_id: str) -> Generator[int, None, None]:
        """
        En generator som läser in sensordata och returnerar värdena
        ett i taget baserat på ett specifikt drone_id.
        """
        file_path = sensor_file_path(drone_id)
        
        if not os.path.exists(file_path):
            sensor_logger.sensor_error(f"Sensorfil saknas för ubåt {drone_id}: {file_path}", level="ERROR")
            return

        sensor_logger.sensor_error(f"Läser sensordata för ubåt: {drone_id}", level="INFO")

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                try:
                    value = int(line)
                    yield value
                except ValueError:
                    sensor_logger.sensor_error(f"Ogiltigt värde '{line}' i sensorfilen: {file_path}", level="WARNING")
                    continue