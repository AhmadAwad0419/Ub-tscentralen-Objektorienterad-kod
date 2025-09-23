import os
from src.utils.logger import secrets_logger, log_calls


class SecretsLoader:
    """Loads and validates secret keys for nukes."""

    def __init__(self, secrets_file="files/Secrets/SecretKEY.txt"):
        self.secrets_file = secrets_file
        self.secrets: set[str] = set()

    @log_calls(secrets_logger, "secrets")
    def load_secrets(self):
        """Laddar hemliga nycklar från fil."""
        if not os.path.exists(self.secrets_file):
            secrets_logger.error(f"Secrets file {self.secrets_file} missing")
            return

        with open(self.secrets_file, "r", encoding="utf-8") as f:
            self.secrets = {line.strip() for line in f if line.strip()}

        secrets_logger.info(f"Loaded {len(self.secrets)} secret keys")

    @log_calls(secrets_logger, "secrets", context_args=["submarine_id"])
    def is_valid_key(self, submarine_id: str) -> bool:
        """Kontrollerar om en ubåts-ID är en giltig nyckel."""
        return submarine_id in self.secrets
