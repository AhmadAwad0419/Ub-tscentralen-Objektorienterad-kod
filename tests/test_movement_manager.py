import sys
import os
import pytest
from unittest.mock import Mock

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.movement_manager import MovementManager

# Pytest fixtures

@pytest.fixture
def mock_movement_report():
    ...

