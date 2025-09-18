# src/core/collision_checker.py
from typing import List, Tuple
from src.core.submarine import Submarine

class CollisionChecker:
    """Simple synchronous collision checker."""

    def __init__(self):
        self.collision_log: list[tuple[str, str, tuple[int,int]]] = []

    def check_for_collisions(
        self, submarines: List[Submarine]
    ) -> List[Tuple[Submarine, Submarine, tuple[int,int]]]:
        active_subs = [s for s in submarines if s.is_active]
        position_map: dict[tuple[int,int], Submarine] = {}
        results: list[tuple[Submarine, Submarine, tuple[int,int]]] = []

        for sub in active_subs:
            pos = sub.position
            if pos in position_map:
                other = position_map[pos]
                if not other.is_active:
                    position_map[pos] = sub
                    continue

                id1, id2 = sorted([other.id, sub.id])
                key = (id1, id2, pos)
                if key not in self.collision_log:
                    self.collision_log.append(key)
                    results.append((other, sub, pos))
                    print(f"Collision detected between {id1} and {id2} at {pos}")
                    position_map.pop(pos, None)
            else:
                position_map[pos] = sub

        return results
