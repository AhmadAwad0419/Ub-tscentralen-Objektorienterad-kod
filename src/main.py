# src/main.py
import sys, os, asyncio

# --- Ensure project root is in sys.path ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.config.paths import MOVEMENT_REPORTS_DIR
from src.data.secrets_loader import SecretsLoader


def parse_speed_arg(default: float = 1.0) -> float:
    """Parse --speed <float> from command line."""
    if "--speed" in sys.argv:
        try:
            idx = sys.argv.index("--speed")
            return float(sys.argv[idx + 1])
        except (ValueError, IndexError):
            print("Felaktigt värde för --speed, använder standardvärde.")
    return default


def run_sync(tick_delay: float):
    from src.core.submarine import Submarine
    from src.data.file_reader import FileReader
    from src.core.movement_manager import MovementManager

    drone_ids = [
        f.replace(".txt", "")
        for f in os.listdir(MOVEMENT_REPORTS_DIR)
        if f.endswith(".txt")
    ]
    subs = [Submarine(id) for id in drone_ids]

    reader = FileReader()
    manager = MovementManager(reader, tick_delay=tick_delay)
    manager.load_submarines_from_generator(subs)
    manager.run()


async def run_async(tick_delay: float):
    from src.core.submarine_async import Submarine
    from src.data.file_reader_async import AsyncFileReader
    from src.core.movement_manager_async import AsyncMovementManager

    drone_ids = [
        f.replace(".txt", "")
        for f in os.listdir(MOVEMENT_REPORTS_DIR)
        if f.endswith(".txt")
    ]
    subs = [Submarine(id) for id in drone_ids]

    reader = AsyncFileReader()
    manager = AsyncMovementManager(reader, tick_delay=tick_delay)
    await manager.load_submarines(subs)
    await manager.run()


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        from src.gui.gui2 import main as gui_main
        gui_main()
        return

    # Load secrets (shared)
    secrets = SecretsLoader()
    if not secrets.load_secrets():
        print("Kunde inte ladda hemligheter. Avslutar.")
        sys.exit(1)

    # Parse optional speed
    tick_delay = parse_speed_arg(default=1.0)
    print(f"Tick delay: {tick_delay} sekunder")

    # Choose mode
    if "--sync" in sys.argv:
        print("Kör i SYNKRONT läge")
        run_sync(tick_delay)
    else:
        print("Kör i ASYNKRONT läge")
        asyncio.run(run_async(tick_delay))


if __name__ == "__main__":
    main()
