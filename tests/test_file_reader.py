import pytest
import os
import sys
import tempfile

# Lägger till projektets rotkatalog till Python-sökvägen för att kunna importera moduler
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data.file_reader import FileReader

# Pytest fixtures
@pytest.fixture
def file_reader():
    """
    Fixture som skapar en instans av FileReader för varje test.
    """
    return FileReader()

@pytest.fixture
def monkeypatch_paths(monkeypatch):
    """
    Fixture som använder monkeypatch för att peka om de interna sökvägarna
    i FileReader till temporära filer. Detta garanterar att testerna
    är isolerade och inte beroende av den verkliga filstrukturen.
    """
    # Skapa temporär mapp för testfiler
    temp_dir = tempfile.TemporaryDirectory()
    temp_path = temp_dir.name

    # Skapa temporära filer med känt innehåll
    movement_path = os.path.join(temp_path, "test_movements.txt")
    with open(movement_path, "w", encoding='utf-8') as f:
        f.write("UP 10\nDOWN 20\nFORWARD 5\nINVALID LINE\nBACKWARD 15")

    sensor_path = os.path.join(temp_path, "test_sensor_data.txt")
    with open(sensor_path, "w", encoding='utf-8') as f:
        f.write("1\n0\n1\nINVALID\n0")

    # Monkeypatchar de funktioner i FileReader som returnerar sökvägar
    monkeypatch.setattr("src.data.file_reader.movement_file_path", lambda drone_id: movement_path)
    monkeypatch.setattr("src.data.file_reader.sensor_file_path", lambda drone_id: sensor_path)

    # Returnerar sökvägarna för användning i testerna, om det behövs
    yield {
        "movement_path": movement_path,
        "sensor_path": sensor_path
    }
    # Städar upp den temporära mappen efter att testerna är klara
    temp_dir.cleanup()

# Testfunktioner 

def test_load_movements_correctly(file_reader, monkeypatch_paths):
    """
    Testar att load_movements läser och bearbetar kommandon korrekt
    från en temporär fil.
    """
    movements = list(file_reader.load_movements("dummy_drone_id"))
    
    expected_result = [("UP", 10), ("DOWN", 20), ("FORWARD", 5), ("BACKWARD", 15)]
    assert movements == expected_result


def test_load_movements_file_not_found(file_reader, monkeypatch):
    """
    Testar hur load_movements hanterar ett fel när en fil inte hittas.
    """
    monkeypatch.setattr("src.data.file_reader.movement_file_path", lambda drone_id: "/non/existent/path/file.txt")
    
    movements = list(file_reader.load_movements("dummy_drone_id"))
    # Generatorn returnerar ingenting om filen inte hittas, så listan är tom.
    assert movements == []


def test_load_sensor_data_correctly(file_reader, monkeypatch_paths):
    """
    Testar att load_sensor_data läser rader korrekt från en temporär fil
    och konverterar dem till heltal.
    """
    sensor_data = list(file_reader.load_sensor_data("dummy_drone_id"))
    
    expected_result = [1, 0, 1, 0]
    assert sensor_data == expected_result


def test_load_sensor_data_file_not_found(file_reader, monkeypatch):
    """
    Testar hur load_sensor_data hanterar ett fel när en fil inte hittas.
    """
    monkeypatch.setattr("src.data.file_reader.sensor_file_path", lambda drone_id: "/non/existent/path/sensor.txt")
    
    sensor_data = list(file_reader.load_sensor_data("dummy_drone_id"))
    # Generatorn returnerar ingenting om filen inte hittas, så listan är tom.
    assert sensor_data == []