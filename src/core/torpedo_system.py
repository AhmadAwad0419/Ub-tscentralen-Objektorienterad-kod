from typing import List, Dict, Tuple, Optional, Generator
from src.core.submarine import Submarine
from src.utils.logger import torpedo_logger

class TorpedoSystem:
    """It handles torpedo launches and checks for friendly fire,
    yielding results and compiling them into a report.
    """

    def check_for_friendly_fire(
        self,
        submarines: List[Submarine],
        submarine_to_check: Submarine
    ) -> Generator[Tuple[str, bool, Optional[Tuple[int, int]]], None, None]:
        """
        A generator that returns 
        (direction, safe, first_target) for each direction, where first_target is (x, y) or None.
        """
        shooter_x, shooter_y = submarine_to_check.position

        up_candidates = []
        down_candidates = []
        forward_candidates = []

        for sub in submarines:
            if sub is submarine_to_check:
                continue
            target_x, target_y = sub.position

            if target_x == shooter_x:
                if target_y < shooter_y:
                    up_candidates.append((sub, shooter_y - target_y))
                elif target_y > shooter_y:
                    down_candidates.append((sub, target_y - shooter_y))

            if target_y == shooter_y and target_x > shooter_x:
                forward_candidates.append((sub, target_x - shooter_x))

        def pick_closest(candidates: List[Tuple[Submarine, int]]) -> Optional[Tuple[int, int]]:
            """Pick the candidate with the smallest distance."""
            if not candidates:
                return None
            best = candidates[0]
            best_distance = best[1]
            for cand in candidates[1:]:
                if cand[1] < best_distance:
                    best = cand
                    best_distance = cand[1]
            chosen_sub = best[0]
            return chosen_sub.position

        up_first = pick_closest(up_candidates)
        down_first = pick_closest(down_candidates)
        forward_first = pick_closest(forward_candidates)

        yield ("up", up_first is None, up_first)
        yield ("down", down_first is None, down_first)
        yield ("forward", forward_first is None, forward_first)

    def get_friendly_fire_report(
        self,
        submarines: List[Submarine],
        submarine_to_check: Submarine
    ) -> Dict[str, Dict[str, Optional[Tuple[int, int]]]]:
        """Collects the generator’s output into a dictionary for easy use."""
        report: Dict[str, Dict[str, Optional[Tuple[int, int]]]] = {}
        for direction, safe, first_target in self.check_for_friendly_fire(submarines, submarine_to_check):
            report[direction] = {"safe": safe, "first_target": first_target}
        return report

    def log_torpedo_launch(
        self,
        submarine: Submarine,
        check_result: Dict[str, Dict[str, Optional[Tuple[int, int]]]]
    ) -> None:
        """Log a torpedo launch attempt and friendly-fire risks."""
        sid = getattr(submarine, "id", "<unknown>")
        torpedo_logger.info(f"Torpedo launch attempt from submarine {sid} at {submarine.position}")

        for direction in ("up", "down", "forward"):
            info = check_result.get(direction, {})
            if info.get("safe", True):
                torpedo_logger.info(f"{sid}: {direction} → SAFE")
            else:
                target = info.get("first_target")
                torpedo_logger.warning(f"{sid}: {direction} → RISK OF FRIENDLY FIRE, first target at {target}")