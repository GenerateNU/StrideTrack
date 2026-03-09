"""
StrideTrack R&D: Percentile-Based Race Report Card
===================================================
Compares an athlete's normalized split profile against the Athletes First
dataset and reports per-segment percentile rankings.

Test script — validates the approach with mock run inputs.
"""

import re, os, subprocess, tempfile
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")

# ── PARSING (same as anomaly_detection.py) ───────────────────

def pdf_to_text(pdf_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(script_dir, pdf_path)
    txt_path = os.path.join(tempfile.gettempdir(), os.path.basename(pdf_path) + '.txt')
    subprocess.run(['pdftotext', '-layout', pdf_path, txt_path], check=True)
    return txt_path

def parse_400mh(filepath):
    with open(filepath) as f:
        lines = f.readlines()
    races, athlete = [], ""
    for i, line in enumerate(lines):
        s = line.strip()
        m = re.match(r'^(.+?)\s*\([A-Z]{3}\)', s)
        if m and re.search(r'\(\d{4}\)', s) and 'H1' in s:
            athlete = m.group(1).strip()
        if not re.match(r'^\s*date\s', line):
            continue
        nums = []
        for p in s.split()[2:]:
            try: nums.append(float(p))
            except ValueError:
                if '/' in p: break
        if len(nums) < 11: continue
        td, time = None, None
        if len(nums) == 11:
            td, time = nums[:10], nums[10]
        else:
            for skip in [5, 6]:
                c = nums[:skip] + nums[skip+1:]
                if len(c) >= 11 and all(c[j] < c[j+1] for j in range(10)):
                    td, time = c[:10], c[10]; break
        if not (td and time and 44 < time < 65): continue
        if not all(td[j] < td[j+1] for j in range(9)): continue
        intervals = [td[0]] + [round(td[j]-td[j-1], 3) for j in range(1, 10)]
        intervals.append(round(time - td[9], 3))
        if all(1.0 < iv < 10.0 for iv in intervals):
            races.append({'athlete': athlete, 'time': time, 'intervals': intervals})
    return races

def parse_400m(filepath):
    with open(filepath) as f:
        lines = f.readlines()
    races, athlete = [], ""
    for i, line in enumerate(lines):
        s = line.strip()
        m = re.match(r'^(.+?)\s*\([A-Z]{3}\)', s)
        if m and re.search(r'\(\d{4}\)', s) and '100m' in s:
            athlete = m.group(1).strip()
        if not re.match(r'^\s*date\s', line): continue
        nums = []
        for p in s.split()[2:]:
            try: nums.append(float(p))
            except ValueError:
                if '/' in p: break
        official = next((n for n in nums if 43 < n < 60), None)
        if not official: continue
        inums = []
        for off in [1, 2]:
            if i + off < len(lines) and 'interval' in lines[i+off]:
                for p in lines[i+off].split():
                    try: inums.append(float(p))
                    except ValueError: continue
                break
        cum = [n for n in nums if n < official]
        splits = None
        if len(cum) >= 8:
            splits = [cum[1], cum[3]-cum[1], cum[5]-cum[3], official-cum[5]]
        elif len(cum) == 4:
            splits = [cum[0], cum[1]-cum[0], cum[2]-cum[1], official-cum[2]]
        elif len(cum) == 3 and cum[0] < 15:
            splits = [cum[0], cum[1]-cum[0], cum[2]-cum[1], official-cum[2]]
        if not splits and len(inums) >= 4:
            for start in range(len(inums) - 3):
                c = inums[start:start+4]
                if abs(sum(c) - official) < 0.5: splits = c; break
        if splits and len(splits) == 4 and all(8 < s < 15 for s in splits):
            races.append({'athlete': athlete, 'time': official,
                         'splits': [round(s, 2) for s in splits]})
    return races


# ── PERCENTILE ENGINE ────────────────────────────────────────

class RaceAnalyzer:
    """Stores population distributions and computes percentile reports."""

    def __init__(self, races, event_type):
        """
        Args:
            races: list of dicts with 'time' and 'intervals'/'splits'
            event_type: '400mH' or '400m'
        """
        self.event_type = event_type

        if event_type == '400mH':
            self.labels = ['Start→H1'] + [f'H{i}→H{i+1}' for i in range(1, 10)] + ['H10→Fin']
            raw = np.array([r['intervals'] for r in races])
        else:
            self.labels = ['0-100m', '100-200m', '200-300m', '300-400m']
            raw = np.array([r['splits'] for r in races])

        times = np.array([r['time'] for r in races])

        # Normalize: each segment as % of total time
        self.population = raw / times[:, None] * 100
        self.pop_mean = self.population.mean(axis=0)
        self.n_races = len(races)

    def analyze_run(self, segments, total_time):
        """
        Analyze a single run against the population.

        Args:
            segments: list of raw segment times (seconds)
            total_time: official finish time (seconds)

        Returns:
            dict with normalized splits, percentiles, and coaching notes
        """
        segments = np.array(segments)
        normalized = segments / total_time * 100

        percentiles = np.array([
            stats.percentileofscore(self.population[:, i], normalized[i])
            for i in range(len(segments))
        ])

        notes = []
        for i, (pct, label) in enumerate(zip(percentiles, self.labels)):
            if pct > 85:
                notes.append(f"⚠ {label}: {pct:.0f}th percentile — significant deceleration. "
                             f"Focus on maintaining pace here.")
            elif pct > 70:
                notes.append(f"⚡ {label}: {pct:.0f}th percentile — mild deceleration. "
                             f"Room for improvement.")
            elif pct < 15:
                notes.append(f"✓ {label}: {pct:.0f}th percentile — strong segment.")

        return {
            'normalized': normalized,
            'percentiles': percentiles,
            'notes': notes,
            'total_time': total_time,
        }

    def print_report(self, result, athlete_name="Athlete"):
        """Print a text race report card."""
        print(f"\n{'='*60}")
        print(f"  RACE REPORT CARD: {athlete_name}")
        print(f"  Event: {self.event_type}  |  Time: {result['total_time']:.2f}s")
        print(f"  Compared against {self.n_races} elite races")
        print(f"{'='*60}")
        print(f"  {'Segment':<12} {'% Time':>7} {'Pctile':>7}")
        print(f"  {'-'*28}")

        for i, label in enumerate(self.labels):
            pct = result['percentiles'][i]
            norm = result['normalized'][i]
            print(f"  {label:<12} {norm:>6.1f}% {pct:>6.0f}th")

        if result['notes']:
            print(f"\n  Coaching Notes:")
            for note in result['notes']:
                print(f"    {note}")
        print()

    def plot_report(self, result, athlete_name="Athlete", save_path=None):
        """Generate a visual race report card."""
        fig, axes = plt.subplots(1, 2, figsize=(16, 6),
                                 gridspec_kw={'width_ratios': [2, 1]})
        fig.suptitle(f"Race Report: {athlete_name} — {self.event_type} ({result['total_time']:.2f}s)",
                     fontsize=14, fontweight='bold')

        # ── Left: pacing curve with population band ──
        ax = axes[0]
        x = np.arange(len(self.labels))

        p10 = np.percentile(self.population, 10, axis=0)
        p25 = np.percentile(self.population, 25, axis=0)
        p75 = np.percentile(self.population, 75, axis=0)
        p90 = np.percentile(self.population, 90, axis=0)

        ax.fill_between(x, p10, p90, alpha=0.15, color='steelblue', label='10th–90th pctile')
        ax.fill_between(x, p25, p75, alpha=0.25, color='steelblue', label='25th–75th pctile')
        ax.plot(x, self.pop_mean, 'b--', lw=1.5, alpha=0.6, label='Population mean')
        ax.plot(x, result['normalized'], 'ro-', lw=2.5, ms=8, label=athlete_name, zorder=5)

        # Color markers by percentile: green=low(fast), red=high(slow)
        for i, (norm, pct) in enumerate(zip(result['normalized'], result['percentiles'])):
            color = plt.cm.RdYlGn_r(pct / 100)  # 0=green, 100=red
            ax.plot(i, norm, 'o', ms=10, color=color, zorder=6,
                    markeredgecolor='white', markeredgewidth=1.5)

        ax.set_xticks(x)
        ax.set_xticklabels(self.labels, rotation=45, ha='right', fontsize=8)
        ax.set_ylabel('% of Total Time')
        ax.set_title('Pacing Profile vs Population')
        ax.legend(fontsize=8, loc='upper left')

        # ── Right: percentile bar chart ──
        ax = axes[1]
        colors = [plt.cm.RdYlGn_r(p / 100) for p in result['percentiles']]
        ax.barh(x, result['percentiles'], color=colors, edgecolor='white', height=0.7)

        ax.axvline(50, color='gray', ls='--', lw=1, alpha=0.5)
        ax.axvline(25, color='green', ls=':', lw=1, alpha=0.4)
        ax.axvline(75, color='orange', ls=':', lw=1, alpha=0.4)

        ax.set_yticks(x)
        ax.set_yticklabels(self.labels, fontsize=8)
        ax.set_xlabel('Percentile (lower = faster)')
        ax.set_title('Segment Percentiles')
        ax.set_xlim(0, 100)

        for i, pct in enumerate(result['percentiles']):
            ax.text(min(pct + 2, 88), i, f'{pct:.0f}th',
                    va='center', fontsize=8, fontweight='bold')

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"  Saved: {save_path}")
        plt.close()


# ── TEST RUNS ────────────────────────────────────────────────

def main():
    print("Loading population data...")
    h_races = parse_400mh(pdf_to_text("data/AthletesFirst_400H.pdf"))
    s_races = parse_400m(pdf_to_text("data/AthletesFirst_400S.pdf"))
    print(f"  400mH: {len(h_races)} races  |  400m: {len(s_races)} races")

    h_analyzer = RaceAnalyzer(h_races, '400mH')
    s_analyzer = RaceAnalyzer(s_races, '400m')

    # ── Mock 400mH runs ──

    # Mock 1: Clean race — Warholm's WR (should be all A's/B's)
    warholm_wr = {
        'name': 'Warholm WR (Tokyo 2021)',
        'time': 45.94,
        'segments': [5.60, 3.48, 3.54, 3.66, 3.68, 3.90, 4.06, 4.12, 4.28, 4.44, 5.18],
    }

    # Mock 2: Late-race collapse — athlete falls apart after H7
    collapse = {
        'name': 'Mock: Late Collapse',
        'time': 51.20,
        'segments': [6.10, 3.80, 3.85, 3.90, 3.95, 4.10, 4.30, 4.80, 5.40, 5.80, 5.20],
    }

    # Mock 3: Aggressive start, paid for it later
    aggressive = {
        'name': 'Mock: Aggressive Start',
        'time': 49.80,
        'segments': [5.50, 3.40, 3.50, 3.60, 3.80, 4.20, 4.50, 4.70, 5.00, 5.30, 6.30],
    }

    for run in [warholm_wr, collapse, aggressive]:
        result = h_analyzer.analyze_run(run['segments'], run['time'])
        h_analyzer.print_report(result, run['name'])
        safe_name = run['name'].replace(' ', '_').replace(':', '').replace('(', '').replace(')', '')
        h_analyzer.plot_report(result, run['name'],
                               save_path=os.path.join(DATA_DIR, f'report_400mH_{safe_name}.png'))

    # ── Mock 400m runs ──

    # Mock 4: van Niekerk WR — perfectly paced
    vniekerk = {
        'name': 'van Niekerk WR (Rio 2016)',
        'time': 43.03,
        'segments': [10.77, 9.81, 10.48, 11.97],
    }

    # Mock 5: Went out way too fast
    too_fast = {
        'name': 'Mock: Too Fast Start',
        'time': 47.50,
        'segments': [10.80, 10.20, 12.00, 14.50],
    }

    for run in [vniekerk, too_fast]:
        result = s_analyzer.analyze_run(run['segments'], run['time'])
        s_analyzer.print_report(result, run['name'])
        safe_name = run['name'].replace(' ', '_').replace(':', '').replace('(', '').replace(')', '')
        s_analyzer.plot_report(result, run['name'],
                               save_path=os.path.join(DATA_DIR, f'report_400m_{safe_name}.png'))

    print("Done — all reports generated.")


if __name__ == '__main__':
    main()