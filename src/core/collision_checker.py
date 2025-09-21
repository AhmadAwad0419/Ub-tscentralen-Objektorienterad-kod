from typing import List, Tuple
from src.core.submarine import Submarine
from src.utils.logger import collision_logger
from collections import defaultdict
from itertools import combinations

class CollisionChecker:
    """Handles collision detection between submarines."""

    def __init__(self):
        self.collision_log: list[tuple[str, str, tuple[int, int]]] = []

    def check_for_collisions(
        self, submarines: List[Submarine]
    ) -> List[Tuple[Submarine, Submarine, tuple[int, int]]]:
        """
        Checks for collisions between active submarines.
        """
        active_subs = [s for s in submarines if s.is_active]
        position_map: defaultdict[tuple[int, int], list[Submarine]] = defaultdict(list)
        for sub in active_subs:
            position_map[sub.position].append(sub)

        results: list[tuple[Submarine, Submarine, tuple[int, int]]] = []
        for pos, subs_at_pos in position_map.items():
            if len(subs_at_pos) > 1:
                for sub1, sub2 in combinations(subs_at_pos, 2):
                    id1, id2 = sorted([sub1.id, sub2.id])
                    key = (id1, id2, pos)
                    if key not in self.collision_log:
                        self.collision_log.append(key)
                        results.append((sub1, sub2, pos))
                        collision_logger.collision(
                            f"Collision detected between {id1} and {id2} at {pos}",
                            level="CRITICAL",
                        )

        return results
