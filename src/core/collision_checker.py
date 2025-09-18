from typing import List, Tuple, Any
from .submarine import Submarine

class CollisionChecker:
    """Check for collisions between submarines based on their positions."""
    def __init__(self):
        self.collision_log: List[Tuple[Any, Any, Tuple[int, int]]] = []

    def check_for_collisions(self, submarines: List[Submarine]) -> List[Tuple[Submarine, Submarine, Tuple[int, int]]]:
        position_map = {}
        new_collisions: List[Tuple[Submarine, Submarine, Tuple[int, int]]] = []

        for sub in submarines:
            if not sub.is_active:
                continue

            pos = sub.get_position()

            if pos in position_map:
                other_sub = position_map[pos]

                #If the other sub is dead, replace it with the current active one
                if not other_sub.is_active:
                    position_map[pos] = sub
                    continue

                #Normalize ordering so (id1,id2) and (id2,id1) are the same
                id1, id2 = sorted([other_sub.id, sub.id])
                entry_ids = (id1, id2, pos)

                if entry_ids not in self.collision_log:
                    self.collision_log.append(entry_ids)
                    print(f"Collision detected between {id1} and {id2} at position {pos}")
                    new_collisions.append((other_sub, sub, pos))

                    #Remove both subs from the map right away (prevents ghost collisions)
                    if pos in position_map:
                        del position_map[pos]
            else:
                position_map[pos] = sub

        return new_collisions


    def log_collision(self, sub1: Submarine, sub2: Submarine, position: Tuple[int, int]):
        """Optional helper to log collisions by id (kept for compatibility)."""
        id1, id2 = sorted([sub1.id, sub2.id])
        entry = (id1, id2, position)
        if entry not in self.collision_log:
            self.collision_log.append(entry)
            print(f"Collision detected between {entry[0]} and {entry[1]} at position {position}")
        return entry
