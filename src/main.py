import sys
import os

from data.file_reader import FileReader
from config.paths import MOVEMENT_REPORTS_DIR
from core.submarine import Submarine
from core.movement_manager import MovementManager
from core.sensor_manager import SensorManager

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def main():

    movement_manager = MovementManager()
    sensor_manager = SensorManager() 

    submarines = []
     
    print("Startar Ubatscentralen...")

    drone_ids = [filename.replace(".txt", "") for filename in os.listdir(MOVEMENT_REPORTS_DIR) if filename.endswith(".txt")]

    for drone_id in drone_ids:
        submarine = Submarine(drone_id)
        submarines.append(submarine)

    for sub in submarines:
        print(sub)
    #file_reader = FileReader()
    #positions = {drone_id: [0,0] for drone_id in drone_ids}
    #generators = {drone_id: file_reader.load_movements(drone_id) for drone_id in drone_ids}
        
if __name__ == "__main__":
    main()
