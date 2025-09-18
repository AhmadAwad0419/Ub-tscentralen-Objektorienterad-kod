import asyncio
from typing import Dict, List, Tuple
from src.core.submarine_async import Submarine
from src.data.file_reader_async import AsyncFileReader
from src.core.collision_checker_async import AsyncCollisionChecker


class AsyncMovementManager:
    """
    Orchestrates all submarine tasks, monitors their positions and collisions.
    """

    def __init__(self, reader: AsyncFileReader, tick_delay: float = 0.0):
        self.reader = reader
        self.submarines: Dict[str, Submarine] = {}
        self.collision_checker = AsyncCollisionChecker()
        self.tick_delay = tick_delay

    @property
    def active_subs(self) -> List[Submarine]:
        return [s for s in self.submarines.values() if s.is_active]

    async def load_submarines(self, subs: List[Submarine]):
        for sub in subs:
            self.submarines[sub.id] = sub
            agen = self.reader.load_movements(sub.id)
            sub.attach_generator(agen)

    async def run(self):
        # Launch all submarines as independent coroutines
        tasks = [asyncio.create_task(sub.run(self.tick_delay)) for sub in self.submarines.values()]

        round_no = 0
        while any(s.is_active for s in self.submarines.values()):
            round_no += 1
            print(f"\n--- Round {round_no} ---")

            # Collision check each round
            collisions = await self.collision_checker.check_for_collisions_async(self.active_subs)
            for s1, s2, _ in collisions:
                s1.is_active = False
                s2.is_active = False

            await asyncio.sleep(self.tick_delay or 0.1)

        await asyncio.gather(*tasks, return_exceptions=True)
        print("SLUT")
