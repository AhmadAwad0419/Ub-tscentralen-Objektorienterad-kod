from datetime import datetime
import hashlib
from typing import List, Dict, Any, Optional
from src.data.secrets_loader import SecretsLoader
from src.core.torpedo_system import TorpedoSystem
from src.core.submarine import Submarine
from src.utils.logger import nuke_logger

class NukeActivation:
    """
    Klass för att hantera aktiveringen av torpeder baserat på
    korrekta hemliga nycklar, aktiveringskoder och friendly fire-kontroller.
    """
    def __init__(self, secrets_loader: SecretsLoader, torpedo_system: TorpedoSystem):
        self.secrets_loader: SecretsLoader = secrets_loader
        self.torpedo_system: TorpedoSystem = torpedo_system
        self.secrets_loader = secrets_loader
        self.torpedo_system = torpedo_system

    def allowed_to_activate(self, submarines: List[Submarine], submarine_to_check: Submarine) -> bool:
        """
        Kontrollerar om aktivering är tillåten baserat på
        en friendly fire-analys.
        """
        # Hämta rapporten från TorpedoSystem
        friendly_fire_report: Dict[str, Dict[str, Any]] = self.torpedo_system.get_friendly_fire_report(submarines, submarine_to_check)

        # Analysera rapporten för att se om någon riktning är osäker
        is_safe: bool = True
        for direction, info in friendly_fire_report.items():
            if info.get("safe") is False:
                nuke_logger.nuke_activation(f"Friendly fire-risk upptäcktes i {direction}-riktningen.", level="WARNING")
                is_safe = False
                break

        self.torpedo_system.log_torpedo_launch(submarine_to_check, friendly_fire_report)
        if is_safe:
            nuke_logger.nuke_activation("Ingen friendly fire-risk upptäcktes.", level="INFO")
        return is_safe

    def activate_nuke(self, serial: str, submarines: List[Submarine], submarine_to_check: Submarine) -> bool:
        """
        Försöker aktivera kärnvapnet för en given ubåt, med
        kontroll av både hemliga nycklar och friendly fire.
        """
        # Kontrollera om avfyrning är tillåten
        if not self.allowed_to_activate(submarines, submarine_to_check):
            return False

        # Verifiera hemliga nycklar och koder
        secret_key: Optional[str] = self.secrets_loader.get_secret_key(serial)
        activation_code: Optional[str] = self.secrets_loader.get_activation_code(serial)
        
        if not (secret_key and activation_code):
            nuke_logger.nuke_activation(f"Kunde inte hitta hemligheter för ubåt {serial}.", level="ERROR")
            return False

        today_date: str = datetime.now().strftime("%Y-%m-%d")

        combined_string: str = f"{today_date}{secret_key}{activation_code}"
        
        hash_object = hashlib.sha256(combined_string.encode('utf-8'))
        calculated_hash: str = hash_object.hexdigest()

        nuke_logger.nuke_activation(
            f"Nukeaktivering godkänd för ubåt {serial}\n"
            f"Använder hemlig nyckel: {secret_key}\n"
            f"Använder aktiveringskod: {activation_code}\n"
            f"Kombinerad sträng: {combined_string}\n"
            f"Beräknad hash: {calculated_hash}\n"
            f"Verifiering lyckades: Nuke avfyras!\n",
            level="CRITICAL"
            )        
        return True
