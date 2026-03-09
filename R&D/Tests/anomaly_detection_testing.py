"""
StrideTrack R&D: Anomaly Detection in 400mH & 400m Sprint
Uses autoencoder (sklearn MLPRegressor) trained on Athletes First data
to detect abnormal race pacing patterns via reconstruction error.
"""

import re, os, subprocess, tempfile
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "data")

sns.set_theme(style="whitegrid")

# ── 1. PARSING ──────────────────────────────────────────────

def parse_400mh(filepath):
    """Parse 400mH touchdown times from pdftotext output."""
    with open(filepath) as f:
        lines = f.readlines()

    races, athlete = [], ""
    for i, line in enumerate(lines):
        s = line.strip()

        # Athlete header
        m = re.match(r'^(.+?)\s*\([A-Z]{3}\)', s)
        if m and re.search(r'\(\d{4}\)', s) and 'H1' in s:
            athlete = m.group(1).strip()

        # Touchdown times line
        if not re.match(r'^\s*date\s', line):
            continue
        nums = []
        for p in s.split()[2:]:
            try: nums.append(float(p))
            except ValueError:
                if '/' in p: break

        if len(nums) < 11:
            continue

        # Handle optional 200m split (11 nums = no 200m, 12+ = has 200m)
        td, time = None, None
        if len(nums) == 11:
            td, time = nums[:10], nums[10]
        else:
            for skip in [5, 6]:
                c = nums[:skip] + nums[skip+1:]
                if len(c) >= 11 and all(c[j] < c[j+1] for j in range(10)):
                    td, time = c[:10], c[10]
                    break

        if not (td and time and 44 < time < 65):
            continue
        if not all(td[j] < td[j+1] for j in range(9)):
            continue

        # Compute intervals from cumulative touchdowns
        intervals = [td[0]] + [round(td[j]-td[j-1], 3) for j in range(1, 10)]
        intervals.append(round(time - td[9], 3))  # run-in

        if all(1.0 < iv < 10.0 for iv in intervals):
            races.append({'athlete': athlete, 'time': time, 'intervals': intervals})

    return races


def parse_400m(filepath):
    """Parse 400m split times from pdftotext output."""
    with open(filepath) as f:
        lines = f.readlines()

    races, athlete = [], ""
    for i, line in enumerate(lines):
        s = line.strip()

        m = re.match(r'^(.+?)\s*\([A-Z]{3}\)', s)
        if m and re.search(r'\(\d{4}\)', s) and '100m' in s:
            athlete = m.group(1).strip()

        if not re.match(r'^\s*date\s', line):
            continue
        nums = []
        for p in s.split()[2:]:
            try: nums.append(float(p))
            except ValueError:
                if '/' in p: break

        official = next((n for n in nums if 43 < n < 60), None)
        if not official:
            continue

        # Find interval line (next 1-2 lines)
        inums = []
        for off in [1, 2]:
            if i + off < len(lines) and 'interval' in lines[i+off]:
                for p in lines[i+off].split():
                    try: inums.append(float(p))
                    except ValueError: continue
                break

        # Try deriving 100m splits from cumulative times
        cum = [n for n in nums if n < official]
        splits = None

        if len(cum) >= 8:  # 50m granularity
            splits = [cum[1], cum[3]-cum[1], cum[5]-cum[3], official-cum[5]]
        elif len(cum) == 4:  # 100m granularity
            splits = [cum[0], cum[1]-cum[0], cum[2]-cum[1], official-cum[2]]
        elif len(cum) == 3 and cum[0] < 15:
            splits = [cum[0], cum[1]-cum[0], cum[2]-cum[1], official-cum[2]]

        # Fallback: find 4 values in interval line that sum to official
        if not splits and len(inums) >= 4:
            for start in range(len(inums) - 3):
                c = inums[start:start+4]
                if abs(sum(c) - official) < 0.5:
                    splits = c
                    break

        if splits and len(splits) == 4 and all(8 < s < 15 for s in splits):
            races.append({'athlete': athlete, 'time': official,
                         'splits': [round(s, 2) for s in splits]})

    return races


# ── 2. AUTOENCODER (sklearn MLPRegressor as identity-mapping NN) ──

def train_autoencoder(X, hidden_layers, epochs=500):
    """
    Train an autoencoder by teaching an MLP to reconstruct its own input.
    The bottleneck layer forces it to learn a compressed representation.
    """
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_val = train_test_split(X_scaled, test_size=0.2, random_state=42)

    ae = MLPRegressor(
        hidden_layer_sizes=hidden_layers,
        activation='relu',
        solver='adam',
        max_iter=epochs,
        learning_rate_init=0.001,
        early_stopping=True,
        validation_fraction=0.15,
        random_state=42,
        verbose=False,
    )
    ae.fit(X_train, X_train)  # Target = Input (autoencoder)

    # Reconstruction error on full dataset
    reconstructed = ae.predict(X_scaled)
    per_feature_err = (X_scaled - reconstructed) ** 2
    per_sample_err = per_feature_err.mean(axis=1)

    threshold = np.percentile(per_sample_err, 95)

    return {
        'model': ae, 'scaler': scaler,
        'reconstructed': scaler.inverse_transform(reconstructed),
        'per_sample_err': per_sample_err,
        'per_feature_err': per_feature_err,
        'threshold': threshold,
        'is_anomaly': per_sample_err > threshold,
    }


# ── 3. VISUALIZATION ──────────────────────────────────────

def plot_overview(normalized, res, labels, event, times, athletes):
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f"Anomaly Detection: Men's {event}", fontsize=15, fontweight='bold')

    # Error distribution
    ax = axes[0, 0]
    ax.hist(res['per_sample_err'], bins=50, color='steelblue', edgecolor='white', alpha=0.8)
    ax.axvline(res['threshold'], color='red', ls='--', lw=2, label='95th pct threshold')
    ax.set_xlabel('Reconstruction Error'); ax.set_ylabel('Count')
    ax.set_title('Reconstruction Error Distribution'); ax.legend()

    # Normal vs anomalous profiles
    ax = axes[0, 1]
    x = np.arange(len(labels))
    norm_mean = normalized[~res['is_anomaly']].mean(0)
    anom_mean = normalized[res['is_anomaly']].mean(0)
    ax.bar(x - 0.2, norm_mean, 0.4, label='Normal', color='steelblue', alpha=0.8)
    ax.bar(x + 0.2, anom_mean, 0.4, label='Anomalous', color='tomato', alpha=0.8)
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('% of Total Time'); ax.set_title('Pacing Profiles'); ax.legend()

    # Which segments drive anomalies
    ax = axes[1, 0]
    seg_err = res['per_feature_err'][res['is_anomaly']].mean(0)
    colors = plt.cm.YlOrRd(seg_err / seg_err.max())
    ax.bar(range(len(labels)), seg_err, color=colors, edgecolor='gray')
    ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Mean Squared Error'); ax.set_title('Which Segments Drive Anomalies?')

    # Top anomalies heatmap
    ax = axes[1, 1]
    top = np.argsort(res['per_sample_err'])[-15:][::-1]
    im = ax.imshow(res['per_feature_err'][top], aspect='auto', cmap='YlOrRd')
    ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels([f"{athletes[i][:20]} ({times[i]:.1f}s)" for i in top], fontsize=7)
    ax.set_title('Top 15 Anomalies by Segment'); plt.colorbar(im, ax=ax)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, f'{event}_overview.png'), dpi=150, bbox_inches='tight')
    plt.close()


def plot_coaching_demo(normalized, res, labels, athletes, times):
    """Show individual anomalous races with per-segment color coding."""
    anomaly_idx = np.where(res['is_anomaly'])[0]
    sorted_anom = anomaly_idx[np.argsort(res['per_sample_err'][anomaly_idx])[::-1]]

    # Pick 6 unique athletes
    selected, seen = [], set()
    for idx in sorted_anom:
        if athletes[idx] not in seen and len(selected) < 6:
            selected.append(idx)
            seen.add(athletes[idx])

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle("400mH Coaching Demo: Flagging Anomalous Race Segments",
                 fontsize=14, fontweight='bold')

    seg_mean = res['per_feature_err'].mean(0)
    seg_std = res['per_feature_err'].std(0)

    for pi, ri in enumerate(selected):
        ax = axes[pi // 3, pi % 3]
        actual = normalized[ri]
        expected = res['reconstructed'][ri]

        # Color by severity (z-score of per-feature error)
        z = (res['per_feature_err'][ri] - seg_mean) / (seg_std + 1e-8)
        colors = ['red' if v > 2 else 'orange' if v > 1 else 'steelblue' for v in z]

        x = np.arange(len(labels))
        ax.bar(x, actual, color=colors, alpha=0.85, edgecolor='gray')
        ax.plot(x, expected, 'k--', lw=2, marker='o', ms=4, label='Expected')
        worst = labels[np.argmax(z)]
        ax.set_title(f"{athletes[ri][:25]} ({times[ri]:.2f}s)\n⚠ {worst}", fontsize=9)
        ax.set_xticks(x); ax.set_xticklabels(labels, rotation=55, ha='right', fontsize=7)
        ax.set_ylabel('% of Total Time')
        if pi == 0: ax.legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'coaching_demo.png'), dpi=150, bbox_inches='tight')
    plt.close()


# ── 4. MAIN ───────────────────────────────────────────────

def pdf_to_text(pdf_path):
    """Convert PDF to text using pdftotext (requires poppler-utils)."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(script_dir, pdf_path)
    txt_path = os.path.join(tempfile.gettempdir(), os.path.basename(pdf_path) + '.txt')
    subprocess.run(['pdftotext', '-layout', pdf_path, txt_path], check=True)
    return txt_path


def main():
    print("Parsing PDFs...")
    h_races = parse_400mh(pdf_to_text("data/AthletesFirst_400H.pdf"))
    s_races = parse_400m(pdf_to_text("data/AthletesFirst_400S.pdf"))
    print(f"  400mH: {len(h_races)} races  |  400m: {len(s_races)} races")

    # Build matrices
    h_data = np.array([r['intervals'] for r in h_races])
    h_times = np.array([r['time'] for r in h_races])
    h_athletes = [r['athlete'] for r in h_races]
    h_labels = ['Start→H1'] + [f'H{i}→H{i+1}' for i in range(1, 10)] + ['H10→Fin']

    s_data = np.array([r['splits'] for r in s_races])
    s_times = np.array([r['time'] for r in s_races])
    s_athletes = [r['athlete'] for r in s_races]
    s_labels = ['0-100m', '100-200m', '200-300m', '300-400m']

    for name, data, times, athletes, labels, hidden in [
        ('400mH', h_data, h_times, h_athletes, h_labels, (8, 4, 8)),
        ('400m',  s_data, s_times, s_athletes, s_labels, (8, 3, 8)),
    ]:
        print(f"\n── {name} ──")
        normalized = data / times[:, None] * 100
        print(f"  Mean split profile: {np.round(normalized.mean(0), 2)}")

        res = train_autoencoder(normalized, hidden)
        print(f"  Threshold: {res['threshold']:.4f}")
        print(f"  Anomalies: {res['is_anomaly'].sum()} / {len(data)}")

        # Top anomalies
        top = np.argsort(res['per_sample_err'])[-5:][::-1]
        for idx in top:
            worst_seg = labels[np.argmax(res['per_feature_err'][idx])]
            print(f"    {athletes[idx][:25]:25s} {times[idx]:.2f}s  ⚠ {worst_seg}")

        plot_overview(normalized, res, labels, name, times, athletes)
        if name == '400mH':
            plot_coaching_demo(normalized, res, labels, athletes, times)

    print("\nDone — visualizations saved.")


if __name__ == '__main__':
    main()