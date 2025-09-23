from src.core.submarine import Submarine
from src.utils.logger import nuke_logger, log_calls
from typing import Optional

class NukeActivation:
    def __init__(self, secrets_loader, torpedo_system):
        self.secrets_loader = secrets_loader
        self.torpedo_system = torpedo_system

    @log_calls(nuke_logger, "nuke", context_args=["submarine_id"])
    def activate_nuke(self, submarine_id: str, submarines: list, submarine, provided_hash: str, for_date: Optional[str] = None):
        """
        Försöker aktivera nuke på given ubåt. 'provided_hash' är hex string som användaren skickar.
        'for_date' kan användas i tester för att ange ett annat datum (YYYY-MM-DD).
        """

        if not submarine.is_active:
            nuke_logger.error(f"Attempted nuke activation on inactive submarine {submarine.id}")
            return False
        
        if not self.secrets_loader.is_valid_key(submarine_id):
            nuke_logger.error(f"Invalid secret key for {submarine.id}, activation denied")
            return False

        # Kontrollera att KEY/activation code finns och verifiera den inkomna hashen
        if not self.secrets_loader.verify_activation(submarine_id, provided_hash, for_date=for_date):
            nuke_logger.error(f"Nuke activation failed verification for submarine {submarine.id}")
            return False

        # Kontrollera friendly fire
        if not self.allowed_to_activate(submarines, submarine):
            nuke_logger.warning(f"Activation blocked (friendly fire risk) for {submarine.id}")
            return False

        # Om vi kommer hit: aktivera nukes (logga och returnera True)
        nuke_logger.critical(f"Nuke ACTIVATED for submarine {submarine.id} at {submarine.position}")
        return True

    def allowed_to_activate(self, submarines: list, submarine) -> bool:
        """
        Kontrollera om en nuke kan aktiveras för given ubåt.
        Blockerar om det finns andra aktiva ubåtar för nära (friendly fire).
        """
        SAFE_DISTANCE = 5  # exempel: Manhattan-avstånd < 5 blockeras

        for other in submarines:
            if other.id == submarine.id or not other.is_active:
                continue

            # Manhattan-avstånd mellan ubåtarna
            dist = abs(other.position[0] - submarine.position[0]) + abs(other.position[1] - submarine.position[1])

            if dist < SAFE_DISTANCE:
                nuke_logger.warning(
                    f"NUKE activation blocked for {submarine.id}: "
                    f"friendly sub {other.id} too close at distance {dist}"
                )
                return False

        nuke_logger.info(f"NUKE activation allowed for {submarine.id} at {submarine.position}")
        return True