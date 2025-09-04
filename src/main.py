import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data.file_reader import FileReader
from src.config.paths import MOVEMENT_REPORTS_DIR
from src.core.submarine import Submarine
from src.core.movement_manager import MovementManager
from src.core.sensor_manager import SensorManager
from src.data.secrets_loader import SecretsLoader

def main():
    """
    Huvudfunktion för att starta Ubatscentralen.
    Ansvarar för att initialisera och koordinera huvudkomponenterna.
    """
    print("Startar Ubatscentralen...")

    movement_manager = MovementManager()
    sensor_manager = SensorManager() 
    secrets_loader = SecretsLoader()

    # Försök ladda secrets
    if not secrets_loader.load_secrets():
        print("Kunde inte ladda hemligheter. Avslutar programmet.")
        sys.exit(1)

    submarines = []
     
    drone_ids = [filename.replace(".txt", "") for filename in os.listdir(MOVEMENT_REPORTS_DIR) if filename.endswith(".txt")]

    for drone_id in drone_ids:
        submarine = Submarine(drone_id)
        submarines.append(submarine)

    movement_manager.load_submarines(submarines)
    movement_manager.start_central()

    #file_reader = FileReader()
    #positions = {drone_id: [0,0] for drone_id in drone_ids}
    #generators = {drone_id: file_reader.load_movements(drone_id) for drone_id in drone_ids}
        
if __name__ == "__main__":
    main()
