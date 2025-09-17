import os
import sys
from datetime import datetime
import pytest
from unittest.mock import Mock

# Lägger till projektets rotkatalog till Python-sökvägen för att kunna importera moduler
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.nuke_activation import NukeActivation
from src.data.secrets_loader import SecretsLoader
from src.core.torpedo_system import TorpedoSystem
from src.core.submarine import Submarine

# Pytest fixtures

@pytest.fixture
def mock_secrets_loader(monkeypatch):
    """
    Mockar SecretsLoader för att ge förutsägbara nycklar och koder.
    """
    loader_mock = Mock(spec=SecretsLoader)
    loader_mock.get_secret_key.side_effect = lambda serial: "SECRET_KEY_A" if serial == "DRONE_1" else None
    loader_mock.get_activation_code.side_effect = lambda serial: "ACTIVATION_CODE_A" if serial == "DRONE_1" else None
    return loader_mock

@pytest.fixture
def mock_torpedo_system():
    """
    Mockar TorpedoSystem. Metoden get_friendly_fire_report() mockas individuellt
    i varje testfall för att simulera olika scenarier.
    """
    return Mock(spec=TorpedoSystem)

@pytest.fixture
def mock_submarine_squadron():
    """
    Skapar mock-objekt för ubåtar för att simulera en drönarna.
    """
    mock_shooter = Mock(spec=Submarine)
    mock_shooter.id = "DRONE_1"
    mock_shooter.get_position.return_value = (10, 10)

    mock_target = Mock(spec=Submarine)
    mock_target.id = "DRONE_2"
    # Samma kolumn, simulerar friendly fire-risk
    mock_target.get_position.return_value = (10, 20) 

    return [mock_shooter, mock_target], mock_shooter, mock_target

@pytest.fixture
def nuke_activation_instance(mock_secrets_loader, mock_torpedo_system):
    """
    Skapar en instans av NukeActivation med mockade beroenden.
    """
    return NukeActivation(mock_secrets_loader, mock_torpedo_system)

# Testfunktioner för Pytest

def test_activate_nuke_no_friendly_fire(nuke_activation_instance, mock_torpedo_system, monkeypatch):
    """
    Testar att en nuke kan aktiveras när det inte finns någon risk för friendly fire.
    """
    # Mocka get_friendly_fire_report att returnera en säker rapport
    safe_report = {
        "up": {"safe": True, "first_target": None},
        "down": {"safe": True, "first_target": None},
        "forward": {"safe": True, "first_target": None}
    }
    mock_torpedo_system.get_friendly_fire_report.return_value = safe_report
    
    # Mocka datetime.now för att simulera ett specifikt datum för hash-verifieringen
    monkeypatch.setattr("src.core.nuke_activation.datetime", Mock(now=lambda: datetime(2025, 9, 15)))
    
    # Skapa dummy-data för att skicka till activate_nuke
    mock_submarine = Mock(spec=Submarine, id="DRONE_1")
    
    result = nuke_activation_instance.activate_nuke(
        serial="DRONE_1", 
        submarines=[mock_submarine], 
        submarine_to_check=mock_submarine
    )
    
    assert result is True
    mock_torpedo_system.get_friendly_fire_report.assert_called_once()


def test_activate_nuke_with_friendly_fire_risk(nuke_activation_instance, mock_torpedo_system, mock_submarine_squadron):
    """
    Testar att nuke-aktivering avbryts när friendly fire-risk finns.
    """
    submarines, shooter, target = mock_submarine_squadron

    # Mocka get_friendly_fire_report att returnera en rapport med risk
    risky_report = {
        "up": {"safe": True, "first_target": None},
        "down": {"safe": False, "first_target": target.get_position()},
        "forward": {"safe": True, "first_target": None}
    }
    mock_torpedo_system.get_friendly_fire_report.return_value = risky_report
    
    result = nuke_activation_instance.activate_nuke(
        serial=shooter.id, 
        submarines=submarines, 
        submarine_to_check=shooter
    )
    
    assert result is False
    mock_torpedo_system.get_friendly_fire_report.assert_called_once()


def test_activate_nuke_invalid_serial(nuke_activation_instance, mock_torpedo_system):
    """
    Testar att aktivering misslyckas med ett ogiltigt serienummer.
    """
    # Mocka get_friendly_fire_report att returnera en säker rapport
    safe_report = {
        "up": {"safe": True, "first_target": None},
        "down": {"safe": True, "first_target": None},
        "forward": {"safe": True, "first_target": None}
    }
    mock_torpedo_system.get_friendly_fire_report.return_value = safe_report
    
    # Använd ett ogiltigt serienummer
    mock_submarine = Mock(spec=Submarine, id="INVALID_DRONE")
    
    result = nuke_activation_instance.activate_nuke(
        serial="INVALID_DRONE", 
        submarines=[mock_submarine], 
        submarine_to_check=mock_submarine
    )
    
    assert result is False
    # Kontrollera att friendly fire-kontrollen kördes, men att det sedan misslyckades på grund av nyckeln
    mock_torpedo_system.get_friendly_fire_report.assert_called_once()