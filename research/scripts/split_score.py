import os
import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from scipy import stats

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_TRAINING_DIR = _PROJECT_ROOT / "research" / "data" / "training"
DATA_DIR = str(_TRAINING_DIR)

BG = "#F7F5F0"
CARD = "#FFFFFF"
TEXT = "#0f172a"
TEXT_SOFT = "#334155"
TEXT_MUTED = "#64748b"
BORDER = "#e2e8f0"
PRIMARY = "#0f172a"
GREEN = "#16a34a"
GREEN_BG = "#dcfce7"
RED = "#ee4444"
RED_BG = "#fee2e2"
MUTED_BG = "#f1f5f9"


# Segment labels

LABELS_400MH = [
    "Start→H1",
    "H1→H2",
    "H2→H3",
    "H3→H4",
    "H4→H5",
    "H5→H6",
    "H6→H7",
    "H7→H8",
    "H8→H9",
    "H9→H10",
    "H10→Fin",
]
SHORT_LABELS_400MH = [
    "S→H1",
    "1→2",
    "2→3",
    "3→4",
    "4→5",
    "5→6",
    "6→7",
    "7→8",
    "8→9",
    "9→10",
    "10→F",
]
LABELS_110MH = LABELS_400MH  # same structure: Start→H1 ... H10→Fin
SHORT_LABELS_110MH = SHORT_LABELS_400MH
LABELS_100MH = LABELS_400MH
SHORT_LABELS_100MH = SHORT_LABELS_400MH

LABELS_400M = ["0-100m", "100-200m", "200-300m", "300-400m"]
SHORT_LABELS_400M = ["0-100", "100-200", "200-300", "300-400"]

LABELS_100M = ["0-30m", "30-60m", "60-100m"]
SHORT_LABELS_100M = ["0-30", "30-60", "60-100"]

LABELS_200M = ["0-100m", "100-200m"]
SHORT_LABELS_200M = ["0-100", "100-200"]


def _pct_color(pct: float) -> str:
    """Dot/bar color based on percentile. Lower = faster = green."""
    if pct <= 30:
        return GREEN
    if pct <= 70:
        return TEXT_MUTED
    if pct <= 85:
        return "#c47832"
    return RED


def _pct_bg(pct: float) -> str:
    """Badge background based on percentile."""
    if pct <= 30:
        return GREEN_BG
    if pct <= 70:
        return MUTED_BG
    return RED_BG


def _pdf_to_text(pdf_name: str) -> str:
    """Convert a PDF to text using pdftotext. Returns path to text file."""
    pdf_path = str(_TRAINING_DIR / pdf_name)
    txt_path = os.path.join(tempfile.gettempdir(), pdf_name + ".txt")
    subprocess.run(["pdftotext", "-layout", pdf_path, txt_path], check=True)
    return txt_path


def _extract_floats_until_slash(parts: list[str]) -> list[float]:
    """Extract consecutive floats from a list of string tokens, stopping at '/'."""
    nums: list[float] = []
    for part in parts:
        try:
            nums.append(float(part))
        except ValueError:
            if "/" in part:
                break
    return nums


# ── Hurdle parsers (400mH, 110mH, 100mH share the same touchdown format) ──


def _parse_hurdles(filepath: str, min_time: float, max_time: float) -> list[dict]:
    """
    Generic hurdle parser for events with 10 hurdles + run-in.
    Works for 400mH, 110mH, and 100mH — only the finish time range differs.
    """
    with open(filepath) as f:
        lines = f.readlines()

    races: list[dict] = []
    athlete = ""

    for line in lines:
        stripped = line.strip()

        match = re.match(r"^(.+?)\s*\([A-Z]{3}\)", stripped)
        if match and re.search(r"\(\d{4}\)", stripped) and "H1" in stripped:
            athlete = match.group(1).strip()

        if not re.match(r"^\s*date\s", line):
            continue

        nums = _extract_floats_until_slash(stripped.split()[2:])
        if len(nums) < 11:
            continue

        touchdowns, finish_time = None, None
        if len(nums) == 11:
            touchdowns, finish_time = nums[:10], nums[10]
        else:
            for skip in [5, 6]:
                candidate = nums[:skip] + nums[skip + 1 :]
                if len(candidate) >= 11 and all(
                    candidate[j] < candidate[j + 1] for j in range(10)
                ):
                    touchdowns, finish_time = candidate[:10], candidate[10]
                    break

        if not (touchdowns and finish_time and min_time < finish_time < max_time):
            continue
        if not all(touchdowns[j] < touchdowns[j + 1] for j in range(9)):
            continue

        intervals = [touchdowns[0]] + [
            round(touchdowns[j] - touchdowns[j - 1], 3) for j in range(1, 10)
        ]
        intervals.append(round(finish_time - touchdowns[9], 3))

        if all(0.5 < iv < 10.0 for iv in intervals):
            races.append(
                {"athlete": athlete, "time": finish_time, "intervals": intervals}
            )

    return races


def parse_400mh(filepath: str) -> list[dict]:
    """Parse 400mH touchdown times (finish time 44–65s)."""
    return _parse_hurdles(filepath, min_time=44, max_time=65)


def parse_110mh(filepath: str) -> list[dict]:
    """Parse 110mH touchdown times (finish time 12–16s)."""
    return _parse_hurdles(filepath, min_time=12, max_time=16)


def parse_100mh(filepath: str) -> list[dict]:
    """Parse 100mH (women) touchdown times (finish time 11–15s)."""
    return _parse_hurdles(filepath, min_time=11, max_time=15)


# ── Sprint parsers ──


def parse_400m(filepath: str) -> list[dict]:
    """Parse 400m split times from pdftotext layout output."""
    with open(filepath) as f:
        lines = f.readlines()

    races: list[dict] = []
    athlete = ""

    for i, line in enumerate(lines):
        stripped = line.strip()

        match = re.match(r"^(.+?)\s*\([A-Z]{3}\)", stripped)
        if match and re.search(r"\(\d{4}\)", stripped) and "100m" in stripped:
            athlete = match.group(1).strip()

        if not re.match(r"^\s*date\s", line):
            continue

        nums = _extract_floats_until_slash(stripped.split()[2:])
        official = next((n for n in nums if 43 < n < 60), None)
        if not official:
            continue

        interval_nums: list[float] = []
        for offset in [1, 2]:
            if i + offset < len(lines) and "interval" in lines[i + offset]:
                for part in lines[i + offset].split():
                    try:
                        interval_nums.append(float(part))
                    except ValueError:
                        continue
                break

        cumulative = [n for n in nums if n < official]
        splits = None

        if len(cumulative) >= 8:
            splits = [
                cumulative[1],
                cumulative[3] - cumulative[1],
                cumulative[5] - cumulative[3],
                official - cumulative[5],
            ]
        elif len(cumulative) == 4:
            splits = [
                cumulative[0],
                cumulative[1] - cumulative[0],
                cumulative[2] - cumulative[1],
                official - cumulative[2],
            ]
        elif len(cumulative) == 3 and cumulative[0] < 15:
            splits = [
                cumulative[0],
                cumulative[1] - cumulative[0],
                cumulative[2] - cumulative[1],
                official - cumulative[2],
            ]

        if not splits and len(interval_nums) >= 4:
            for start in range(len(interval_nums) - 3):
                candidate = interval_nums[start : start + 4]
                if abs(sum(candidate) - official) < 0.5:
                    splits = candidate
                    break

        if splits and len(splits) == 4 and all(8 < s < 15 for s in splits):
            races.append(
                {
                    "athlete": athlete,
                    "time": official,
                    "splits": [round(s, 2) for s in splits],
                }
            )

    return races


def parse_100m(filepath: str) -> list[dict]:
    """
    Parse 100m split times into 3 segments: 0-30m, 30-60m, 60-100m.
    The PDF has cumulative times at 10m intervals (10m, 20m, ..., 100m).
    We use: 30m mark, 60m mark, and finish to derive the three splits.
    """
    with open(filepath) as f:
        lines = f.readlines()

    races: list[dict] = []
    athlete = ""

    for i, line in enumerate(lines):
        stripped = line.strip()

        match = re.match(r"^(.+?)\s*\([A-Z]{3}\)", stripped)
        if match and re.search(r"\(\d{4}\)", stripped) and "10m" in stripped:
            athlete = match.group(1).strip()

        if not re.match(r"^\s*date\s", line):
            continue

        nums = _extract_floats_until_slash(stripped.split()[2:])
        official = next((n for n in nums if 9.5 < n < 11.5), None)
        if not official:
            continue

        # Cumulative times less than official (the split marks)
        cumulative = sorted([n for n in nums if 1.0 < n < official])

        splits = None
        # Need at least the 30m, 60m marks from 10m-granularity data
        if len(cumulative) >= 6:
            # indices 2, 5 correspond to 30m and 60m in 10m-step data
            t30 = cumulative[2]
            t60 = cumulative[5]
            splits = [
                round(t30, 3),
                round(t60 - t30, 3),
                round(official - t60, 3),
            ]
        elif len(cumulative) >= 2:
            # Some entries only have 30m and 60m directly
            candidates = [n for n in cumulative if 3.0 < n < 4.5]  # ~30m range
            candidate60 = [n for n in cumulative if 5.5 < n < 7.5]  # ~60m range
            if candidates and candidate60:
                t30 = candidates[0]
                t60 = candidate60[0]
                splits = [
                    round(t30, 3),
                    round(t60 - t30, 3),
                    round(official - t60, 3),
                ]

        if splits and len(splits) == 3 and all(0.5 < s < 8.0 for s in splits):
            races.append(
                {
                    "athlete": athlete,
                    "time": official,
                    "splits": splits,
                }
            )

    return races


def parse_200m(filepath: str) -> list[dict]:
    """
    Parse 200m split times into 2 segments: 0-100m and 100-200m.
    The PDF has cumulative times at 50m, 100m, 150m, and 200m (official).
    We use the 100m mark to derive the two 100m splits.
    """
    with open(filepath) as f:
        lines = f.readlines()

    races: list[dict] = []
    athlete = ""

    for i, line in enumerate(lines):
        stripped = line.strip()

        match = re.match(r"^(.+?)\s*\([A-Z]{3}\)", stripped)
        if match and re.search(r"\(\d{4}\)", stripped) and "200m" in stripped:
            athlete = match.group(1).strip()

        if not re.match(r"^\s*date\s", line):
            continue

        nums = _extract_floats_until_slash(stripped.split()[2:])
        official = next((n for n in nums if 19.0 < n < 25.0), None)
        if not official:
            continue

        cumulative = sorted([n for n in nums if 5.0 < n < official])
        splits = None

        # Look for the 100m mark (~9.5–11.5s range)
        t100_candidates = [n for n in cumulative if 9.5 < n < 11.5]
        if t100_candidates:
            t100 = t100_candidates[0]
            splits = [
                round(t100, 3),
                round(official - t100, 3),
            ]

        if splits and len(splits) == 2 and all(8.0 < s < 14.0 for s in splits):
            races.append(
                {
                    "athlete": athlete,
                    "time": official,
                    "splits": splits,
                }
            )

    return races


# ── RaceAnalyzer ──────────────────────────────────────────────────────────────


class RaceAnalyzer:
    """Compares a single run's splits against a population distribution."""

    LABELS = {
        "400mH": LABELS_400MH,
        "110mH": LABELS_110MH,
        "100mH": LABELS_100MH,
        "400m": LABELS_400M,
        "100m": LABELS_100M,
        "200m": LABELS_200M,
        "400mH_W": LABELS_400MH,
        "400m_W": LABELS_400M,
        "100mH_W": LABELS_100MH,
        "100m_W": LABELS_100M,
        "200m_W": LABELS_200M,
    }
    SHORT_LABELS = {
        "400mH": SHORT_LABELS_400MH,
        "110mH": SHORT_LABELS_110MH,
        "100mH": SHORT_LABELS_100MH,
        "400m": SHORT_LABELS_400M,
        "100m": SHORT_LABELS_100M,
        "200m": SHORT_LABELS_200M,
        "400mH_W": SHORT_LABELS_400MH,
        "400m_W": SHORT_LABELS_400M,
        "100mH_W": SHORT_LABELS_100MH,
        "100m_W": SHORT_LABELS_100M,
        "200m_W": SHORT_LABELS_200M,
    }
    SPLIT_KEY = {
        "400mH": "intervals",
        "110mH": "intervals",
        "100mH": "intervals",
        "400m": "splits",
        "100m": "splits",
        "200m": "splits",
        "400mH_W": "intervals",
        "400m_W": "splits",
        "100mH_W": "intervals",
        "100m_W": "splits",
        "200m_W": "splits",
    }

    def __init__(self, races: list[dict], event_type: str) -> None:
        self.event_type = event_type
        self.labels = self.LABELS[event_type]
        self.short_labels = self.SHORT_LABELS[event_type]
        key = self.SPLIT_KEY[event_type]
        raw = np.array([r[key] for r in races])
        times = np.array([r["time"] for r in races])
        self.population = raw / times[:, None] * 100
        self.pop_mean = self.population.mean(axis=0)
        self.n_races = len(races)

    def analyze_run(self, segments: list[float], total_time: float) -> dict:
        """Compute per-segment percentiles for a single run."""
        normalized = np.array(segments) / total_time * 100
        percentiles = np.array(
            [
                stats.percentileofscore(self.population[:, i], normalized[i])
                for i in range(len(segments))
            ]
        )
        return {
            "normalized": normalized,
            "percentiles": percentiles,
            "total_time": total_time,
        }

    def print_report(self, result: dict, athlete_name: str = "Athlete") -> None:
        """Print a formatted console report card."""
        print(f"\n{'=' * 55}")
        print(f"  {athlete_name}")
        print(
            f"  {self.event_type}  ·  {result['total_time']:.2f}s  ·  vs {self.n_races} races"
        )
        print(f"{'=' * 55}")
        print(f"  {'Segment':<12} {'% Time':>7} {'Pctile':>7}")
        print(f"  {'-' * 28}")
        for i, label in enumerate(self.labels):
            print(
                f"  {label:<12} {result['normalized'][i]:>6.1f}% {result['percentiles'][i]:>6.0f}th"
            )
        print()


# ── Main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    """Load all population data and print constants for hardcoding."""
    print("Loading population data...")

    # Men's events
    hurdle_400m_races = parse_400mh(_pdf_to_text("AthletesFirst_400H_M.pdf"))
    sprint_400m_races = parse_400m(_pdf_to_text("AthletesFirst_400S_M.pdf"))
    hurdle_110m_races = parse_110mh(_pdf_to_text("AthleteFirst_110H_M.pdf"))
    hurdle_100m_races = parse_100mh(_pdf_to_text("AthleteFirst_100H_W.pdf"))
    sprint_100m_races = parse_100m(_pdf_to_text("AthleteFirst_100S_M.pdf"))
    sprint_200m_races = parse_200m(_pdf_to_text("AthleteFirst_200S_M.pdf"))

    # Women's events
    hurdle_400m_w_races = parse_400mh(_pdf_to_text("AthleteFirst_400H_W.pdf"))
    sprint_400m_w_races = parse_400m(_pdf_to_text("AthleteFirst_400S_W.pdf"))
    hurdle_100m_w_races = parse_100mh(_pdf_to_text("AthleteFirst_100H_W.pdf"))
    sprint_100m_w_races = parse_100m(_pdf_to_text("AthleteFirst_100S_W.pdf"))
    sprint_200m_w_races = parse_200m(_pdf_to_text("AthleteFirst_200S_W.pdf"))

    print(f"  400mH: {len(hurdle_400m_races)} races")
    print(f"  400m:  {len(sprint_400m_races)} races")
    print(f"  110mH: {len(hurdle_110m_races)} races")
    print(f"  100mH: {len(hurdle_100m_races)} races")
    print(f"  100m:  {len(sprint_100m_races)} races")
    print(f"  200m:  {len(sprint_200m_races)} races")
    print(f"  400mH_W: {len(hurdle_400m_w_races)} races")
    print(f"  400m_W:  {len(sprint_400m_w_races)} races")
    print(f"  100mH_W: {len(hurdle_100m_w_races)} races")
    print(f"  100m_W:  {len(sprint_100m_w_races)} races")
    print(f"  200m_W:  {len(sprint_200m_w_races)} races")

    events = [
        ("400mH", hurdle_400m_races),
        ("400m", sprint_400m_races),
        ("110mH", hurdle_110m_races),
        ("100mH", hurdle_100m_races),
        ("100m", sprint_100m_races),
        ("200m", sprint_200m_races),
        ("400mH_W", hurdle_400m_w_races),
        ("400m_W", sprint_400m_w_races),
        ("100mH_W", hurdle_100m_w_races),
        ("100m_W", sprint_100m_w_races),
        ("200m_W", sprint_200m_w_races),
    ]

    for name, races in events:
        analyzer = RaceAnalyzer(races, name)
        pop = analyzer.population
        print(f"\n── {name} ({len(races)} races) ──")
        print(f"{name} mean:", np.round(pop.mean(0), 4).tolist())
        print(f"{name} std: ", np.round(pop.std(0), 4).tolist())
        print(f"{name} p10: ", np.percentile(pop, 10, axis=0).round(4).tolist())
        print(f"{name} p25: ", np.percentile(pop, 25, axis=0).round(4).tolist())
        print(f"{name} p75: ", np.percentile(pop, 75, axis=0).round(4).tolist())
        print(f"{name} p90: ", np.percentile(pop, 90, axis=0).round(4).tolist())

    print("\nDone.")


if __name__ == "__main__":
    main()
