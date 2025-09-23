import os
import hashlib
from collections import Counter
from pathlib import Path
from src.utils.logger import sensor_logger, log_calls
from src.config.paths import SENSOR_DATA_DIR, LOG_DIR

PATTERN_LEN = 208

class SensorManager:
    """Exakt analys av sensorloggar med hashning."""

    def __init__(self, reader=None, movement_manager=None):
        self.reader = reader
        self.movement_manager = movement_manager
        self._cache: dict[str, dict] = {}   # {serial: analysresultat}
        self._hashes: dict[str, str] = {}   # {serial: filhash}

    # --- Hjälpmetod: filhash ---
    def _file_sha256(self, file_path: Path) -> str:
        sha = hashlib.sha256()
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(1 << 15), b""):
                sha.update(block)
        return sha.hexdigest()

    # --- Hjälpmetod: radvalidering ---
    def _valid_line(self, s: str) -> bool:
        return len(s) == PATTERN_LEN and not (set(s) - {"0", "1"})

    # --- Huvudmetod ---
    def process_sensor_by_serial(self, serial_number: str) -> dict:
        """
        Exakt analys:
          - max antal 0:or i en rad
          - frekvens av identiska mönster (via SHA1-hash)
        """
        file_path = SENSOR_DATA_DIR / f"{serial_number}.txt"
        if not file_path.exists():
            return {
                "id": serial_number,
                "status": "missing",
                "msg": f"Missing sensor file (expected at: {file_path.as_posix()})",
            }

        # Hasha filen → cache-kontroll
        file_hash = self._file_sha256(file_path)
        if self._hashes.get(serial_number) == file_hash and serial_number in self._cache:
            return self._cache[serial_number]

        total_lines = 0
        max_errors = 0
        counts: Counter[str] = Counter()
        exemplars: dict[str, str] = {}

        # Streama filen rad-för-rad
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                s = line.strip()
                if not s:
                    continue
                if not self._valid_line(s):
                    total_lines += 1
                    continue

                total_lines += 1
                zeros = s.count("0")
                if zeros > max_errors:
                    max_errors = zeros

                h = hashlib.sha1(s.encode("ascii")).hexdigest()
                counts[h] += 1
                if h not in exemplars:
                    exemplars[h] = s  # spara ett exempel

        # Ta topp 5 mönster för rapport
        most_common = [(exemplars[h], c) for h, c in counts.most_common(5)]

        result = {
            "id": serial_number,
            "status": "ok",
            "lines": total_lines,
            "max_errors": max_errors,
            "common": most_common,
            "unique_patterns": len(counts),
            "mode": "exact",
        }

        # Cachea
        self._hashes[serial_number] = file_hash
        self._cache[serial_number] = result
        return result

    @log_calls(sensor_logger, "sensor")
    def process_all_sensor_data(self, only_active: bool = True) -> None:
        """
        Kör exakt analys för subs. Default = bara aktiva.
        """
        if self.movement_manager is None:
            sensor_logger.error("No movement_manager linked to SensorManager")
            return

        subs = (
            self.movement_manager.active_subs
            if only_active else self.movement_manager.submarines.values()
        )

        results = []
        for sub in subs:
            res = self.process_sensor_by_serial(sub.id)
            results.append(res)

            if res["status"] == "missing":
                sensor_logger.warning(
                    f"[Sensor] {res['id']} missing file → {res['msg']}"
                )
            else:
                sensor_logger.info(
                    f"[Sensor] {res['id']}: {res['lines']} lines, "
                    f"max errors {res['max_errors']}, "
                    f"unique patterns {res['unique_patterns']}"
                )

        # --- Sammanställning sparas om du vill följa hela körningen ---
        out_path = Path(LOG_DIR) / "sensor_analysis_all.txt"
        with open(out_path, "a", encoding="utf-8") as outfile:
            outfile.write(f"=== Round analysis ({len(subs)} active subs) ===\n")
            for res in results:
                if res["status"] == "missing":
                    outfile.write(f"{res['id']}: MISSING\n")
                else:
                    outfile.write(
                        f"{res['id']}: {res['lines']} lines, "
                        f"max errors = {res['max_errors']}, "
                        f"unique patterns = {res['unique_patterns']}\n"
                    )
            outfile.write("\n")
