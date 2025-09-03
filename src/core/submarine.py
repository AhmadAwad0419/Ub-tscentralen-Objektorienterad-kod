from typing import List, Tuple

class Submarine:
    """A submarine drone with unique serial number and position tracking."""
    def __init__(self, id: int) -> None:
        # # Control the serial number format
        # parts = serial_number.split('-')
        # if len(parts) != 2 or not (parts[0].isdigit() and parts[1].isdigit()):
        #     raise ValueError(f"Invalid serial number format: {serial_number}")
        # if len(parts[0]) != 8 or len(parts[1]) != 2:
        #     raise ValueError(f"Invalid serial number format: {serial_number}")
        
        self.id: str = id
        self.vertical_position: int = 0
        self.horizontal_position: int = 0
        self.movements: List[Tuple[str, int]] = []

    
    def load_movements_data_from_file(self, filename):
        """Read movement commands from file and yield them one at a time."""
        with open(filename, "r") as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) != 2:
                    continue
                direction, distance_str = parts
                try:
                    distance = int(distance_str)
                    yield direction, distance 
                except ValueError:
                    print(f"Invalid line skipped: '{line.strip()}'")
        
    def move_from_position_and_distance(self, direction: str, distance: int) -> None:
        """Update position based on direction and distance."""
        
        if direction not in {"up", "down", "forward"}:
            raise ValueError(f"Invalid direction: {direction}")
        if distance < 0:
            raise ValueError("Distance must be non-negative")
        
        self.movements.append((direction, distance))
        
        if direction == "up":
            self.vertical_position -= distance
        elif direction == "down":
            self.vertical_position += distance
        elif direction == "forward":
            self.horizontal_position += distance    
        
        """log the move"""
        self.movements.append((direction, distance))


    def get_position(self) -> Tuple[int, int]:
        """Return the current position as (horizontal, vertical)."""
        return (self.horizontal_position, self.vertical_position)
    
    def __repr__(self) -> str:
        return (f"Submarine(serial_number={self.id}, "
                f"horizontal_position={self.horizontal_position}, "
                f"vertical_position={self.vertical_position})")
