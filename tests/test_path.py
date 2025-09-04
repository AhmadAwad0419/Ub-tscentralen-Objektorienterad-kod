import sys
import os
import random

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.config.paths import *

def get_random_drone_id():
    """
    Väljer slumpmässig drönartext från MovementReport mappen.
    """
    movement_files = [f for f in os.listdir(MOVEMENT_REPORTS_DIR)if f.endswith(".txt")]

    drone_ids = [os.path.splitext(f)[0] for f in movement_files]

    if not movement_files:
        raise FileNotFoundError(f"Hittade inga filer i mappen {MOVEMENT_REPORTS_DIR}")

    return random.choice(drone_ids)

def path_test():
    """
    Testar så att alla filer finns och hittas av paths.py
    """
    try:
        test_drone_id = get_random_drone_id()

        paths = [
            movement_file_path(test_drone_id),
            sensor_file_path(test_drone_id),
            secret_key_file_path(),
            activation_codes_file_path()
        ]

        for p in paths:
            if os.path.exists(p):
                print(f"HITTAR FILEN: {p}")
            else:
                print(f"HITTAR INTE FILEN: {p}")

    except Exception as e:
        print(f"Fel uppstod: {e}")

if __name__ == "__main__":
    path_test()