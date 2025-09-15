import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.movement_manager import MovementManager

def test_movement_manager():

    print("--- TESTAR MOVEMENTS MANAGER ---")
    movement_manager = MovementManager()
    

if __name__ == "__main__":
    test_movement_manager()

