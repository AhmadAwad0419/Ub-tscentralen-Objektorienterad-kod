# src/data/file_reader.py
import os
from pathlib import Path
from typing import Generator, Tuple, Union
from src.config import paths
from src.utils.logger import file_logger, sensor_file_logger, log_calls


class FileReader:
    """Synchronous version: yields movements from file line by line."""

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
            file_logger.error("MovementReports directory not found")
            raise

    @log_calls(file_logger, "movement_files", context_args=["drone_id"])
    def load_movements(self, drone_id: str, max_lines: int = 10_000):
        """
        Loads movement commands for a specific drone.
        Läser högst `max_lines` rader. Stoppar även på första tomma raden.
        """
        file_path = paths.movement_file_path(drone_id)
        if not os.path.exists(file_path):
            file_logger.error(f"Movement file not found: {file_path}")
            raise FileNotFoundError(file_path)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                count = 0
                for i, line in enumerate(f, start=1):
                    if count >= max_lines:
                        file_logger.warning(
                            f"[{drone_id}] Movement file {file_path} has more than {max_lines} lines → extra lines ignored"
                        )
                        break

                    stripped = line.strip()
                    if not stripped:   # stoppa på första tomma rad
                        file_logger.info(
                            f"[{drone_id}] Empty line at line {i}, stopping read"
                        )
                        break

                    parts = stripped.split()
                    if len(parts) == 2:
                        direction = parts[0]
                        try:
                            distance = int(parts[1])
                        except ValueError:
                            file_logger.error(
                                f"[{drone_id}] Invalid distance at line {i}: {parts[1]}"
                            )
                            continue

                        count += 1
                        file_logger.debug(
                            f"[{drone_id}] Loaded move {count}: {direction} {distance}"
                        )
                        yield (direction, distance)

                file_logger.info(f"[{drone_id}] Total moves loaded: {count}")

        except Exception as e:
            file_logger.error(f"Failed to load movements for {drone_id}: {e}")
            raise
    """def load_movements(self, drone_id: str):
        #Loads movement commands for a specific drone.
        file_path = paths.movement_file_path(drone_id)
        if not os.path.exists(file_path):
            file_logger.error(f"Movement file not found: {file_path}")
            raise FileNotFoundError()
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                line_num = 0
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 2:
                        direction = parts[0]
                        distance = int(parts[1])
                        line_num += 1
                        file_logger.info(
                            f"[{drone_id}] Loaded movement line {line_num}: {direction} {distance}"
                        )
                        yield (direction, distance)

                if line_num == 0:
                    file_logger.warning(f"[{drone_id}] Movement file {file_path} was empty!")

        except ValueError as e:
            file_logger.error(f"Invalid data in movement file {file_path}: {e}")
            raise"""

    @log_calls(sensor_file_logger, "sensor_files")
    def load_all_sensor_files(self) -> Generator[Tuple[str, Generator[str, None, None]], None, None]:
        """
        Generates a tuple with the submarine ID and its sensor data generator.
        """
        try:
            for file_path in paths.SENSOR_DATA_DIR.glob("*.txt"):
                drone_id = file_path.stem
                yield (drone_id, self.load_sensor_data(file_path))
        except FileNotFoundError:
            sensor_file_logger.error("Sensordata directory not found")
            raise
    
    @log_calls(sensor_file_logger, "sensor_files", context_args=["file_path"])
    def load_sensor_data(self, file_path: Union[str, Path]) -> Generator[str, None, None]:
        """Loads sensor data line by line."""
        if not os.path.exists(file_path):
            sensor_file_logger.error(f"Sensor file not found: {file_path}")
            raise FileNotFoundError()

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    yield line.strip()
        except ValueError as e:
            sensor_file_logger.error(f"Invalid data in sensor file {file_path}: {e}")
            raise
