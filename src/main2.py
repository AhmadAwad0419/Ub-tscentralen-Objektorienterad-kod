# src/main.py
import os, sys

# Lägger till projektets rotkatalog till Python-sökvägen för att kunna importera moduler
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.config.paths import MOVEMENT_REPORTS_DIR
from src.data.secrets_loader import SecretsLoader
from src.core.submarine import Submarine
from src.data.file_reader import FileReader
from src.core.movement_manager import MovementManager

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        from src.gui.gui2 import main as gui_main
        gui_main()
        return

    print("Startar Ubåtscentralen...")

    secrets = SecretsLoader()
    if not secrets.load_secrets():
        print("Kunde inte ladda hemligheter. Avslutar.")
        sys.exit(1)

    drone_ids = [
        f.replace(".txt", "")
        for f in os.listdir(MOVEMENT_REPORTS_DIR)
        if f.endswith(".txt")
    ]
    subs = [Submarine(id) for id in drone_ids]

    reader = FileReader()
    manager = MovementManager(reader, tick_delay=1.0)
    manager.load_submarines(subs)
    manager.run()

if __name__ == "__main__":
    main()
