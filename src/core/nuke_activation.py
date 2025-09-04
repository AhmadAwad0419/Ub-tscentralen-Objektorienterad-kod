from datetime import datetime
import hashlib
from src.data.secrets_loader import SecretsLoader

class NukeActivation:
    """
    Klass för att hantera aktiveringen av torpeder baserat på
    korrekta hemliga nycklar och aktiveringskoder.
    """
    def __init__(self, secrets_loader: SecretsLoader):
        self.secrets_loader = secrets_loader

    # Får också bara aktiveras om det inte finns risk för friendly fire. 
    # Implementeras när torpedo_system är fixat

    def activate_nuke(self, serial: str) -> bool:
        secret_key = self.secrets_loader.get_secret_key(serial)
        activation_code = self.secrets_loader.get_activation_code(serial)
        
        if not (secret_key and activation_code):
            print(f"Fel: Kunde inte hitta hemligheter för ubåt {serial}.")
            return False

        today_date = datetime.now().strftime("%Y-%m-%d")

        combined_string = f"{today_date}{secret_key}{activation_code}"
        
        hash_object = hashlib.sha256(combined_string.encode('utf-8'))
        calculated_hash = hash_object.hexdigest()

        print(f"Nukeaktivering godkänd för ubåt {serial}")
        print(f"Använder hemlig nyckel: {secret_key}")
        print(f"Använder aktiveringskod: {activation_code}")
        print(f"Kombinerad sträng: {combined_string}")
        print(f"Beräknad hash: {calculated_hash}")
        
        # Måste ändras till rätt datum för test. Datum för denna hash: 2025-09-01
        expected_hash = "35962cf4c529a44e22fe04f0532086410742979a98e9fd8a8abacc91cef4613f"
        
        if calculated_hash == expected_hash:
            print("Verifiering lyckades: Hashen matchar!")
            return True
        else:
            print("Verifiering misslyckades: Hashen matchar inte.")
            return False

if __name__ == '__main__':
    secrets_loader = SecretsLoader()

    if not secrets_loader.load_secrets():
        print("Kunde inte ladda hemligheter. Avslutar.")
    else:
        nuke_activator = NukeActivation(secrets_loader)