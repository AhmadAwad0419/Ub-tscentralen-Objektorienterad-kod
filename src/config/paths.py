import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

MOVEMENT_REPORTS_DIR = os.path.join(BASE_DIR, "MovementReports")
SENSOR_DATA_DIR = os.path.join(BASE_DIR, "SensorData")
SECRETS_DIR = os.path.join(BASE_DIR, "Secrets")

def movement_file_path(drone_id: str) -> str:
    return os.path.join(MOVEMENT_REPORTS_DIR, f"{drone_id}.txt")

def sensor_file_path(drone_id: str) -> str:
    return os.path.join(SENSOR_DATA_DIR, f"{drone_id}.txt")

def secret_key_file_path() -> str:
    return os.path.join(SECRETS_DIR, "SecretKEY.txt")
    
def activation_codes_file_path() -> str:
    return os.path.join(SECRETS_DIR, "ActivationCodes.txt")

# Kanske kan byta ut "os" mot "pathlib". Verkar vara lättare och "renare" att jobba med.

# import pathlib

# BASE_DIR = pathlib.Path(__file__).parent.parent.parent

# MOVEMENT_REPORTS_DIR = BASE_DIR / "files" / "MovementReports"
# SENSOR_DATA_DIR = BASE_DIR / "files" / "SensorData"
# SECRETS_DIR = BASE_DIR / "files" / "Secrets"

# def movement_file_path(drone_id: str) -> pathlib.Path:
#     """Returnerar sökvägen till en specifik rörelserapport-fil."""
#     return MOVEMENT_REPORTS_DIR / f"{drone_id}.txt"

# def sensor_file_path(drone_id: str) -> pathlib.Path:
#     """Returnerar sökvägen till en specifik sensordata-fil."""
#     return SENSOR_DATA_DIR / f"{drone_id}.txt"

# def secret_key_file_path() -> pathlib.Path:
#     """Returnerar sökvägen till SecretKEY.txt."""
#     return SECRETS_DIR / "SecretKEY.txt"

# def activation_codes_file_path() -> pathlib.Path:
#     """Returnerar sökvägen till ActivationCodes.txt."""
#     return SECRETS_DIR / "ActivationCodes.txt"
