import pytest
import os
import sys
import random

# Lägger till projektets rotkatalog till Python-sökvägen för att kunna importera moduler
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.config.paths import MOVEMENT_REPORTS_DIR

def get_random_drone_id():
    """
    Hjälpfunktion som väljer en slumpmässig drönar-ID
    från MovementReports-mappen.
    """
    try:
        movement_files = [f for f in os.listdir(MOVEMENT_REPORTS_DIR) if f.endswith(".txt")]
        if not movement_files:
            # Använd pytest.skip för att indikera att testet ska hoppas över om inga filer finns
            pytest.skip(f"Inga filer hittades i mappen: {MOVEMENT_REPORTS_DIR}. Testet hoppas över.")
        
        drone_ids = [os.path.splitext(f)[0] for f in movement_files]
        return random.choice(drone_ids)
    except FileNotFoundError:
        pytest.skip(f"Mappen {MOVEMENT_REPORTS_DIR} hittades inte. Testet hoppas över.")

# Pytest fixture som använder funktionen ovan
@pytest.fixture
def random_drone_id_fixture():
    """
    Pytest fixture som tillhandahåller en slumpmässig drönar-ID
    för tester.
    """
    return get_random_drone_id()