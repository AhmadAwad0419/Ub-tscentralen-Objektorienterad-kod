import os, sys
import concurrent.futures

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data.file_reader import FileReader
from src.data.secrets_loader import SecretsLoader
from src.core.movement_manager import MovementManager
from src.core.torpedo_system import TorpedoSystem
from src.core.nuke_activation import NukeActivation
from src.core.sensor_manager import SensorManager

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        from src.gui.gui2 import main as gui_main
        gui_main()
        return

    print("Startar Ubåtscentralen...")
    
    reader = FileReader()
    manager = MovementManager(reader, tick_delay=0.0)
    
    manager.load_submarines_from_generator(reader.load_all_movement_files())

    sensor_manager = SensorManager(reader, manager)
    def sensor_process():
        sensor_manager.process_all_sensor_data()

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        print("Kör MovementManager och SensorManager parallellt...")
        executor.submit(manager.run)
        executor.submit(sensor_process)

    torpedos = TorpedoSystem()
    secrets = SecretsLoader()
    nuke = NukeActivation(secrets_loader=secrets, torpedo_system=torpedos)
    
    print("\n--- Nuke Activation Stage ---")

    def check_nuke_activation(sub):
        print(f"Checking submarine {sub.id} at position {sub.position}")
        nuke.allowed_to_activate(manager.active_subs, sub)

    for sub in manager.active_subs:
        check_nuke_activation(sub)

if __name__ == "__main__":
    main()