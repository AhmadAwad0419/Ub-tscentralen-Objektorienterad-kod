import os
import hmac
import hashlib
from datetime import date
from typing import Dict, Optional
from src.utils.logger import secrets_logger, log_calls

class SecretsLoader:
    def __init__(
        self,
        secrets_file: str = "files/Secrets/SecretKEY.txt",
        activation_file: str = "files/Secrets/ActivationCodes.txt",
    ):
        self.secrets_file = secrets_file
        self.activation_file = activation_file
        # maps: submarine_id -> KEY
        self.keys: Dict[str, str] = {}
        # maps: submarine_id -> activation_code
        self.activation_codes: Dict[str, str] = {}

    @log_calls(secrets_logger, "secrets")
    def load_secrets(self):
        # load keys
        if os.path.exists(self.secrets_file):
            with open(self.secrets_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or ":" not in line:
                        continue
                    sid, key = [p.strip() for p in line.split(":", 1)]
                    self.keys[sid] = key
        else:
            secrets_logger.error(f"Secrets file {self.secrets_file} missing")

        # load activation codes
        if os.path.exists(self.activation_file):
            with open(self.activation_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or ":" not in line:
                        continue
                    sid, code = [p.strip() for p in line.split(":", 1)]
                    self.activation_codes[sid] = code
        else:
            secrets_logger.error(f"Activation file {self.activation_file} missing")

        secrets_logger.info(f"Loaded {len(self.keys)} keys and {len(self.activation_codes)} activation codes")

    @log_calls(secrets_logger, "secrets", context_args=["submarine_id"])
    def is_valid_key(self, submarine_id: str) -> bool:
        return submarine_id in self.keys

    def expected_activation_hash(self, submarine_id: str, for_date: Optional[str] = None) -> Optional[str]:
        """
        Beräkna förväntad aktiverings-hash: SHA256( date + KEY + activation_code ).
        date ska vara YYYY-MM-DD. Returnerar hex string eller None om inte konfigurerad.
        """
        if submarine_id not in self.keys or submarine_id not in self.activation_codes:
            return None

        if for_date is None:
            for_date = date.today().isoformat()

        key = self.keys[submarine_id]
        code = self.activation_codes[submarine_id]
        input_str = f"{for_date}{key}{code}"
        digest = hashlib.sha256(input_str.encode("utf-8")).hexdigest()
        return digest

    def verify_activation(self, submarine_id: str, provided_hash: str, for_date: Optional[str] = None) -> bool:
        """
        Jämför provided_hash med beräknad hash i ett timing-safe sätt.
        """
        expected = self.expected_activation_hash(submarine_id, for_date=for_date)
        if expected is None:
            return False
        # använd constant-time compare
        return hmac.compare_digest(expected, provided_hash)
