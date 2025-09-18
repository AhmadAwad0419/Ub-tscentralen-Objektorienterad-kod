from data.file_reader import FileReader
from .collision_checker import CollisionChecker
from .torpedo_system import TorpedoSystem
from time import sleep

class MovementManager:
    def __init__(self):
        self.submarines = {}  # Dictionary: {id: submarine_object}
        self.active_generators = {}

    def load_submarines(self, submarines_list):
        file_reader = FileReader()
        for sub in submarines_list:
            self.submarines[sub.id] = sub  # Store by ID
            self.active_generators[sub.id] = file_reader.load_movements(sub.id)

    def move_from_position_and_distance(self, submarine, direction: str, distance: int) -> None:
        """Update position based on direction and distance."""
    
        if direction not in {"up", "down", "forward"}:
            raise ValueError(f"Invalid direction: {direction}")
        if distance < 0:
            raise ValueError("Distance must be non-negative")
        
        # Update position
        if direction == "up":
            submarine.vertical_position -= distance
        elif direction == "down":
            submarine.vertical_position += distance
        elif direction == "forward":
            submarine.horizontal_position += distance    
        
        # Log the move
        submarine.movements.append((direction, distance))

    def start_central(self):
        collision_checker = CollisionChecker()

        while any(sub.is_active for sub in self.submarines.values()):
            finished_subs = []

            # Process movements for all active submarines
            for sub_id, generator in list(self.active_generators.items()):
                sub = self.submarines.get(sub_id)
                if not sub or not sub.is_active:
                    continue
                    
                try:
                    movement = next(generator)
                    if movement is not None:
                        command, value = movement
                        sub = self.submarines.get(sub_id)
                        if sub is not None:
                            self.move_from_position_and_distance(sub, command, value)
                        else:
                            print(f"Warning: Submarine id {sub_id} is not found. Skipping")
                except StopIteration:
                    finished_subs.append(sub_id)
            
            # Remove finished submarines
            for sub_id in finished_subs:
                if sub_id in self.active_generators:        
                    del self.active_generators[sub_id]
            
            # Check collisions only on active submarines
            active_subs = [s for s in self.submarines.values() if s.is_active]
            new_collisions = collision_checker.check_for_collisions(active_subs)
            
            for sub1, sub2, position in new_collisions:
                sub1.is_active = False
                sub2.is_active = False

                if sub1.id in self.active_generators:
                    del self.active_generators[sub1.id]
                if sub2.id in self.active_generators:
                    del self.active_generators[sub2.id]  

            if not self.active_generators:
                break

            sleep(0.5)

        # Run friendly-fire checks
        torpedo_system = TorpedoSystem()
        for sub in self.submarines.values():
            report = torpedo_system.get_friendly_fire_report(list(self.submarines.values()), sub)
            torpedo_system.log_torpedo_launch(sub, report)

            #self._calculate_statistics()
            #self._final_report()
            #self._update_gui_with_final_positions()