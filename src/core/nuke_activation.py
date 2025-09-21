from datetime import datetime
import hashlib
from typing import List, Dict, Any, Optional
from src.data.secrets_loader import SecretsLoader
from src.core.torpedo_system import TorpedoSystem
from src.core.submarine import Submarine
from src.utils.logger import nuke_logger, log_calls

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

    def allowed_to_activate(self, submarines, submarine_to_check):
        """
        Kontrollerar om aktivering är tillåten baserat på friendly fire-analys.
        """
        # Hämta rapporten från TorpedoSystem
        friendly_fire_report = self.torpedo_system.get_friendly_fire_report(submarines, submarine_to_check)
        
        # Analysera rapporten för att se om någon riktning är osäker
        self.torpedo_system.log_torpedo_launch(submarine_to_check, friendly_fire_report)
        for direction, info in friendly_fire_report.items():
            if info.get("safe") is False:
                
                return False
        
        return True

    @log_calls(nuke_logger, "movement_files", context_args=["submarines", "submarine_to_check"])
    def activate_nuke(self, serial: str, submarines: List[Submarine], submarine_to_check: Submarine) -> bool:
        """
        Försöker aktivera kärnvapnet för en given ubåt, med
        kontroll av både hemliga nycklar och friendly fire.
        """
        # Kontrollera om avfyrning är tillåten baserat på friendly fire
        if not self.allowed_to_activate(submarines, submarine_to_check):
            return False

        # Verifiera hemliga nycklar och koder
        secret_key: Optional[str] = self.secrets_loader.get_secret_key(serial)
        activation_code: Optional[str] = self.secrets_loader.get_activation_code(serial)
        
        if not (secret_key and activation_code):
            
            return False

        today_date: str = datetime.now().strftime("%Y-%m-%d")

        combined_string: str = f"{today_date}{secret_key}{activation_code}"
        
        hash_object = hashlib.sha256(combined_string.encode('utf-8'))
        calculated_hash: str = hash_object.hexdigest()
        calculated_hash
    
        return True