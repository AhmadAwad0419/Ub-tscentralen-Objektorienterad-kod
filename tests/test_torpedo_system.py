import os
import sys
from unittest.mock import Mock
import pytest
from typing import List, Dict, Tuple, Optional

# Lägger till projektets rotkatalog till Python-sökvägen för att kunna importera moduler
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.torpedo_system import TorpedoSystem
from src.core.submarine import Submarine

# Pytest Fixtures

@pytest.fixture
def torpedo_system():
    """
    Fixture som skapar en instans av TorpedoSystem för varje test.
    """
    return TorpedoSystem()

@pytest.fixture
def mock_submarines():
    """
    Skapar mock-ubåtsobjekt med specifika positioner för att testa
    olika scenarier. Returnerar en tuple av (flottan, skyttens ubåt).
    
    Korrigerat: Använder nu .position egenskapen istället för .get_position()
    för att matcha TorpedoSystem klassen.
    """
    # Ubåten som avfyrar
    shooter_sub = Mock(spec=Submarine)
    shooter_sub.id = "DRONE_1"
    shooter_sub.position = (50, 50)
    
    # En ubåt rakt "uppåt" (på samma x, lägre y)
    up_target = Mock(spec=Submarine)
    up_target.id = "UP_TARGET"
    up_target.position = (50, 20)

    # En ubåt rakt "nedåt" (på samma x, högre y)
    down_target = Mock(spec=Submarine)
    down_target.id = "DOWN_TARGET"
    down_target.position = (50, 80)
    
    # En ubåt rakt "framåt" (på samma y, högre x)
    forward_target = Mock(spec=Submarine)
    forward_target.id = "FORWARD_TARGET"
    forward_target.position = (70, 50)

    # En ubåt som är en distraktion och inte i vägen
    distraction_target = Mock(spec=Submarine)
    distraction_target.id = "DISTRACTION"
    distraction_target.position = (10, 10)
    
    submarines_list = [
        shooter_sub, 
        up_target, 
        down_target, 
        forward_target, 
        distraction_target
    ]
    
    return submarines_list, shooter_sub


# Testfunktioner för Pytest

def test_check_for_friendly_fire_generator(torpedo_system, mock_submarines):
    """
    Testar generatorn check_for_friendly_fire.
    """
    submarines, shooter_sub = mock_submarines
    
    results = list(torpedo_system.check_for_friendly_fire(submarines, shooter_sub))
    
    assert len(results) == 3
    assert results[0] == ("up", False, (50, 20))
    assert results[1] == ("down", False, (50, 80))
    assert results[2] == ("forward", False, (70, 50))


def test_get_friendly_fire_report(torpedo_system, mock_submarines):
    """
    Testar funktionen som sammanställer rapporten.
    """
    submarines, shooter_sub = mock_submarines
    
    report = torpedo_system.get_friendly_fire_report(submarines, shooter_sub)
    
    expected_report = {
        "up": {"safe": False, "first_target": (50, 20)},
        "down": {"safe": False, "first_target": (50, 80)},
        "forward": {"safe": False, "first_target": (70, 50)}
    }
    
    assert report == expected_report


def test_log_torpedo_launch_safe(torpedo_system, capsys):
    """
    Testar att log_torpedo_launch loggar korrekt när avfyrningsvägen är säker.
    Använder capsys för att fånga utskrifter till konsolen.
    
    Korrigerat: Använder nu .position egenskapen för mock-objektet.
    """
    mock_submarine = Mock(spec=Submarine, id="DRONE_1", position=(1, 1))
    
    safe_report = {
        "up": {"safe": True, "first_target": None},
        "down": {"safe": True, "first_target": None},
        "forward": {"safe": True, "first_target": None}
    }
    
    torpedo_system.log_torpedo_launch(mock_submarine, safe_report)
    
    captured = capsys.readouterr()
    assert "SAFE" in captured.out
    assert "RISK OF FRIENDLY FIRE" not in captured.out

def test_log_torpedo_launch_with_risk(torpedo_system, capsys):
    """
    Testar att log_torpedo_launch loggar korrekt när det finns en risk.
    
    Korrigerat: Använder nu .position egenskapen för mock-objektet.
    """
    mock_submarine = Mock(spec=Submarine, id="DRONE_1", position=(1, 1))
    
    unsafe_report = {
        "up": {"safe": False, "first_target": (1, 10)},
        "down": {"safe": True, "first_target": None},
        "forward": {"safe": False, "first_target": (5, 1)}
    }
    
    torpedo_system.log_torpedo_launch(mock_submarine, unsafe_report)
    
    captured = capsys.readouterr()
    assert "RISK OF FRIENDLY FIRE" in captured.out
    assert "SAFE" in captured.out
