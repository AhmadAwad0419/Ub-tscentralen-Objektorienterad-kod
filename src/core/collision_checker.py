from submarine import Submarine


class CollisionChecker:
    """Check for collisions between submarines based on their positions."""
    def __init__(self):
        self.collision_log = []
        
    def check_for_collisions(self, submarine_positions):
        """Check for collisions among a list of submarine positions."""
        position_map = {}
        
        for sub in submarine_positions:
            pos = sub.get_position()
            if pos in position_map:
                other_sub = position_map[pos]
                yield self.log_collision(sub, other_sub, pos)
                self.collision_log.append((sub, other_sub, pos))
            else:
                position_map[pos] = sub
    
    def log_collision(self, sub1, sub2, position):
        """Log and return a collision event."""
        entry = (sub1.serial_number, sub2.serial_number, position)
        if entry not in self.collision_log:
            self.collision_log.append(entry)    
            print(f"Collision detected between {sub1.serial_number} and {sub2.serial_number} at position {position}")
        return entry          
