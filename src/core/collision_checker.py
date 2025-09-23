# src/core/collision_checker.py
from typing import List, Tuple
from src.core.submarine import Submarine
from src.utils.logger import collision_logger, log_calls


class CollisionChecker:
    """Simple synchronous collision checker."""

    def __init__(self):
        self.collision_log: list[tuple[str, str, tuple[int,int]]] = []

    @log_calls(collision_logger, "collision", context_args=["submarines"])
    def check_for_collisions(self, submarines: List[Submarine]):
        # Gruppera subs per position
        position_map: dict[tuple[int, int], list[Submarine]] = {}
        for sub in submarines:
            if not sub.is_active:
                continue
            position_map.setdefault(sub.position, []).append(sub)

        collisions: List[Tuple[Submarine, Submarine, tuple[int, int]]] = []

        for pos, subs_at_pos in position_map.items():
            if len(subs_at_pos) >= 2:
                # Alla subs på samma plats dör
                ids = [s.id for s in subs_at_pos]
                for s in subs_at_pos:
                    s.is_active = False

                # Lägg in alla krockpar i loggen
                for i in range(len(subs_at_pos)):
                    for j in range(i + 1, len(subs_at_pos)):
                        collisions.append((subs_at_pos[i], subs_at_pos[j], pos))
                        self.collision_log.append((subs_at_pos[i].id, subs_at_pos[j].id, pos))

                if len(subs_at_pos) == 2:
                    collision_logger.critical(
                        f"Collision at {pos} → {ids[0]} and {ids[1]} destroyed"
                    )
                else:
                    collision_logger.critical(
                        f"Mass collision at {pos} → subs {', '.join(ids)} destroyed"
                    )

        return collisions