import pytest
import os
import sys

# Lägger till projektets rotkatalog till Python-sökvägen för att kunna importera moduler
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tests.random_file_loader import random_drone_id_fixture
from src.config.paths import movement_file_path, sensor_file_path, secret_key_file_path, activation_codes_file_path

# Testfunktioner för Pytest

def test_movement_file_exists(random_drone_id_fixture):
    """
    Testar att rörelserapportsfilen för en slumpmässig drönare existerar.
    """
    path = movement_file_path(random_drone_id_fixture)
    assert os.path.exists(path)

def test_sensor_file_exists(random_drone_id_fixture):
    """
    Testar att sensordatafilen för en slumpmässig drönare existerar.
    """
    path = sensor_file_path(random_drone_id_fixture)
    assert os.path.exists(path)

def test_secret_key_file_exists():
    """
    Testar att SecretKEY.txt existerar.
    """
    path = secret_key_file_path()
    assert os.path.exists(path)

def test_activation_codes_file_exists():
    """
    Testar att ActivationCodes.txt existerar.
    """
    path = activation_codes_file_path()
    assert os.path.exists(path)