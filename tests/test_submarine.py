import os
import pytest
import sys
from src.core.submarine import Submarine

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

@pytest.fixture
def submarine():
    """fixture for submarine instance."""
    return Submarine()

def test_initial_position(submarine):
    """Test a new submarine  (0, 0)."""
    assert submarine.get_position() == (0, 0)

def test_move_up(submarine):
    submarine.move_from_position_and_distance("up", 5)
    assert submarine.get_position() == (0, -5)

def test_move_down(submarine):
    submarine.move_from_position_and_distance("down", 3)
    assert submarine.get_position() == (0, 3)

def test_move_forward(submarine):
    submarine.move_from_position_and_distance("forward", 10)
    assert submarine.get_position() == (10, 0)

def test_multiple_moves(submarine):
    submarine.move_from_position_and_distance("down", 5)
    submarine.move_from_position_and_distance("forward", 8)
    submarine.move_from_position_and_distance("up", 3)
    assert submarine.get_position() == (8, 2)

def test_invalid_direction(submarine):
    with pytest.raises(ValueError):
        submarine.move_from_position_and_distance("backward", 5)

def test_negative_distance(submarine):
    with pytest.raises(ValueError):
        submarine.move_from_position_and_distance("forward", -1)

def test_load_movements_from_file(tmp_path, submarine):
    """Testa att läsa in rörelser från en temporär testfil."""
    file_path = tmp_path / "movements.txt"
    file_path.write_text("forward 5\nup 2\ndown 3\ninvalid_line\nforward x\n")

    moves = list(submarine.load_movements_data_from_file(file_path))
    assert moves == [("forward", 5), ("up", 2), ("down", 3)]