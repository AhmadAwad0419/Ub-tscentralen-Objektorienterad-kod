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

    def get_position(self) -> Tuple[int, int]:
        """Return the current position as (horizontal, vertical)."""
        return (self.horizontal_position, self.vertical_position)
    
    def __repr__(self) -> str:
        return (f"Submarine(serial_number={self.id}, "
                f"horizontal_position={self.horizontal_position}, "
                f"vertical_position={self.vertical_position})")
