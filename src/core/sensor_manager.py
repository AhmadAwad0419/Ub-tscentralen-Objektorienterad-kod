from collections import Counter
import hashlib
from pathlib import Path
from src.utils.logger import sensor_logger
from src.config.paths import SENSOR_DATA_DIR, LOG_DIR

PATTERN_LEN = 208

class SensorManager:
    """Stegvis analys av sensordata: en rad per runda."""

    def __init__(self, movement_manager=None):
        self.movement_manager = movement_manager
        self.generators: dict[str, iter] = {}
        self.pattern_counts: dict[str, Counter] = {}    # sub_id -> Counter över mönster-hash
        self.pattern_examples: dict[str, dict] = {}     # sub_id -> {hash: exempelsträng}

    def _sensor_line_generator(self, file_path: Path):
        """Ger giltiga rader (208 tecken av 0/1) från en sensorfil."""
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                s = line.strip()
                if len(s) == PATTERN_LEN and not (set(s) - {"0","1"}):
                    yield s

    def attach_generators(self, submarines):
        """Initiera sensor-generators för alla subs."""
        for sub in submarines:
            file_path = SENSOR_DATA_DIR / f"{sub.id}.txt"
            if not file_path.exists():
                sensor_logger.warning(f"No sensor file for {sub.id}")
                continue
            self.generators[sub.id] = self._sensor_line_generator(file_path)
            self.pattern_counts[sub.id] = Counter()
            self.pattern_examples[sub.id] = {}

    def process_next_round(self, round_counter: int, only_active=True):
        """Läs nästa rad för varje sub och logga antalet fel + uppdatera mönsterstatistik."""
        subs = (
            self.movement_manager.active_subs
            if only_active else self.movement_manager.submarines.values()
        )

        for sub in subs:
            gen = self.generators.get(sub.id)
            if not gen:
                continue

            try:
                new_pattern = next(gen)
            except StopIteration:
                sensor_logger.info(f"{sub.id}: no more sensor data")
                continue

            # 1. Antal fel (0:or)
            zero_count = new_pattern.count("0")
            sensor_logger.info(f"{sub.id}: {zero_count} sensor errors this round")

            # 2. Mönsterstatistik
            h = hashlib.sha1(new_pattern.encode("ascii")).hexdigest()
            self.pattern_counts[sub.id][h] += 1
            if h not in self.pattern_examples[sub.id]:
                self.pattern_examples[sub.id][h] = new_pattern

    def final_summary(self):
        """Summera sensordata efter simuleringen och logga till sensor_logger."""
        sensor_logger.info("=== Final Sensor Summary ===")

        for sub_id in self.generators.keys():
            unique = len(self.pattern_counts.get(sub_id, {}))
            top5 = self.pattern_counts[sub_id].most_common(5)
            examples = [
                (self.pattern_examples[sub_id][h], c) for h, c in top5
            ]

            sensor_logger.info(
                f"{sub_id}: unique_patterns={unique}, top={examples}"
            )
                
