import os
import pytest
import sys
from unittest.mock import MagicMock


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
     sys.path.insert(0, PROJECT_ROOT)

from src.core.submarine import Submarine

class TestSubmarine:
    def testing_movements_and_update_position(self):
        """ Test movement application and position updates. """
        sub = Submarine("TEST_SUB")
        sub.apply_movement("forward", 5)
        sub.apply_movement("down", 3)

        assert sub.position == (5, 3)
        assert sub.movements == [("forward", 5), ("down", 3)]


    def test_invalid_direction_raises_value_error(self):
        """ Test that invalid direction raises ValueError. """
        sub = Submarine("TEST_SUB_1")
        with pytest.raises(ValueError):
            sub.apply_movement("backward", 5)

    def test_negative_distance_raises_value_error(self):
        """ Test that negative distance raises ValueError. """
        sub = Submarine("TEST_SUB_2")
        with pytest.raises(ValueError):
            sub.apply_movement("forward", -3)

    def test_step_with_mock_generator(self):
        """ Test stepping through movements using a mock generator. """
        sub = Submarine("TEST_SUB_3")
        mock_gen = MagicMock()
        mock_gen.__next__.side_effect = [("forward", 4), ("up", 2), StopIteration]

        sub.attach_generator(mock_gen)

        sub.step()
        assert sub.position == (4, 0)

        sub.step()
        assert sub.position == (4, -2)

        sub.step()
        assert sub.is_active is False


    def test_step_without_generator_does_nothing(self):
        """ Test that step does nothing if no generator is attached. """
        sub = Submarine("TEST_SUB_4")
        sub.is_active = False
        gen = MagicMock()
        sub.attach_generator(gen)

        sub.step()
        gen.__next__.assert_not_called() # Generator should not be called if sub is inactive