# src/data/file_reader_async.py
import os
import aiofiles
from typing import AsyncGenerator

from src.config.paths import movement_file_path, sensor_file_path
from src.utils.logger import main_logger


class AsyncFileReader:
    """Asynchronous reader for movement and sensor files."""

    async def load_movements(self, drone_id: str) -> AsyncGenerator[tuple[str, int], None]:
        """
        Async generator: yields (command, value) from a movement report file.
        """
        file_path = movement_file_path(drone_id)

        if not os.path.exists(file_path):
            main_logger.error(f"Rörelsefil saknas för ubåt {drone_id}: {file_path}")
            return

        main_logger.info(f"Läser rörelserapport för ubåt: {drone_id}")

        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            async for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    command, value_str = parts
                    try:
                        value = int(value_str)
                        yield command, value
                    except ValueError:
                        continue

    async def load_sensor_data(self, drone_id: str) -> AsyncGenerator[str, None]:
        """
        Async generator: yields each raw line from the sensor data file for one drone.
        """
        file_path = sensor_file_path(drone_id)

        if not os.path.exists(file_path):
            main_logger.error(f"Sensordata saknas för ubåt {drone_id}: {file_path}")
            return

        main_logger.info(f"Läser sensordata för ubåt: {drone_id}")

        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            async for line in f:
                clean = line.strip()
                if clean:
                    yield clean
