# src/main.py
import os, sys
import concurrent.futures
import argparse

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.config.paths import MOVEMENT_REPORTS_DIR

from src.gui.control_gui import launch_gui
from src.data.file_reader import FileReader
from src.data.secrets_loader import SecretsLoader
from src.core.submarine import Submarine
from src.data.file_reader import FileReader
from src.core.movement_manager import MovementManager
from src.core.sensor_manager import SensorManager
from src.core.torpedo_system import TorpedoSystem
from src.core.nuke_activation import NukeActivation


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        from src.gui.control_gui import launch_gui
        launch_gui()
        return

    print("Startar Ubåtscentralen...")

    secrets = SecretsLoader()
    if not secrets.load_secrets():
        print("Kunde inte ladda hemligheter. Avslutar.")
        sys.exit(1)

    drone_ids = [
        f.replace(".txt", "")
        for f in os.listdir(MOVEMENT_REPORTS_DIR)
        if f.endswith(".txt")
    ]
    subs = [Submarine(id) for id in drone_ids]

    reader = FileReader()
    manager = MovementManager(reader, tick_delay=1.0)
    manager.load_submarines(subs)
    manager.run()

def run_cli():
    print("Running simulation in CLI mode...")

    reader = FileReader()
    manager = MovementManager(reader, tick_delay=0.0)
    manager.load_submarines_from_generator(reader.load_all_movement_files())

    sensor_manager = SensorManager(reader, manager)

    manager.run(sensor_manager)

    # När alla rundor är klara → kör torped/nuke-steg
    torpedos = TorpedoSystem()
    secrets = SecretsLoader()
    nuke = NukeActivation(secrets_loader=secrets, torpedo_system=torpedos)

    print("\n--- Nuke Activation Stage ---")
    for sub in manager.active_subs:
        print(f"Checking submarine {sub.id} at position {sub.position}")
        nuke.allowed_to_activate(manager.active_subs, sub)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gui", action="store_true", help="Run with GUI")
    args = parser.parse_args()

    if args.gui:
        launch_gui()
    else:
        run_cli()
