import os

import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

MOVEMENT_REPORTS_DIR = os.path.join(BASE_DIR, "files", "MovementReports")
SENSOR_DATA_DIR = os.path.join(BASE_DIR, "files", "SensorData")
SECRETS_DIR = os.path.join(BASE_DIR, "files", "Secrets")

def movement_file_path(drone_id: str) -> str:
    return os.path.join(MOVEMENT_REPORTS_DIR, f"{drone_id}.txt")

def sensor_file_path(drone_id: str) -> str:
    return os.path.join(SENSOR_DATA_DIR, f"{drone_id}.txt")

def secret_key_file() -> str:
    return os.path.join(SECRETS_DIR, "SecretKEY.txt")
