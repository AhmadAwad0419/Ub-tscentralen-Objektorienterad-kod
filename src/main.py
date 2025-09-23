# src/main.py
import sys, os, asyncio

# --- Ensure project root is in sys.path ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.config.paths import MOVEMENT_REPORTS_DIR
from src.data.secrets_loader import SecretsLoader
from src.core.nuke_activation import NukeActivation
from src.core.sensor_manager import SensorManager
from src.core.torpedo_system import TorpedoSystem


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
    remaining_subs = list(manager.submarines.values())
    post_run_analysis(remaining_subs)
    show_menu(remaining_subs)


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

def post_run_analysis(subs):
    print("\n=== Alla ubåtar har nått sina slutpositioner ===\n")

    # --- Sensoranalys ---
    sensor_manager = SensorManager()
    for sub in subs:
        output_path = f"logs/sensor_analysis_{sub.id}.txt"
        sensor_manager.process_sensor_by_serial(
            serial_number=sub.id,
            data_folder="files/Sensordata",
            output_path=output_path
        )
        print(f"Sensoranalys sparad för {sub.id} → {output_path}")

    # --- Torped-check ---
    torpedo_system = TorpedoSystem()
    for sub in subs:
        report = torpedo_system.get_friendly_fire_report(subs, sub)
        torpedo_system.log_torpedo_launch(sub, report)

    # --- Nuke-aktiveringsexempel ---
    from src.data.secrets_loader import SecretsLoader
    secrets = SecretsLoader()
    secrets.load_secrets()

    nuke = NukeActivation(secrets_loader=secrets, torpedo_system=torpedo_system)

    # Här kan man aktivera för en specifik ubåt (exempel första)
    if subs:
        target = subs[0]
        nuke.activate_nuke(target.id, subs, target)


def show_menu(subs):
    sensor_manager = SensorManager()
    torpedo_system = TorpedoSystem()
    secrets = SecretsLoader()
    secrets.load_secrets()
    nuke = NukeActivation(secrets_loader=secrets, torpedo_system=torpedo_system)

    while True:
        print("\n=== Kontrollcentral ===")
        print("Tillgängliga ubåtar:")
        for sub in subs:
            print(f" - {sub.id} vid position {sub.position}")
        print("\nAlternativ:")
        print("1. Analysera sensordata för en ubåt")
        print("2. Kontrollera friendly fire för alla ubåtar")
        print("3. Aktivera nuke på en ubåt")
        print("4. Avsluta")
        choice = input("Val: ").strip()

        if choice == "1":
            serial = input("Ange ubåtens serienummer (XXXXXXXX-XX): ").strip()
            output_path = f"logs/sensor_analysis_{serial}.txt"
            sensor_manager.process_sensor_by_serial(
                serial_number=serial,
                data_folder="files/Sensordata",
                output_path=output_path
            )
            print(f"✅ Sensoranalys sparad till {output_path}")

        elif choice == "2":
            for sub in subs:
                report = torpedo_system.get_friendly_fire_report(subs, sub)
                torpedo_system.log_torpedo_launch(sub, report)

        elif choice == "3":
            serial = input("Ange ubåtens serienummer: ").strip()
            found = next((s for s in subs if s.id == serial), None)
            if not found:
                print("⚠️ Ubåten hittades inte i listan.")
                continue
            nuke.activate_nuke(serial, subs, found)

        elif choice == "4":
            print("Avslutar menyn.")
            break
        else:
            print("⚠️ Ogiltigt val.")




if __name__ == "__main__":
    main()
