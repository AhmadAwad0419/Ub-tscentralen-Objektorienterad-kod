import time
from typing import Dict, List, Generator, Tuple
from src.core.submarine import Submarine
from src.data.file_reader import FileReader
from src.core.collision_checker import CollisionChecker
from src.utils.logger import movement_logger, log_calls

class MovementManager:
    """
    Synchronous orchestrator: steps all submarines in lockstep rounds.
    """

    def __init__(self, reader: FileReader, tick_delay: float = 0.0):
        self.reader = reader
        self.submarines: Dict[str, Submarine] = {}
        self.collision_checker = CollisionChecker()
        self.tick_delay = tick_delay

    @property
    def active_subs(self) -> List[Submarine]:
        return [s for s in self.submarines.values() if s.is_active]

    def load_submarines_from_generator(self, gen: Generator[Tuple[str, Generator], None, None]):
        """
        Laddar ubåtar direkt från en generator.
        """
        for sub_id, movement_gen in gen:
            sub = Submarine(sub_id)
            sub.attach_generator(movement_gen)
            self.submarines[sub.id] = sub

    def run(self):
        round_no = 0
        while any(s.is_active for s in self.submarines.values()):
            round_no += 1
            active_count = len(self.active_subs)
            movement_logger.movement(f"Round {round_no} ({active_count} active submarines)", level="INFO")

            # Each sub takes one step
            for sub in self.active_subs:
                sub.step()

            # Collision check
            collisions = self.collision_checker.check_for_collisions(self.active_subs)
            for s1, s2, _ in collisions:
                s1.is_active = False
                s2.is_active = False

            if self.tick_delay:
                time.sleep(self.tick_delay)

        print("SLUT")