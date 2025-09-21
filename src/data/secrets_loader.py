import os
from typing import Dict, Generator, Tuple
from src.config.paths import secret_key_file_path, activation_codes_file_path
from src.utils.logger import secrets_logger, log_calls

class SecretsLoader:
    """
    Klass för att säkert ladda in hemliga nycklar och aktiveringskoder
    från textfiler.
    """

    def __init__(self):
        self.secret_keys: Dict[str, str] = {}
        self.activation_codes: Dict[str, str] = {}
        self.is_loaded = False

    def load_file_row(self, file_path: str) -> Generator[Tuple[str, str], None, None]:
        """
        Generator för att läsa en fil rad för rad.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Filen kunde inte hittas: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(":")
                    if len(parts) == 2:
                        serial_number = parts[0].strip()
                        value = parts[1].strip()
                        yield serial_number, value
                    else:
                        secrets_logger.secret_loader(f"Ogiltigt format på rad i filen: {file_path}", level="WARNING")

    @log_calls
    def load_secrets(self) -> bool:
        """
        Läser in både SecretKEY.txt och ActivationCodes.txt.
        Returnerar True vid lyckad inläsning, annars False.
        """
        if self.is_loaded:
            return True

        try:
            key_file_path = secret_key_file_path()
            code_file_path = activation_codes_file_path()

            for serial, key in self.load_file_row(key_file_path):
                self.secret_keys[serial] = key

            for serial, code in self.load_file_row(code_file_path):
                self.activation_codes[serial] = code
            
            self.is_loaded = True
            return True

        except FileNotFoundError as e:
            secrets_logger.secret_loader(f"Fil hittades inte: {e}", level="ERROR")
            return False
        except Exception as e:
            secrets_logger.secret_loader(f"Ett oväntat fel uppstod vid inläsning av hemligheter: {e}", level="EXCEPTION")
            return False

    @log_calls
    def get_secret_key(self, serial_number: str) -> str | None:
        """
        Hämtar en hemlig nyckel baserat på ubåtens serienummer.
        Returnerar nyckeln eller None om den inte hittas.
        """
        if not self.is_loaded:
            self.load_secrets()
            
        return self.secret_keys.get(serial_number)

    @log_calls
    def get_activation_code(self, serial_number: str) -> str | None:
        """
        Hämtar en aktiveringskod baserat på ubåtens serienummer.
        Returnerar koden eller None om den inte hittas.
        """
        if not self.is_loaded:
            self.load_secrets()
            
        return self.activation_codes.get(serial_number)

if __name__ == '__main__':
    loader = SecretsLoader()