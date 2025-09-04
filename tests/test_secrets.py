import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.data.secrets_loader import SecretsLoader
from tests.test_path import get_random_drone_id

def test_loader():
    """
    Testar att SecretsLoader-klassen kan ladda hemligheterna korrekt.
    """
    print("--- TESTAR SECRETSLOADER ---")
    secrets_loader = SecretsLoader()
    test_drone_id = get_random_drone_id()

    # Den här raden testar att load_secrets() fungerar
    if not secrets_loader.load_secrets():
        print("Test misslyckades: Kunde inte ladda hemligheterna.")
        sys.exit(1)
    
    # Validera att en specifik nyckel kan hämtas
    test_serial_number = test_drone_id
    key = secrets_loader.get_secret_key(test_serial_number)
    code = secrets_loader.get_activation_code(test_serial_number)

    if key and code:
        print(f"Hittade hemlig nyckel för {test_serial_number}: {key}")
        print(f"Hittade aktiveringskod för {test_serial_number}: {code}")
    else:
        print(f"Test misslyckades: Kunde inte hitta nyckel/kod för {test_serial_number}.")
        sys.exit(1)

if __name__ == "__main__":
    test_loader()