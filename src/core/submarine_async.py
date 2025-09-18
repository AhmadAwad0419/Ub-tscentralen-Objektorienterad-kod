# src/core/submarine_async.py
import asyncio
from typing import Optional, AsyncGenerator, Tuple

class Submarine:
    """
    A submarine drone that can run as an async task.
    It owns its own movement generator and state.
    """
    def __init__(self, id: str):
        self.id = id
        self._x = 0
        self._y = 0
        self._active = True
        self.movements: list[tuple[str, int]] = []
        self._gen: Optional[AsyncGenerator[tuple[str,int], None]] = None

    # --- Properties ---
    @property
    def position(self) -> Tuple[int,int]:
        return self._x, self._y

    @property
    def is_active(self) -> bool:
        return self._active

    @is_active.setter
    def is_active(self, val: bool):
        self._active = bool(val)

    def attach_generator(self, gen: AsyncGenerator[tuple[str,int], None]):
        """Attach an async generator (usually from FileReader)."""
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

    async def run(self, tick_delay: float = 0.0):
        """
        Run this submarine as an independent async task.
        Reads one movement per tick from its generator.
        """
        if not self._gen:
            raise RuntimeError(f"No generator attached for sub {self.id}")

        while self._active:
            try:
                command, value = await self._gen.__anext__()
                self.apply_movement(command, value)
            except StopAsyncIteration:
                self._active = False

            if tick_delay:
                await asyncio.sleep(tick_delay)

        print(f"Submarine {self.id} stopped at {self.position}")
