import os

class SensorManager:
    
    def load_sensor_data(self, file_path):
        """Generator to load sensor data from a file line by line."""
        with open(file_path, 'r') as file:
            for line in file:
                yield line.strip()
#         This method uses a generator to read large sensor logs line by line.      
    def analyze_data(self, file_path):
        """Analyze sensor data to count errors and patterns."""
        error_count = 0
        pattern_count = {}

        for line in self.load_sensor_data(file_path):
            # Count errors (0s) in the line
            errors_in_line = line.count('0')
            error_count += errors_in_line

            # Count occurrences of each unique pattern
            if line in pattern_count:
                pattern_count[line] += 1
            else:
                pattern_count[line] = 1

        return error_count, pattern_count
    
    def save_analysis(self, analysis, output_path):
        """Save the analysis results to a file."""
        error_count, pattern_count = analysis
        with open(output_path, 'w') as file:
            file.write(f"Total Errors: {error_count}\n")
            file.write("Pattern Counts:\n")
            for pattern, count in pattern_count.items():
                file.write(f"{pattern}: {count}\n")
    def process_sensor_file(self, input_path, output_path):
        """Process a sensor data file and save the analysis."""
        analysis = self.analyze_data(input_path)
        self.save_analysis(analysis, output_path)

    def process_sensor_by_serial(self, serial_number, data_folder, output_path):
        """
        Process sensor data for a specific submarine serial number.
        Args:
            serial_number (str): Submarine's unique serial number.
            data_folder (str): Path to the folder containing sensor data files.
            output_path (str): Path to save the analysis output file.
        """
        # Construct the file name based on the serial number
        file_name = f"sensor_data_{serial_number}.txt"
        file_path = os.path.join(data_folder, file_name)

        # Check if the data file exists
        if not os.path.isfile(file_path):
            print(f"Data file for serial number {serial_number} not found.")
            return

        # Process the sensor data file
        self.process_sensor_file(file_path, output_path)








