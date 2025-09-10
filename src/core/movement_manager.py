from data.file_reader import FileReader
from .collision_checker import CollisionChecker
from .torpedo_system import TorpedoSystem

class MovementManager:
    def __init__(self):
        self.submarines = []
        self.active_generators = {}

    def load_submarines(self, submarines_list):
        file_reader = FileReader()
        for sub in submarines_list:
            self.submarines.append(sub)
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
        while self.active_generators:
            finished_subs = []
            for sub_id, generator in self.active_generators.items():
                try:
                    movement = next(generator)
                    if movement is not None:
                        command, value = movement
                        sub = next((s for s in self.submarines if s.id == sub_id), None)
                        if sub is not None:
                            self.move_from_position_and_distance(sub, command, value)
                        else:
                            print(f"Warning: Submarine id {sub_id} is not found. Skipping")
                except StopIteration:
                    finished_subs.append(sub_id)
            
            # Ta bort ubåtar som är färdiga
            for sub_id in finished_subs:        
                del self.active_generators[sub_id]
                    
        #Check for collisions after this batch of movements
        new_collisions = CollisionChecker().check_for_collisions(self.submarines)
        if new_collisions:
                for sub1, sub2, position in new_collisions:
                    self.collision_checker.log_collision(sub1, sub2, position)
                    for sid in (getattr(sub1, "id", None), getattr(sub2, "id", None)):
                        if sid in self.active_generators:
                            del self.active_generators[sid]
        else:
            print("No collisions detected in this round.")
            
        
        # Run friendly-fire checks for torpedoes using final positions.
        self.torpedo_system = TorpedoSystem()
        for sub in self.submarines:
            report = self.torpedo_system.get_friendly_fire_report(self.submarines, sub)
            self.torpedo_system.log_torpedo_launch(sub, report)