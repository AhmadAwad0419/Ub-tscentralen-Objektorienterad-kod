from typing import Generator, Tuple
from src.data.file_reader import FileReader
from src.core.movement_manager import MovementManager
from src.utils.logger import sensor_logger, log_calls

class SensorManager:
    """
    Manages loading, analyzing, and saving sensor data.
    """
    def __init__(self, file_reader: FileReader, movement_manager: MovementManager):
        self.file_reader = file_reader
        self.movement_manager = movement_manager

    def analyze_data(self, data_generator: Generator[str, None, None]):
        """Analyze sensor data to count errors and patterns."""
        error_count = 0
        pattern_count = {}

        for line in data_generator:
            errors_in_line = line.count('0')
            error_count += errors_in_line

            if line in pattern_count:
                pattern_count[line] += 1
            else:
                pattern_count[line] = 1

        return error_count, pattern_count
    
    def log_analysis(self, analysis, drone_id: str):
        """Logs the analysis results for a given drone."""
        error_count, pattern_count = analysis
        
    def process_all_sensor_data(self):
        """Processes all sensor data files."""
        print("\n--- Sensor Data Analysis Stage ---")

        sensor_generator = self.file_reader.load_all_sensor_files()
        for sub_id, data_gen in sensor_generator:
            print(f"Analyzing sensor data for submarine {sub_id}...")

            analysis = self.analyze_data(data_gen)
            self.log_analysis(analysis, sub_id)
            print(f"Analysis for {sub_id} has been logged.")

    def process_active_submarines_data(self):
        """Processes sensor data for all active submarines."""
        print("\n--- Sensor Data Analysis Stage ---")

        active_sub_ids = {sub.id for sub in self.movement_manager.active_subs}
        all_sensor_data = self.file_reader.load_all_sensor_files()

        found_active_subs = set()
        for sub_id, data_gen in all_sensor_data:
            if sub_id in active_sub_ids:
                print(f"Analyzing sensor data for submarine {sub_id}...")

                analysis = self.analyze_data(data_gen)
                self.log_analysis(analysis, sub_id)
                print(f"Analysis for {sub_id} has been logged.")
                found_active_subs.add(sub_id)

        missing_subs = active_sub_ids - found_active_subs
        for sub_id in missing_subs:
            print(f"No sensor data file found for submarine {sub_id}. Skipping.")