from src.utils.logger import movement_logger, log_calls, collision_logger, sensor_logger
from src.core.submarine import Submarine
from src.core.collision_checker import CollisionChecker
from src.core.sensor_manager import SensorManager
import time

class MovementManager:
    def __init__(self, reader, tick_delay=0.0):
        self.file_reader = reader
        self.submarines = {}
        self.tick_delay = tick_delay
        self.collision_checker = CollisionChecker()

    def load_submarines_from_generator(self, gen):
        for sub_id, movement_gen in gen:
            sub = Submarine(sub_id)
            sub.attach_generator(movement_gen)
            self.submarines[sub.id] = sub
            sub.attach_generator(self.file_reader.load_movements(sub.id))

    @property
    def active_subs(self):
        return [s for s in self.submarines.values() if s.is_active]

    def check_collisions(self):
        """Kontrollerar kollisioner mellan aktiva ubåtar."""
        return self.collision_checker.check_for_collisions(self.active_subs)

    @log_calls(movement_logger, "movement")
    def step_round(self, round_counter: int, sensor_manager) -> None:
        """Kör en enda runda: move, kollision, sensorer"""
        movement_logger.info(
            f"Round {round_counter} ({len(self.active_subs)} active submarines)"
        )

        positions: dict[tuple[int, int], object] = {}

        for sub in list(self.active_subs):
            if sub._gen is None:
                continue
            sub.step()
            pos = sub.position
            if pos in positions and positions[pos].is_active:
                other = positions[pos]
                sub.is_active = False
                other.is_active = False
                movement_logger.critical(
                    f"Collision at {pos}: {sub.id} and {other.id} destroyed"
                )
                collision_logger.critical(
                        f"Collision at {pos}: {sub.id} and {other.id} destroyed"
                )
            else:
                positions[pos] = sub

        # sensorerna körs bara på aktiva subs
        sensor_manager.process_all_sensor_data(only_active=True)
        sensor_logger.info(
        f"[Sensor] Round {round_counter} finished → {len(self.active_subs)} subs left"
    )
        if self.tick_delay > 0:
            time.sleep(self.tick_delay)

    def run(self, sensor_manager):
        """Kör hela simuleringen tills inga subs kan röra sig längre."""
        round_counter = 1

        while True:
            # Kolla om det finns minst en aktiv ubåt med en generator kvar
            can_move = any(
                sub.is_active and sub._gen is not None
                for sub in self.submarines.values()
            )
            if not can_move:
                break

            self.step_round(round_counter, sensor_manager)
            round_counter += 1

        movement_logger.info("Simulation finished")


    """def run(self):
        round_counter = 1

        while any(sub.is_active for sub in self.submarines.values()):
            movement_logger.info(
                f"Round {round_counter} ({len(self.active_subs)} active submarines)"
            )

            positions: dict[tuple[int, int], object] = {}

            for sub in list(self.active_subs):
                sub.step()
                pos = sub.position
                if pos in positions and positions[pos].is_active:
                    other = positions[pos]
                    sub.is_active = False
                    other.is_active = False
                    movement_logger.critical(
                        f"Collision at {pos}: {sub.id} and {other.id} destroyed"
                    )
                else:
                    positions[pos] = sub

            if self.tick_delay > 0:
                time.sleep(self.tick_delay)

            round_counter += 1

        # När alla rundor är klara → kör sensorerna en gång
        if self.file_reader:
            sensor_manager = SensorManager(self.file_reader, self)
            sensor_manager.process_all_sensor_data()

        movement_logger.info("Simulation finished")

    def run_round(self, round_counter: int):
        #Kör en enskild runda (för GUI/live uppdatering).

        movement_logger.info(
            f"Round {round_counter} ({len(self.active_subs)} active submarines)"
        )

        positions: dict[tuple[int, int], object] = {}

        for sub in list(self.active_subs):
            sub.step()
            pos = sub.position
            if pos in positions and positions[pos].is_active:
                other = positions[pos]
                sub.is_active = False
                other.is_active = False
                movement_logger.critical(
                    f"Collision at {pos}: {sub.id} and {other.id} destroyed"
                )
            else:
                positions[pos] = sub

        if self.tick_delay > 0:
            time.sleep(self.tick_delay)"""
