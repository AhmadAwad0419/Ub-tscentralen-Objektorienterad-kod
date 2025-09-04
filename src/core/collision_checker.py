from typing import List, Tuple, Any
from .submarine import Submarine

class CollisionChecker:
    """Check for collisions between submarines based on their positions."""
    def __init__(self):
        # (sub1_id, sub2_id, position)
        self.collision_log: List[Tuple[Any, Any, Tuple[int, int]]] = []

    def check_for_collisions(self, submarines: List[Submarine]) -> List[Tuple[Submarine, Submarine, Tuple[int, int]]]:
        """
        Check for collisions among a list of Submarine objects.
        Returns a list of newly detected collisions as tuples: (sub1, sub2, position).
        """
        position_map = {}
        new_collisions: List[Tuple[Submarine, Submarine, Tuple[int, int]]] = []

        for sub in submarines:
            pos = sub.get_position()      
            if pos in position_map:
                other_sub = position_map[pos]
                entry_ids = (getattr(other_sub, "id", None), getattr(sub, "id", None), pos)
                if entry_ids not in self.collision_log:
                    # record and print once per unique collision
                    self.collision_log.append(entry_ids)
                    print(f"Collision detected between {entry_ids[0]} and {entry_ids[1]} at position {pos}")
                    new_collisions.append((other_sub, sub, pos))
            else:
                position_map[pos] = sub

        return new_collisions

    def log_collision(self, sub1: Submarine, sub2: Submarine, position: Tuple[int, int]):
        """Optional helper to log collisions by id (kept for compatibility)."""
        entry = (getattr(sub1, "id", None), getattr(sub2, "id", None), position)
        if entry not in self.collision_log:
            self.collision_log.append(entry)
            print(f"Collision detected between {entry[0]} and {entry[1]} at position {position}")
        return entry
