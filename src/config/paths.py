import os
import pathlib

BASE_DIR = pathlib.Path(__file__).parent.parent.parent

MOVEMENT_REPORTS_DIR = BASE_DIR / "files" / "MovementReports"
SENSOR_DATA_DIR = BASE_DIR / "files" / "Sensordata"
SECRETS_DIR = BASE_DIR / "files" / "Secrets"
LOG_DIR = BASE_DIR / "files" / "Logs"

def movement_file_path(drone_id: str) -> pathlib.Path:
    """Returnerar sökvägen till en specifik rörelserapport-fil."""
    return MOVEMENT_REPORTS_DIR / f"{drone_id}.txt"

def sensor_file_path(drone_id: str) -> pathlib.Path:
    """Returnerar sökvägen till en specifik sensordata-fil."""
    return SENSOR_DATA_DIR / f"{drone_id}.txt"

def secret_key_file_path() -> pathlib.Path:
    """Returnerar sökvägen till SecretKEY.txt."""
    return SECRETS_DIR / "SecretKEY.txt"

def activation_codes_file_path() -> pathlib.Path:
    """Returnerar sökvägen till ActivationCodes.txt."""
    return SECRETS_DIR / "ActivationCodes.txt"
