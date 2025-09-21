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
    """
    # Ubåten som avfyrar
    shooter_sub = Mock(spec=Submarine)
    shooter_sub.position = (50, 50)
    
    # En ubåt rakt "uppåt" (på samma x, lägre y)
    up_target = Mock(spec=Submarine)
    up_target.position = (50, 20)
    
    # En ubåt rakt "nedåt" (på samma x, högre y)
    down_target = Mock(spec=Submarine)
    down_target.position = (50, 80)
    
    # En ubåt rakt "framåt" (på samma y, högre x)
    forward_target = Mock(spec=Submarine)
    forward_target.position = (70, 50)
    
    # En ubåt diagonalt, som inte ska upptäckas
    diagonal_target = Mock(spec=Submarine)
    diagonal_target.position = (100, 100)
    
    # En ubåt som är närmare i "nedåt"-riktningen
    closer_down_target = Mock(spec=Submarine)
    closer_down_target.position = (50, 60)
    
    fleet = [
        shooter_sub, 
        up_target, 
        down_target, 
        forward_target, 
        diagonal_target, 
        closer_down_target
    ]
    
    return fleet, shooter_sub

# Testfunktioner för Pytest 

def test_check_for_friendly_fire_all_directions(torpedo_system, mock_submarines):
    """
    Testar att generatorn check_for_friendly_fire hittar det närmaste målet
    i varje relevant riktning.
    """
    fleet, shooter_sub = mock_submarines
    
    # Kör generatorn och konverterar utdatan till en lista för enklare verifiering
    results = list(torpedo_system.check_for_friendly_fire(fleet, shooter_sub))
    
    # Definierar de förväntade resultaten (Riktning, Säker, Första Målets Position)
    expected_results = [
        ("up", False, (50, 20)),
        ("down", False, (50, 60)), # closer_down_target är närmare än down_target
        ("forward", False, (70, 50)),
    ]
    assert results == expected_results

def test_check_for_friendly_fire_safe_path(torpedo_system):
    """
    Testar att generatorn returnerar "safe" när det inte finns några mål.
    """
    shooter_sub = Mock(spec=Submarine)
    shooter_sub.position = (10, 10)
    
    # Endast skytten finns i flottan
    fleet = [shooter_sub] 
    
    results = list(torpedo_system.check_for_friendly_fire(fleet, shooter_sub))
    
    for direction, safe, first_target in results:
        assert safe is True
        assert first_target is None

def test_get_friendly_fire_report(torpedo_system, mock_submarines):
    """
    Testar att get_friendly_fire_report kompilerar generatorns utdata
    till en korrekt formaterad rapport-dictionary.
    """
    fleet, shooter_sub = mock_submarines
    
    report = torpedo_system.get_friendly_fire_report(fleet, shooter_sub)
    
    expected_report = {
        "up": {"safe": False, "first_target": (50, 20)},
        "down": {"safe": False, "first_target": (50, 60)},
        "forward": {"safe": False, "first_target": (70, 50)}
    }
    
    assert report == expected_report

def test_log_torpedo_launch_safe(torpedo_system, capsys):
    """
    Testar att log_torpedo_launch loggar korrekt när avfyrningsvägen är säker.
    Använder capsys för att fånga utskrifter till konsolen.
    """
    mock_submarine = Mock(spec=Submarine, id="DRONE_1", get_position=lambda: (1, 1))
    
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
    """
    mock_submarine = Mock(spec=Submarine, id="DRONE_1", get_position=lambda: (1, 1))
    
    risky_report = {
        "up": {"safe": True, "first_target": None},
        "down": {"safe": False, "first_target": (1, 10)},
        "forward": {"safe": True, "first_target": None}
    }
    
    torpedo_system.log_torpedo_launch(mock_submarine, risky_report)
    
    captured = capsys.readouterr()
    assert "RISK OF FRIENDLY FIRE" in captured.out
    assert "first target at (1, 10)" in captured.out