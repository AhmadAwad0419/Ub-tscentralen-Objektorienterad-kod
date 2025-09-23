# src/core/submarine.py
from typing import Optional, Generator, Tuple
from src.utils.logger import movement_logger

class Submarine:
    """
    A submarine drone that runs step by step (synchronous).
    Owns its own movement generator and state.
    """
    def __init__(self, id: str):
        self.id = id
        self._x = 0
        self._y = 0
        self._active = True
        self.movements: list[tuple[str, int]] = []
        self._gen: Optional[Generator[tuple[str,int], None, None]] = None

    @property
    def position(self) -> Tuple[int,int]:
        return self._x, self._y

    @property
    def is_active(self) -> bool:
        return self._active

    @is_active.setter
    def is_active(self, val: bool):
        self._active = bool(val)

    def attach_generator(self, gen):
        self._gen = gen

    def apply_movement(self, direction: str, distance: int):
        if direction not in {"up", "down", "forward"}:
            raise ValueError(f"Invalid direction {direction}")
        if distance < 0:
            raise ValueError("Distance must be non-negative")

        self.movements.append((direction, distance))
        ops = {
            "up": lambda: setattr(self, "_y", self._y - distance),
            "down": lambda: setattr(self, "_y", self._y + distance),
            "forward": lambda: setattr(self, "_x", self._x + distance),
        }
        ops[direction]()
        print(f"Sub {self.id} moved {direction} {distance} → pos {self.position}")
        movement_logger.info(f"Sub {self.id} moved {direction} {distance} → pos {self.position}")


    def step(self):
        if not self._gen or not self._active:
            return
        try:
            command, value = next(self._gen)
            #print(f"Stepping with {self.id} to {command} and {value}")
            self.apply_movement(command, value)
        except StopIteration:
            print(f"Sub {self.id} ran out of moves!")
            self._gen = None

    def __repr__(self):
        return f"Submarine({self.id}, pos={self.position}, active={self.is_active})"
