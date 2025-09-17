import sys
import os
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from core.sensor_manager import SensorManager

@pytest.fixture
def sensor_manager():
    return SensorManager()

def create_temp_file(contents):
    temp = tempfile.NamedTemporaryFile(delete=False, mode='w+', encoding='utf-8')
    temp.write(contents)
    temp.close()
    return temp.name

def test_load_sensor_data(sensor_manager):
    contents = "1010\n1100\n0000\n"
    file_path = create_temp_file(contents)
    data = list(sensor_manager.load_sensor_data(file_path))
    assert data == ["1010", "1100", "0000"]
    os.remove(file_path)

def test_analyze_data(sensor_manager):
    contents = "1010\n1100\n0000\n"
    file_path = create_temp_file(contents)
    error_count, pattern_count = sensor_manager.analyze_data(file_path)
    # error_count borde vara 8. 2 in 1010, 2 in 1100, 4 in 0000. Testet misslyckas annars
    assert error_count == 8  # 2 in 1010, 2 in 1100, 3 in 0000
    assert pattern_count == {"1010": 1, "1100": 1, "0000": 1}
    os.remove(file_path)

def test_save_analysis(sensor_manager):
    analysis = (5, {"1010": 2, "1100": 1})
    with tempfile.NamedTemporaryFile(delete=False, mode='r+', encoding='utf-8') as temp:
        output_path = temp.name
    sensor_manager.save_analysis(analysis, output_path)
    with open(output_path, 'r') as f:
        content = f.read()
    assert "Total Errors: 5" in content
    assert "1010: 2" in content
    assert "1100: 1" in content
    os.remove(output_path)

def test_process_sensor_file(sensor_manager):
    contents = "1010\n1010\n1100\n"
    input_path = create_temp_file(contents)
    with tempfile.NamedTemporaryFile(delete=False, mode='r+', encoding='utf-8') as temp:
        output_path = temp.name
    sensor_manager.process_sensor_file(input_path, output_path)
    with open(output_path, 'r') as f:
        content = f.read()
        # "Total Errors" borde vara 6. 2 i 1010, 2 i 1010, 2 1100. Testet misslyckas annars
    assert "Total Errors: 6" in content
    assert "1010: 2" in content
    assert "1100: 1" in content
    os.remove(input_path)
    os.remove(output_path)

def test_process_sensor_by_serial_found(sensor_manager):
    contents = "1010\n1100\n"
    with tempfile.TemporaryDirectory() as data_folder:
        serial_number = "ABC123"
        file_name = f"sensor_data_{serial_number}.txt"
        file_path = os.path.join(data_folder, file_name)
        with open(file_path, 'w') as f:
            f.write(contents)
        output_path = os.path.join(data_folder, "output.txt")
        sensor_manager.process_sensor_by_serial(serial_number, data_folder, output_path)
        with open(output_path, 'r') as f:
            content = f.read()
        assert "Total Errors: 4" in content
        assert "1010: 1" in content
        assert "1100: 1" in content

def test_process_sensor_by_serial_not_found(sensor_manager, capsys):
    with tempfile.TemporaryDirectory() as data_folder:
        serial_number = "NOTFOUND"
        output_path = os.path.join(data_folder, "output.txt")
        sensor_manager.process_sensor_by_serial(serial_number, data_folder, output_path)
        captured = capsys.readouterr()
        assert f"Data file for serial number {serial_number} not found." in captured.out