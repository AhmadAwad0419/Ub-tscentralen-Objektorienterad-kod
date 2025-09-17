import pytest
import os
import sys
import tempfile

# Lägg till projektets rotkatalog till Python-sökvägen
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data.secrets_loader import SecretsLoader

# Pytest fixtures

@pytest.fixture
def secrets_loader():
    """
    Fixture som skapar en instans av SecretsLoader för varje test.
    """
    return SecretsLoader()

@pytest.fixture
def setup_secret_files(monkeypatch):
    """
    Fixture som skapar temporära filer och använder monkeypatch
    för att omdirigera filvägarna i SecretsLoader till dem.
    Detta isolerar testerna från den verkliga filstrukturen.
    """
    temp_dir = tempfile.TemporaryDirectory()
    secrets_path = os.path.join(temp_dir.name, "Secrets")
    os.makedirs(secrets_path, exist_ok=True)

    # Skapa temporära filer med känt innehåll
    secret_key_content = """DRONE_1:KEY_A
DRONE_2:KEY_B"""
    secret_key_path = os.path.join(secrets_path, "SecretKEY.txt")
    with open(secret_key_path, "w", encoding='utf-8') as f:
        f.write(secret_key_content)

    activation_code_content = """DRONE_1:CODE_A
DRONE_2:CODE_B"""
    activation_code_path = os.path.join(secrets_path, "ActivationCodes.txt")
    with open(activation_code_path, "w", encoding='utf-8') as f:
        f.write(activation_code_content)
    
    # Monkeypatchar de funktioner i SecretsLoader som returnerar sökvägar
    monkeypatch.setattr("src.data.secrets_loader.secret_key_file_path", lambda: secret_key_path)
    monkeypatch.setattr("src.data.secrets_loader.activation_codes_file_path", lambda: activation_code_path)

    yield {
        "secret_key_path": secret_key_path,
        "activation_code_path": activation_code_path
    }
    
    temp_dir.cleanup()

# Testfunktioner för Pytest 

def test_load_secrets_success(secrets_loader, setup_secret_files):
    """
    Testar att load_secrets() kan ladda filer korrekt och ställa in
    is_loaded till True.
    """
    assert secrets_loader.load_secrets() is True
    assert secrets_loader.is_loaded is True
    assert secrets_loader.secret_keys == {"DRONE_1": "KEY_A", "DRONE_2": "KEY_B"}
    assert secrets_loader.activation_codes == {"DRONE_1": "CODE_A", "DRONE_2": "CODE_B"}

def test_load_secrets_file_not_found(secrets_loader, monkeypatch):
    """
    Testar att load_secrets() hanterar ett FileNotFoundError.
    """
    # Använd monkeypatch för att simulera en icke-existerande fil
    monkeypatch.setattr("src.data.secrets_loader.secret_key_file_path", lambda: "/non/existent/path/file.txt")
    
    assert secrets_loader.load_secrets() is False
    assert secrets_loader.is_loaded is False

def test_get_secret_key(secrets_loader, setup_secret_files):
    """
    Testar att get_secret_key() returnerar rätt värde.
    """
    # Loader laddas automatiskt när metoden anropas för första gången
    assert secrets_loader.get_secret_key("DRONE_1") == "KEY_A"
    assert secrets_loader.get_secret_key("DRONE_2") == "KEY_B"
    assert secrets_loader.get_secret_key("NON_EXISTENT") is None

def test_get_activation_code(secrets_loader, setup_secret_files):
    """
    Testar att get_activation_code() returnerar rätt värde.
    """
    assert secrets_loader.get_activation_code("DRONE_1") == "CODE_A"
    assert secrets_loader.get_activation_code("DRONE_2") == "CODE_B"
    assert secrets_loader.get_activation_code("NON_EXISTENT") is None

def test_idempotent_load(secrets_loader, setup_secret_files):
    """
    Testar att load_secrets() returnerar True och inte laddar om
    om det redan har anropats.
    """
    assert secrets_loader.load_secrets() is True
    assert secrets_loader.load_secrets() is True
    # Innehållet ska vara oförändrat efter det andra anropet
    assert secrets_loader.secret_keys == {"DRONE_1": "KEY_A", "DRONE_2": "KEY_B"}