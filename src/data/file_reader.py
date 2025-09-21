import os
from pathlib import Path
from typing import Generator, Tuple, Union
from src.config import paths
from src.utils.logger import file_logger, log_calls

class FileReader:
    """Reads various data files and returns them as generators."""

    @log_calls(file_logger, "movement_files")
    def load_all_movement_files(self) -> Generator[Tuple[str, Generator[Tuple[str, int], None, None]], None, None]:
        """
        Generates a tuple for each movement file found.
        Each tuple contains the drone's ID and its movement generator.
        """
        try:
            for file_path in paths.MOVEMENT_REPORTS_DIR.glob("*.txt"):
                drone_id = file_path.stem
                yield (drone_id, self.load_movements(drone_id))
        except FileNotFoundError:
            raise

    @log_calls(file_logger, "movement_files", context_args=["drone_id"])
    def load_movements(self, drone_id: str) -> Generator[Tuple[str, int], None, None]:
        """Loads movement commands for a specific drone."""
        file_path = paths.movement_file_path(drone_id)
        if not os.path.exists(file_path):
            raise FileNotFoundError()
        
        try:
            with open(file_path, "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 2:
                        direction = parts[0]
                        distance = int(parts[1])
                        yield (direction, distance)
        except ValueError:
            raise
    
    @log_calls(file_logger, "sensor_files")
    def load_all_sensor_files(self) -> Generator[Tuple[str, Generator[str, None, None]], None, None]:
        """
        Generates a tuple with the submarine ID and its sensor data generator.
        """
        for file_path in paths.SENSOR_DATA_DIR.glob("*.txt"):
            drone_id = file_path.stem
            yield (drone_id, self.load_sensor_data(file_path))
    
    @log_calls(file_logger, "sensor_files", context_args=["drone_id"])
    def load_sensor_data(self, file_path: Union[str, Path]) -> Generator[str, None, None]:
        """Loads sensor data line by line."""
        if not os.path.exists(file_path):
            raise FileNotFoundError()

        try:
            with open(file_path, "r") as f:
                for line in f:
                    yield line.strip()                    
        except ValueError:
            raise