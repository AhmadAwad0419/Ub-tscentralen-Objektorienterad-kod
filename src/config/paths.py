import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

MOVEMENT_REPORTS_DIR = os.path.join(BASE_DIR, "MovementReports")
SENSOR_DATA_DIR = os.path.join(BASE_DIR, "SensorData")
SECRETS_DIR = os.path.join(BASE_DIR, "Secrets")

def movement_file_path(drone_id: str) -> str:
    """Returnerar sökvägen till en specifik rörelserapport-fil."""
    return os.path.join(MOVEMENT_REPORTS_DIR, f"{drone_id}.txt")

def sensor_file_path(drone_id: str) -> str:
    """Returnerar sökvägen till en specifik sensordata-fil."""
    return os.path.join(SENSOR_DATA_DIR, f"{drone_id}.txt")

def secret_key_file_path() -> str:
    """Returnerar sökvägen till SecretKEY.txt."""
    return os.path.join(SECRETS_DIR, "SecretKEY.txt")
    
def activation_codes_file_path() -> str:
    """Returnerar sökvägen till ActivationCodes.txt."""
    return os.path.join(SECRETS_DIR, "ActivationCodes.txt")