import os
import re
import subprocess
import tempfile

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import FancyBboxPatch
from scipy import stats

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")

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
    "Start→H1", "H1→H2", "H2→H3", "H3→H4", "H4→H5",
    "H5→H6", "H6→H7", "H7→H8", "H8→H9", "H9→H10", "H10→Fin",
]
SHORT_LABELS_400MH = [
    "S→H1", "1→2", "2→3", "3→4", "4→5",
    "5→6", "6→7", "7→8", "8→9", "9→10", "10→F",
]
LABELS_400M = ["0-100m", "100-200m", "200-300m", "300-400m"]
SHORT_LABELS_400M = ["0-100", "100-200", "200-300", "300-400"]


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


def _pdf_to_text(pdf_path: str) -> str:
    """Convert a PDF to text using pdftotext. Returns path to text file."""
    pdf_path = os.path.join(SCRIPT_DIR, pdf_path)
    txt_path = os.path.join(
        tempfile.gettempdir(), os.path.basename(pdf_path) + ".txt"
    )
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


def parse_400mh(filepath: str) -> list[dict]:
    """Parse 400mH touchdown times from pdftotext layout output."""
    with open(filepath) as f:
        lines = f.readlines()

    races: list[dict] = []
    athlete = ""

    for line in lines:
        stripped = line.strip()

        # Detect athlete header
        match = re.match(r"^(.+?)\s*\([A-Z]{3}\)", stripped)
        if match and re.search(r"\(\d{4}\)", stripped) and "H1" in stripped:
            athlete = match.group(1).strip()

        # Detect touchdown times line
        if not re.match(r"^\s*date\s", line):
            continue

        nums = _extract_floats_until_slash(stripped.split()[2:])
        if len(nums) < 11:
            continue

        # Extract touchdowns and finish time (handle optional 200m split)
        touchdowns, finish_time = None, None
        if len(nums) == 11:
            touchdowns, finish_time = nums[:10], nums[10]
        else:
            for skip in [5, 6]:
                candidate = nums[:skip] + nums[skip + 1:]
                if len(candidate) >= 11 and all(
                    candidate[j] < candidate[j + 1] for j in range(10)
                ):
                    touchdowns, finish_time = candidate[:10], candidate[10]
                    break

        if not (touchdowns and finish_time and 44 < finish_time < 65):
            continue
        if not all(touchdowns[j] < touchdowns[j + 1] for j in range(9)):
            continue

        # Compute inter-hurdle intervals from cumulative touchdowns
        intervals = [touchdowns[0]] + [
            round(touchdowns[j] - touchdowns[j - 1], 3) for j in range(1, 10)
        ]
        intervals.append(round(finish_time - touchdowns[9], 3))

        if all(1.0 < iv < 10.0 for iv in intervals):
            races.append(
                {"athlete": athlete, "time": finish_time, "intervals": intervals}
            )

    return races


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

        # Find interval line (next 1–2 lines)
        interval_nums: list[float] = []
        for offset in [1, 2]:
            if i + offset < len(lines) and "interval" in lines[i + offset]:
                for part in lines[i + offset].split():
                    try:
                        interval_nums.append(float(part))
                    except ValueError:
                        continue
                break

        # Derive 100m splits from cumulative times
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

        # Fallback: find 4 values in interval line that sum to official
        if not splits and len(interval_nums) >= 4:
            for start in range(len(interval_nums) - 3):
                candidate = interval_nums[start: start + 4]
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


# Analyzes races


class RaceAnalyzer:
    """Compares a single run's splits against a population distribution."""

    def __init__(self, races: list[dict], event_type: str) -> None:
        self.event_type = event_type

        if event_type == "400mH":
            self.labels = LABELS_400MH
            self.short_labels = SHORT_LABELS_400MH
            raw = np.array([r["intervals"] for r in races])
        else:
            self.labels = LABELS_400M
            self.short_labels = SHORT_LABELS_400M
            raw = np.array([r["splits"] for r in races])

        times = np.array([r["time"] for r in races])
        self.population = raw / times[:, None] * 100
        self.pop_mean = self.population.mean(axis=0)
        self.n_races = len(races)

    def analyze_run(self, segments: list[float], total_time: float) -> dict:
        """Compute per-segment percentiles for a single run."""
        normalized = np.array(segments) / total_time * 100
        percentiles = np.array([
            stats.percentileofscore(self.population[:, i], normalized[i])
            for i in range(len(segments))
        ])
        return {
            "normalized": normalized,
            "percentiles": percentiles,
            "total_time": total_time,
        }

    def print_report(self, result: dict, athlete_name: str = "Athlete") -> None:
        """Print a formatted console report card."""
        print(f"\n{'=' * 55}")
        print(f"  {athlete_name}")
        print(f"  {self.event_type}  ·  {result['total_time']:.2f}s  ·  vs {self.n_races} races")
        print(f"{'=' * 55}")
        print(f"  {'Segment':<12} {'% Time':>7} {'Pctile':>7}")
        print(f"  {'-' * 28}")

        for i, label in enumerate(self.labels):
            print(f"  {label:<12} {result['normalized'][i]:>6.1f}% {result['percentiles'][i]:>6.0f}th")
        print()

    # ── Mobile Visualization ─────────────────────────────────

    def plot_mobile(
        self,
        result: dict,
        athlete_name: str = "Athlete",
        save_path: str | None = None,
    ) -> None:
        """Generate a mobile-styled race report matching the StrideTrack app."""
        normalized = result["normalized"]
        percentiles = result["percentiles"]
        total_time = result["total_time"]
        n_seg = len(self.labels)

        # Layout sizing (mobile: ~390px wide at 2x retina)
        w = 4.0
        header_h = 0.75
        chart_h = 2.6
        row_h = 0.36
        table_h = 0.4 + row_h * n_seg + 0.1
        gap = 0.12
        total_h = header_h + gap + chart_h + gap + table_h + 0.2

        fig = plt.figure(figsize=(w, total_h), facecolor=BG, dpi=200)
        cursor_y = total_h

        # ── Layout helpers ──

        def card_axes(height: float, pad_lr: float = 0.05) -> plt.Axes:
            nonlocal cursor_y
            cursor_y -= height
            ax = fig.add_axes(
                [pad_lr, cursor_y / total_h, 1 - 2 * pad_lr, height / total_h]
            )
            ax.set_facecolor(CARD)
            for spine in ax.spines.values():
                spine.set_color(BORDER)
                spine.set_linewidth(0.5)
            ax.set_xticks([])
            ax.set_yticks([])
            return ax

        def spacer(h: float = 0.12) -> None:
            nonlocal cursor_y
            cursor_y -= h

        # ── Header ──

        cursor_y -= header_h
        fig.text(
            0.06, cursor_y / total_h + 0.72 * header_h / total_h,
            athlete_name,
            fontsize=12, color=TEXT, fontweight="bold", fontfamily="sans-serif",
        )
        fig.text(
            0.06, cursor_y / total_h + 0.25 * header_h / total_h,
            f"{self.event_type}  ·  {total_time:.2f}s  ·  vs {self.n_races:,} elite races",
            fontsize=7, color=TEXT_MUTED, fontfamily="sans-serif",
        )

        spacer()

        # ── Pacing Chart ──

        ax = card_axes(chart_h, pad_lr=0.04)
        x = np.arange(n_seg)

        # Population percentile bands
        p10 = np.percentile(self.population, 10, axis=0)
        p25 = np.percentile(self.population, 25, axis=0)
        p75 = np.percentile(self.population, 75, axis=0)
        p90 = np.percentile(self.population, 90, axis=0)

        ax.fill_between(x, p10, p90, alpha=0.06, color=PRIMARY)
        ax.fill_between(x, p25, p75, alpha=0.12, color=PRIMARY)
        ax.plot(x, self.pop_mean, color=PRIMARY, ls="--", lw=1, alpha=0.35)
        ax.plot(x, normalized, color=TEXT, lw=2, zorder=5)

        # Dots colored by percentile
        for i, (norm, pct) in enumerate(zip(normalized, percentiles)):
            ax.plot(
                i, norm, "o", ms=5, color=_pct_color(pct),
                zorder=6, markeredgecolor="white", markeredgewidth=1.2,
            )

        ax.set_xticks(x)
        ax.set_xticklabels(
            self.short_labels, fontsize=5.5,
            color=TEXT_MUTED, fontfamily="sans-serif",
        )
        ax.tick_params(axis="y", labelsize=5.5, labelcolor=TEXT_MUTED)
        ax.set_ylabel("% of Total Time", fontsize=6, color=TEXT_MUTED, fontfamily="sans-serif")
        ax.grid(axis="y", color=BORDER, linewidth=0.3, alpha=0.5)
        ax.set_title(
            "Pacing Profile", fontsize=8, color=TEXT, fontweight="bold",
            loc="left", pad=6, fontfamily="sans-serif",
        )
        ax.text(
            0.98, 0.97,
            "— athlete    --- mean    ░ 25th–75th pctile",
            fontsize=4.5, color=TEXT_MUTED, ha="right", va="top",
            transform=ax.transAxes, fontfamily="sans-serif",
        )
        for spine in ax.spines.values():
            spine.set_color(BORDER)
            spine.set_linewidth(0.5)

        spacer()

        # ── Segment Table ──

        ax_t = card_axes(table_h, pad_lr=0.04)
        ax_t.set_xlim(0, 10)
        ax_t.set_ylim(0, n_seg + 1.1)

        # Title
        ax_t.text(
            0.25, n_seg + 0.6, "Segment Breakdown",
            fontsize=8, color=TEXT, fontweight="bold",
            va="center", fontfamily="sans-serif",
        )

        # Column headers
        col_headers = [
            ("Segment", 0.25, "left"),
            ("Time", 3.2, "right"),
            ("% Total", 4.8, "right"),
            ("Pctile", 6.3, "center"),
        ]
        for label, xpos, ha in col_headers:
            ax_t.text(
                xpos, n_seg + 0.1, label,
                fontsize=5, color=TEXT_MUTED, fontweight="600",
                ha=ha, va="center", fontfamily="sans-serif",
            )

        # Header separator
        ax_t.plot([0.15, 9.85], [n_seg - 0.05, n_seg - 0.05], color=BORDER, lw=0.5)

        # Rows
        for i, label in enumerate(self.labels):
            row_y = n_seg - 0.55 - i * 0.85
            pct = percentiles[i]
            norm = normalized[i]
            raw_s = norm * total_time / 100
            color = _pct_color(pct)

            # Row separator
            if i < n_seg - 1:
                ax_t.plot(
                    [0.15, 9.85], [row_y - 0.35, row_y - 0.35],
                    color=BORDER, lw=0.3,
                )

            # Segment name
            ax_t.text(
                0.25, row_y, label,
                fontsize=6, color=TEXT, fontweight="500",
                va="center", fontfamily="sans-serif",
            )

            # Raw time
            ax_t.text(
                3.2, row_y, f"{raw_s:.2f}s",
                fontsize=6, color=TEXT_SOFT, va="center",
                ha="right", fontfamily="sans-serif",
            )

            # % of total
            ax_t.text(
                4.8, row_y, f"{norm:.1f}%",
                fontsize=6, color=TEXT_MUTED, va="center",
                ha="right", fontfamily="sans-serif",
            )

            # Percentile badge
            badge = FancyBboxPatch(
                (5.6, row_y - 0.2), 1.3, 0.4,
                boxstyle="round,pad=0.08",
                facecolor=_pct_bg(pct), edgecolor="none", zorder=3,
            )
            ax_t.add_patch(badge)
            ax_t.text(
                6.25, row_y, f"{pct:.0f}th",
                fontsize=5.5, color=color, fontweight="bold",
                ha="center", va="center", zorder=4, fontfamily="sans-serif",
            )

            # Progress bar
            bar_x, bar_w = 7.3, 2.5
            ax_t.add_patch(plt.Rectangle(
                (bar_x, row_y - 0.09), bar_w, 0.18,
                facecolor=MUTED_BG, edgecolor="none", zorder=2,
            ))
            ax_t.add_patch(plt.Rectangle(
                (bar_x, row_y - 0.09), bar_w * (pct / 100), 0.18,
                facecolor=color, edgecolor="none", zorder=3,
            ))

        # Save
        if save_path:
            plt.savefig(save_path, dpi=200, bbox_inches="tight", facecolor=BG)
            print(f"  Saved: {save_path}")
        plt.close()


# ── Test Data ────────────────────────────────────────────────

MOCK_400MH_RUNS = [
    {
        "name": "Warholm WR (Tokyo 2021)",
        "time": 45.94,
        "segments": [5.60, 3.48, 3.54, 3.66, 3.68, 3.90, 4.06, 4.12, 4.28, 4.44, 5.18],
    },
    {
        "name": "Mock: Late Collapse",
        "time": 51.20,
        "segments": [6.10, 3.80, 3.85, 3.90, 3.95, 4.10, 4.30, 4.80, 5.40, 5.80, 5.20],
    },
    {
        "name": "Mock: Aggressive Start",
        "time": 49.80,
        "segments": [5.50, 3.40, 3.50, 3.60, 3.80, 4.20, 4.50, 4.70, 5.00, 5.30, 6.30],
    },
]

MOCK_400M_RUNS = [
    {
        "name": "van Niekerk WR (Rio 2016)",
        "time": 43.03,
        "segments": [10.77, 9.81, 10.48, 11.97],
    },
    {
        "name": "Mock: Too Fast Start",
        "time": 47.50,
        "segments": [10.80, 10.20, 12.00, 14.50],
    },
]


# ── Main ─────────────────────────────────────────────────────


def main() -> None:
    """Load population data, run mock test cases, generate reports."""
    print("Loading population data...")
    hurdle_races = parse_400mh(_pdf_to_text("data/AthletesFirst_400H.pdf"))
    sprint_races = parse_400m(_pdf_to_text("data/AthletesFirst_400S.pdf"))
    print(f"  400mH: {len(hurdle_races)} races  |  400m: {len(sprint_races)} races")

    hurdle_analyzer = RaceAnalyzer(hurdle_races, "400mH")
    sprint_analyzer = RaceAnalyzer(sprint_races, "400m")

    for analyzer, mock_runs in [
        (hurdle_analyzer, MOCK_400MH_RUNS),
        (sprint_analyzer, MOCK_400M_RUNS),
    ]:
        for run in mock_runs:
            result = analyzer.analyze_run(run["segments"], run["time"])
            analyzer.print_report(result, run["name"])

            safe_name = (
                run["name"]
                .replace(" ", "_")
                .replace(":", "")
                .replace("(", "")
                .replace(")", "")
            )
            analyzer.plot_mobile(
                result,
                run["name"],
                save_path=os.path.join(DATA_DIR, f"report_{safe_name}.png"),
            )

    print("Done.")


if __name__ == "__main__":
    main()