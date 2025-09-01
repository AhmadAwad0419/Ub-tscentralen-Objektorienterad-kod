import os
from config.paths import movement_file_path

class FileReader:

    def load_movements(self, drone_id):
        """ A generator that yields one movement command at a time.
        """
        file_path = movement_file_path(drone_id)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip()
                    command, value = parts.split()
                    try:
                        yield (command, int(value))
                    except ValueError:
                        #log error
                        yield None
        except FileNotFoundError:
            #log error
            yield None
                
    
