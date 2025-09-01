from data.file_reader import load_movements

class MovementManager:
    def __init__(self):
        self.submarines = []
        self.active_generators = {}

    def load_submarines(self, submarines_list):
        for sub in submarines_list:
            self.submarines.append(sub)
            self.active_generators[sub.id] = load_movements(sub.id)

    
