import asyncio
from typing import List, Tuple
from src.core.submarine_async import Submarine


class AsyncCollisionChecker:
    """
    Async version of the collision checker.
    Parallelizes collision checks across submarines for large fleets.
    """

    def __init__(self):
        self.collision_log: list[tuple[str, str, tuple[int, int]]] = []

    async def check_for_collisions_async(
        self, submarines: List[Submarine]
    ) -> List[Tuple[Submarine, Submarine, Tuple[int, int]]]:
        """
        Checks for collisions among active submarines asynchronously.
        Returns a list of (sub1, sub2, position).
        """
        active_subs = [s for s in submarines if s.is_active]
        position_map: dict[tuple[int, int], Submarine] = {}
        results: list[tuple[Submarine, Submarine, tuple[int, int]]] = []

        async def process_sub(sub: Submarine):
            pos = sub.position
            if pos in position_map:
                other = position_map[pos]
                if not other.is_active:
                    position_map[pos] = sub
                    return

                id1, id2 = sorted([other.id, sub.id])
                key = (id1, id2, pos)
                if key not in self.collision_log:
                    self.collision_log.append(key)
                    results.append((other, sub, pos))
                    print(f"Collision detected between {id1} and {id2} at position {pos}")
                    position_map.pop(pos, None)
            else:
                position_map[pos] = sub

        # Run all sub position checks concurrently
        tasks = [process_sub(sub) for sub in active_subs]
        if tasks:
            await asyncio.gather(*tasks)

        return results
