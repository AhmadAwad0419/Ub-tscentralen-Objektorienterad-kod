from src.core.submarine import Submarine
from src.utils.logger import nuke_logger, log_calls


class NukeActivation:
    """Handles nuke activation with safety + secret key checks."""

    def __init__(self, secrets_loader, torpedo_system):
        self.secrets_loader = secrets_loader
        self.torpedo_system = torpedo_system

    @log_calls(nuke_logger, "nuke", context_args=["submarine"])
    def activate_nuke(self, submarine_id: str, submarines: list[Submarine], submarine: Submarine):
        """Försöker aktivera nuke på given ubåt."""

        if not submarine.is_active:
            nuke_logger.error(f"Attempted nuke activation on inactive submarine {submarine.id}")
            return False

        # Kontrollera hemlig nyckel först
        if not self.secrets_loader.is_valid_key(submarine_id):
            nuke_logger.error(f"Invalid secret key for {submarine.id}, activation denied")
            return False

        # Kontrollera friendly fire
        if not self.allowed_to_activate(submarines, submarine):
            nuke_logger.warning(f"Activation blocked (friendly fire risk) for {submarine.id}")
            return False

        # Om vi kommit hit, aktivering godkänd
        nuke_logger.critical(f"Nuke activated for submarine {submarine.id}")
        return True

    def allowed_to_activate(self, submarines: list[Submarine], submarine: Submarine) -> bool:
        """Kollar om nuke kan aktiveras utan friendly fire."""
        report = self.torpedo_system.get_friendly_fire_report(submarines, submarine)
        # Nuke får inte aktiveras om någon riktning har risk
        return all(info["safe"] for info in report.values())
