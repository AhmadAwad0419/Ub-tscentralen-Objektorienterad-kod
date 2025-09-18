# src/data/file_reader.py
import os
from typing import Generator
from src.config.paths import movement_file_path
from src.utils.logger import main_logger

class FileReader:
    """Synchronous version: yields movements from file line by line."""

    def load_movements(self, drone_id: str) -> Generator[tuple[str,int], None, None]:
        file_path = movement_file_path(drone_id)

        if not os.path.exists(file_path):
            main_logger.error(f"Rörelsefil saknas för ubåt {drone_id}: {file_path}")
            return

        main_logger.info(f"Läser rörelserapport för ubåt: {drone_id}")

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    command, value_str = parts
                    try:
                        value = int(value_str)
                        yield command, value
                    except ValueError:
                        continue
