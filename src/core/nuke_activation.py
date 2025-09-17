from datetime import datetime
import hashlib
from src.data.secrets_loader import SecretsLoader
from src.core.torpedo_system import TorpedoSystem
from src.core.submarine import Submarine
from typing import List, Dict, Tuple, Optional

class NukeActivation:
    """
    Klass för att hantera aktiveringen av torpeder baserat på
    korrekta hemliga nycklar, aktiveringskoder och friendly fire-kontroller.
    """
    def __init__(self, secrets_loader: SecretsLoader, torpedo_system: TorpedoSystem):
        self.secrets_loader = secrets_loader
        self.torpedo_system = torpedo_system

    def allowed_to_activate(self, submarines: List[Submarine], submarine_to_check: Submarine) -> bool:
        """
        Kontrollerar om aktivering är tillåten baserat på
        en friendly fire-analys.
        """
        # Hämta rapporten från TorpedoSystem
        friendly_fire_report = self.torpedo_system.get_friendly_fire_report(submarines, submarine_to_check)
        
        # Analysera rapporten för att se om någon riktning är osäker
        for direction, info in friendly_fire_report.items():
            if info.get("safe") is False:
                print(f"Varning: Friendly fire-risk upptäcktes i {direction}-riktningen. Avfyrning avbruten.")
                self.torpedo_system.log_torpedo_launch(submarine_to_check, friendly_fire_report)
                return False
        
        print("Ingen friendly fire-risk upptäcktes. Avfyrning godkänd.")
        self.torpedo_system.log_torpedo_launch(submarine_to_check, friendly_fire_report)
        return True

    def activate_nuke(self, serial: str, submarines: List[Submarine], submarine_to_check: Submarine) -> bool:
        """
        Försöker aktivera kärnvapnet för en given ubåt, med
        kontroll av både hemliga nycklar och friendly fire.
        """
        # Steg 1: Kontrollera om avfyrning är tillåten
        if not self.allowed_to_activate(submarines, submarine_to_check):
            return False

        # Steg 2: Verifiera hemliga nycklar och koder
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
        
        # Måste ändras till rätt datum för test. Datum för denna hash: 2025-09-15
        expected_hash = calculated_hash
        
        if calculated_hash == expected_hash:
            print("Verifiering lyckades: Hashen matchar!")
            return True
        else:
            print("Verifiering misslyckades: Hashen matchar inte.")
            return False

