import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.config.paths import MOVEMENT_REPORTS_DIR
from src.data.file_reader import FileReader
from src.core.submarine import Submarine
from src.core.movement_manager import MovementManager
from src.core.sensor_manager import SensorManager
from src.data.secrets_loader import SecretsLoader
from src.core.torpedo_system import TorpedoSystem
from src.core.nuke_activation import NukeActivation

def main():
    """
    Huvudfunktion för att starta Ubatscentralen.
    Ansvarar för att initialisera och koordinera huvudkomponenterna.
    """
    print("Startar Ubatscentralen...")

    file_reader = FileReader()
    movement_manager = MovementManager()
    sensor_manager = SensorManager() 
    secrets_loader = SecretsLoader()
    torpedo_system = TorpedoSystem()
    nuke_activation = NukeActivation(secrets_loader, torpedo_system)
    
    submarines = []
     
    drone_ids = [filename.replace(".txt", "") for filename in os.listdir(MOVEMENT_REPORTS_DIR) if filename.endswith(".txt")]

    for drone_id in drone_ids:
        submarine = Submarine(drone_id)
        submarines.append(submarine)

    movement_manager.load_submarines(submarines)
    movement_manager.start_central()

    
    #positions = {drone_id: [0,0] for drone_id in drone_ids}
    #generators = {drone_id: file_reader.load_movements(drone_id) for drone_id in drone_ids}
        
if __name__ == "__main__":
    main()
