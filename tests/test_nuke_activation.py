import sys
import os
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.nuke_activation import NukeActivation
from src.data.secrets_loader import SecretsLoader

def nuke_tester():
    """
    Testar NukeActivation-klassen för att se att nukes kan aktiveras med rätt serienummer.
    """
    print("--- TESTAR NUKEACTIVATOR-SKRIPTET ---")
    secrets_loader = SecretsLoader()
    
    # Försök ladda hemligheterna, annars avsluta
    if not secrets_loader.load_secrets():
        print("Kunde inte ladda hemligheter. Kan inte fortsätta testet.")
        return

    nuke_activator = NukeActivation(secrets_loader)

    # Test med giltigt och ogiltigt serienummer
    valid_serial_number = '39200767-28'
    invalid_serial_number = '12345678-90'

    # --- Test 1: Giltigt serienummer ---
    print(f"\nTestar med giltigt serienummer: {valid_serial_number}")
    is_activated = nuke_activator.activate_nuke(valid_serial_number)
    print(f"Resultat: Nuke aktiverad: {is_activated}")
    
    if is_activated:
        print("Test 1 lyckades: Nuke aktiverades med ett giltigt serienummer.")
    else:
        print("Test 1 misslyckades: Nuke aktiverades inte med ett giltigt serienummer.")

    # --- Test 2: Ogiltigt serienummer ---
    print(f"\nTestar med ogiltigt serienummer: {invalid_serial_number}")
    is_activated = nuke_activator.activate_nuke(invalid_serial_number)
    print(f"Resultat: Nuke aktiverad: {is_activated}")

    if not is_activated:
        print("Test 2 lyckades: Nuke aktiverades inte med ett ogiltigt serienummer.")
    else:
        print("Test 2 misslyckades: Nuke aktiverades med ett ogiltigt serienummer.")

if __name__ == "__main__":
    nuke_tester()