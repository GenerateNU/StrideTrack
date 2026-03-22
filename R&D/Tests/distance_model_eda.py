"""
train_tau_model.py
==================
Trains a finish_time → τ lookup model from published sprint split data.
Tests separately on held-out athletes.
Compares: combined model vs sex-specific models vs untrained baseline.

Data sources (all published, laser/video timed):
  - 2009 IAAF Berlin WC: Men's 100m final (Graubner & Nixdorf, New Studies in Athletics 2011)
  - 2017 IAAF London WC: Men's 100m final (Bissas et al., Leeds Beckett 2018)
  - 2017 IAAF London WC: Women's 100m final (Bissas et al., Leeds Beckett 2018)
  - 2009 IAAF Berlin WC: Women's 100m final (Graubner & Nixdorf, 2011)
  - 2012 IAAF Berlin WC: High school athletes (Jakalski / Freelap USA, 2013)
  - Synthesised sub-elite/recreational using published mean biomechanics
    (Morin et al. 2012, Samozino et al. 2016) for 11–15s finish time range.

Usage:
  python train_tau_model.py
"""

import math
import json
import random
import numpy as np
from dataclasses import dataclass

# ─── Core model (same as test_position_model.py) ─────────────────────────────

def dist(v, tau, t):
    return v * (t + tau * math.exp(-t / tau) - tau)

def invert_dist(v, tau, d, t_max=25.0):
    lo, hi = 0.0, t_max
    for _ in range(60):
        mid = (lo + hi) / 2
        if dist(v, tau, mid) < d:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2

def fit_tau_from_splits(finish_time, race_distance, split_times):
    """
    Fit the true τ for an athlete given their published split times.
    Uses the analytical constraint: for given τ, v_max = D / integral.
    Searches τ to minimise split prediction error.
    """
    def v_from_tau(tau):
        denom = finish_time + tau * math.exp(-finish_time / tau) - tau
        return race_distance / denom if denom > 0 else None

    def split_loss(tau):
        if tau <= 0:
            return 1e9
        v = v_from_tau(tau)
        if v is None or v <= 0:
            return 1e9
        loss = 0.0
        for d_split, t_split in split_times.items():
            pred_t = invert_dist(v, tau, d_split, finish_time * 2)
            loss += (pred_t - t_split) ** 2
        return loss

    best = (1e9, 1.5)
    for tau_try in np.arange(0.1, 8.0, 0.05):
        l = split_loss(tau_try)
        if l < best[0]:
            best = (l, tau_try)

    lo, hi = max(0.05, best[1] - 0.5), best[1] + 0.5
    for _ in range(80):
        m1 = lo + (hi - lo) * 0.382
        m2 = lo + (hi - lo) * 0.618
        if split_loss(m1) < split_loss(m2):
            hi = m2
        else:
            lo = m1
    tau = (lo + hi) / 2
    v = v_from_tau(tau)
    return tau, v


def predict_splits(finish_time, race_distance, tau):
    """Given finish time, distance, and tau, predict all intermediate splits."""
    denom = finish_time + tau * math.exp(-finish_time / tau) - tau
    v = race_distance / denom

    marks = [10 * i for i in range(1, int(race_distance / 10))]
    return {d: invert_dist(v, tau, d, finish_time * 2) for d in marks}


def rmse(pred, actual):
    pairs = [(p, a) for p, a in zip(pred, actual) if p is not None and a is not None]
    if not pairs:
        return float("nan")
    return math.sqrt(sum((p - a) ** 2 for p, a in pairs) / len(pairs))

def mae(pred, actual):
    pairs = [(p, a) for p, a in zip(pred, actual) if p is not None and a is not None]
    if not pairs:
        return float("nan")
    return sum(abs(p - a) for p, a in pairs) / len(pairs)


# ─── Dataset ─────────────────────────────────────────────────────────────────

@dataclass
class Athlete:
    name: str
    sex: str            # 'M' or 'F'
    finish_time: float  # from motion start (reaction subtracted)
    # 10m cumulative splits from motion start: {10: t, 20: t, ..., 90: t}
    splits: dict
    source: str
    level: str          # 'elite', 'subelite', 'highschool', 'recreational'


def build_dataset():
    athletes = []

    # ── 2017 WC MEN'S FINAL ────────────────────────────────────────────────
    # Source: Bissas et al. 2018 / IAAF flash report, laser timing
    # Reaction times subtracted. Interval splits → cumulative.
    wc17_men = [
        ("Gatlin",  "M", 0.138, [1.74,1.02,0.91,0.90,0.88,0.86,0.86,0.87,0.87,0.87], 9.92),
        ("Coleman", "M", 0.123, [1.75,1.00,0.90,0.88,0.87,0.86,0.88,0.88,0.88,0.92], 9.94),
        ("Bolt17",  "M", 0.183, [1.78,1.02,0.90,0.88,0.88,0.85,0.85,0.86,0.86,0.89], 9.95),
        ("Blake",   "M", 0.137, [1.74,1.02,0.91,0.90,0.89,0.88,0.87,0.88,0.87,0.89], 9.99),
        ("Simbine", "M", 0.141, [1.78,1.03,0.92,0.92,0.87,0.84,0.86,0.87,0.88,0.90], 10.01),
        ("Vicaut",  "M", 0.152, [1.80,1.03,0.90,0.89,0.87,0.87,0.88,0.89,0.90,0.90], 10.08),
        ("Prescod", "M", 0.145, [1.89,1.05,0.92,0.92,0.89,0.86,0.86,0.87,0.88,0.88], 10.17),
        ("Su",      "M", 0.224, [1.81,1.03,0.92,0.91,0.89,0.89,0.89,0.89,0.90,0.92], 10.27),
    ]
    for name, sex, rt, ivs, total in wc17_men:
        motion_ivs = [ivs[0] - rt] + list(ivs[1:])
        cum = {}
        t = 0.0
        for i, iv in enumerate(motion_ivs):
            t += iv
            cum[(i + 1) * 10] = round(t, 4)
        finish_motion = total - rt
        athletes.append(Athlete(
            name=name, sex=sex, finish_time=finish_motion,
            splits={k: v for k, v in cum.items() if k < 100},
            source="2017 WC London", level="elite"
        ))

    # ── 2009 WC BERLIN MEN'S FINAL ────────────────────────────────────────
    # Source: Graubner & Nixdorf, New Studies in Athletics 2011
    # Table 4: split times and reaction times
    wc09_men = [
        ("Bolt09",   "M", 0.146, [1.89,1.01,0.90,0.86,0.83,0.82,0.81,0.82,0.83,0.90], 9.58),
        ("Gay",      "M", 0.144, [1.83,1.02,0.90,0.87,0.85,0.83,0.83,0.85,0.87,0.92], 9.71),
        ("Powell",   "M", 0.134, [1.86,1.03,0.91,0.88,0.85,0.84,0.84,0.85,0.87,0.91], 9.84),
        ("Dix",      "M", 0.133, [1.85,1.03,0.92,0.89,0.87,0.85,0.85,0.86,0.88,0.93], 9.88),
        ("Thompson", "M", 0.138, [1.88,1.04,0.93,0.89,0.87,0.86,0.85,0.86,0.88,0.93], 9.93),
    ]
    for name, sex, rt, ivs, total in wc09_men:
        motion_ivs = [ivs[0] - rt] + list(ivs[1:])
        cum = {}
        t = 0.0
        for i, iv in enumerate(motion_ivs):
            t += iv
            cum[(i + 1) * 10] = round(t, 4)
        finish_motion = total - rt
        athletes.append(Athlete(
            name=name, sex=sex, finish_time=finish_motion,
            splits={k: v for k, v in cum.items() if k < 100},
            source="2009 WC Berlin", level="elite"
        ))

    # ── 2017 WC WOMEN'S FINAL ────────────────────────────────────────────
    # Source: Bissas et al. 2018, Leeds Beckett. Table 2.1 cumulative splits.
    # Reaction times from Table 2.1.
    wc17_women = [
        ("Bowie",      "F", 0.128, [1.86,2.92,3.91,4.87,5.77,6.66,7.56,8.45,9.63,10.85]),
        ("Ta_Lou",     "F", 0.132, [1.84,2.89,3.87,4.83,5.73,6.62,7.52,8.43,9.60,10.86]),
        ("Schippers",  "F", 0.155, [1.87,2.93,3.93,4.89,5.79,6.68,7.57,8.47,9.65,10.96]),
        ("Thompson",   "F", 0.131, [1.87,2.94,3.94,4.91,5.81,6.70,7.60,8.52,9.69,10.98]),
        ("Asher_Smith","F", 0.133, [1.88,2.95,3.96,4.93,5.83,6.73,7.63,8.54,9.72,11.02]),
    ]
    for name, sex, rt, cum_from_gun in wc17_women:
        finish_motion = cum_from_gun[-1] - rt
        cum_motion = {(i + 1) * 10: round(t - rt, 4) for i, t in enumerate(cum_from_gun)}
        athletes.append(Athlete(
            name=name, sex=sex, finish_time=finish_motion,
            splits={k: v for k, v in cum_motion.items() if k < 100},
            source="2017 WC London", level="elite"
        ))

    # ── 2009 WC BERLIN WOMEN'S FINAL ────────────────────────────────────
    # Source: Graubner & Nixdorf 2011, Table 11.
    wc09_women = [
        ("Fraser09",   "F", 0.146, [1.81,2.85,3.82,4.77,5.68,6.59,7.50,8.42,9.58,10.73]),
        ("Campbell",   "F", 0.148, [1.83,2.88,3.86,4.82,5.73,6.64,7.55,8.47,9.63,10.76]),
        ("Jeter",      "F", 0.164, [1.84,2.89,3.88,4.84,5.75,6.66,7.57,8.49,9.65,10.90]),
        ("Sturrup",    "F", 0.150, [1.85,2.91,3.91,4.88,5.79,6.70,7.62,8.55,9.73,10.98]),
    ]
    for name, sex, rt, cum_from_gun in wc09_women:
        finish_motion = cum_from_gun[-1] - rt
        cum_motion = {(i + 1) * 10: round(t - rt, 4) for i, t in enumerate(cum_from_gun)}
        athletes.append(Athlete(
            name=name, sex=sex, finish_time=finish_motion,
            splits={k: v for k, v in cum_motion.items() if k < 100},
            source="2009 WC Berlin", level="elite"
        ))

    # ── HIGH SCHOOL ATHLETES (Male) ───────────────────────────────────────
    # Source: Jakalski / Freelap USA 2012, Carlin Nalley Invitational.
    # Note: first 10m split appears to include timing setup offset —
    # we use 10-90m only for tau fitting, consistent with other sources.
    hs_men = [
        ("HS_M1", "M", [1.98,1.16,1.06,0.99,0.96,1.01,1.03,0.97,1.02,1.03], 11.21),
        ("HS_M2", "M", [1.79,1.21,1.10,1.04,1.03,1.06,1.08,1.03,1.12,1.17], 11.63),
    ]
    for name, sex, ivs, total in hs_men:
        # No reaction time published — assume 0.15s typical
        rt = 0.15
        motion_ivs = [ivs[0] - rt] + list(ivs[1:])
        cum = {}
        t = 0.0
        for i, iv in enumerate(motion_ivs):
            t += iv
            cum[(i + 1) * 10] = round(t, 4)
        athletes.append(Athlete(
            name=name, sex=sex, finish_time=total - rt,
            splits={k: v for k, v in cum.items() if k < 100},
            source="2012 HS Invitational", level="highschool"
        ))

    # ── SYNTHESISED SUB-ELITE / RECREATIONAL ─────────────────────────────
    # Source: Morin et al. (2012) studied 13 subjects ranging from non-specialists
    # (100m ~15s) to national-level sprinters (100m ~10.35s).
    # Samozino et al. published τ distributions for trained non-sprinters.
    # We construct representative split profiles for finish times 11.5–15.0s
    # using the known scaling relationships:
    #   - Slower runners have longer GCT, lower v_max, higher τ
    #   - Female recreational ~10% slower than male at same training level
    #   - The acceleration phase spans a larger fraction of the race at slower speeds
    #
    # Method: for each synthetic athlete, specify the 10m interval pattern
    # consistent with their finish time and published τ ranges for that level.

    synthetic = [
        # name, sex, finish_gun, rt, interval_pattern
        # Sub-elite men (11.0–11.5s)
        ("SubElM_110", "M", 11.0, 0.16, [2.00,1.17,1.06,1.02,0.99,0.98,0.97,0.98,0.99,1.01]),
        ("SubElM_115", "M", 11.5, 0.16, [2.06,1.22,1.11,1.07,1.04,1.03,1.02,1.03,1.05,1.07]),
        # Collegiate men (11.5–12.5s)
        ("ColM_120",   "M", 12.0, 0.17, [2.14,1.28,1.16,1.11,1.08,1.07,1.07,1.08,1.11,1.12]),
        ("ColM_125",   "M", 12.5, 0.17, [2.20,1.34,1.22,1.17,1.14,1.13,1.13,1.14,1.16,1.18]),
        ("ColM_130",   "M", 13.0, 0.17, [2.27,1.40,1.28,1.23,1.20,1.19,1.19,1.20,1.22,1.24]),
        # Recreational men (13.5–15.0s)
        ("RecM_135",   "M", 13.5, 0.18, [2.35,1.47,1.35,1.30,1.27,1.26,1.26,1.27,1.29,1.31]),
        ("RecM_140",   "M", 14.0, 0.18, [2.44,1.54,1.41,1.36,1.33,1.32,1.32,1.33,1.36,1.38]),
        ("RecM_150",   "M", 15.0, 0.18, [2.62,1.68,1.54,1.49,1.46,1.44,1.44,1.45,1.48,1.52]),
        # Sub-elite women (11.5–12.0s)
        ("SubElF_115", "F", 11.5, 0.15, [2.06,1.22,1.10,1.06,1.03,1.02,1.02,1.03,1.07,1.11]),
        ("SubElF_120", "F", 12.0, 0.15, [2.14,1.28,1.16,1.12,1.09,1.08,1.09,1.10,1.13,1.17]),
        # Collegiate women
        ("ColF_125",   "F", 12.5, 0.16, [2.22,1.35,1.23,1.19,1.16,1.15,1.15,1.16,1.20,1.24]),
        ("ColF_130",   "F", 13.0, 0.16, [2.30,1.42,1.30,1.25,1.22,1.21,1.21,1.23,1.27,1.31]),
        ("ColF_135",   "F", 13.5, 0.17, [2.38,1.49,1.37,1.32,1.29,1.28,1.28,1.29,1.33,1.38]),
        # Recreational women
        ("RecF_140",   "F", 14.0, 0.17, [2.47,1.57,1.44,1.39,1.36,1.35,1.35,1.36,1.40,1.44]),
        ("RecF_150",   "F", 15.0, 0.18, [2.65,1.72,1.58,1.53,1.50,1.49,1.49,1.50,1.54,1.59]),
        ("RecF_160",   "F", 16.0, 0.18, [2.85,1.88,1.73,1.68,1.64,1.63,1.63,1.64,1.69,1.75]),
    ]
    for name, sex, total, rt, ivs in synthetic:
        motion_ivs = [ivs[0] - rt] + list(ivs[1:])
        cum = {}
        t = 0.0
        for i, iv in enumerate(motion_ivs):
            t += iv
            cum[(i + 1) * 10] = round(t, 4)
        athletes.append(Athlete(
            name=name, sex=sex, finish_time=total - rt,
            splits={k: v for k, v in cum.items() if k < 100},
            source="Synthesised (Morin 2012 / Samozino 2016)", level="recreational"
        ))

    return athletes


# ─── Training ────────────────────────────────────────────────────────────────

def extract_tau(athlete):
    """Fit true τ from an athlete's published splits."""
    tau, v = fit_tau_from_splits(
        athlete.finish_time, 100.0, athlete.splits
    )
    return tau


def train_tau_model(athletes):
    """
    Fit a piecewise linear τ(finish_time) model from training data.
    Returns a callable: tau_predict(finish_time, sex='M'|'F'|'combined')
    """
    records_m, records_f = [], []
    for a in athletes:
        tau = extract_tau(a)
        if 0.1 < tau < 10.0:
            if a.sex == "M":
                records_m.append((a.finish_time, tau))
            else:
                records_f.append((a.finish_time, tau))

    def fit_linear(records):
        xs = np.array([r[0] for r in records])
        ys = np.array([r[1] for r in records])
        coeffs = np.polyfit(xs, ys, 1)
        return coeffs  # [slope, intercept]

    coeffs_m = fit_linear(records_m)
    coeffs_f = fit_linear(records_f)
    coeffs_combined = fit_linear(records_m + records_f)

    return {
        "M": coeffs_m,
        "F": coeffs_f,
        "combined": coeffs_combined,
        "training_data_m": records_m,
        "training_data_f": records_f,
    }


def predict_tau(finish_time, model, sex="combined"):
    coeffs = model[sex]
    return float(np.polyval(coeffs, finish_time))


# ─── Evaluation ──────────────────────────────────────────────────────────────

def evaluate(test_athletes, model, sex_key):
    """
    Given a set of test athletes and a trained model, compute quarter split
    accuracy using the predicted τ vs the baseline (τ=1.5 for everyone).
    """
    results = []
    for a in test_athletes:
        # Predicted τ from model
        tau_pred = predict_tau(a.finish_time, model, sex_key)
        tau_pred = max(0.2, min(tau_pred, 8.0))

        # True τ from published splits
        tau_true, _ = fit_tau_from_splits(a.finish_time, 100.0, a.splits)

        # Baseline τ: untrained (constant 1.5)
        tau_baseline = 1.5

        # Evaluate quarter splits: 25m, 50m, 75m
        q_marks = [25.0, 50.0, 75.0]
        errs_pred, errs_base = [], []
        for d in q_marks:
            # True time at d from published splits (interpolate)
            lower = int(d // 10) * 10
            upper = lower + 10
            frac = (d - lower) / 10.0
            t_low = a.splits.get(lower, 0.0)
            t_high = a.splits.get(upper, a.finish_time if upper >= 100 else None)
            if t_low is None or t_high is None:
                continue
            t_true = t_low + frac * (t_high - t_low)

            # Predicted model time at d
            denom_pred = a.finish_time + tau_pred * math.exp(-a.finish_time / tau_pred) - tau_pred
            v_pred = 100.0 / denom_pred
            t_pred = invert_dist(v_pred, tau_pred, d, a.finish_time * 2)
            errs_pred.append(abs(t_pred - t_true))

            # Baseline time at d
            denom_base = a.finish_time + tau_baseline * math.exp(-a.finish_time / tau_baseline) - tau_baseline
            v_base = 100.0 / denom_base
            t_base = invert_dist(v_base, tau_baseline, d, a.finish_time * 2)
            errs_base.append(abs(t_base - t_true))

        if errs_pred:
            results.append({
                "name": a.name,
                "sex": a.sex,
                "finish": a.finish_time + 0.15,  # approx gun time for display
                "level": a.level,
                "tau_true": tau_true,
                "tau_pred": tau_pred,
                "mae_pred": sum(errs_pred) / len(errs_pred),
                "mae_base": sum(errs_base) / len(errs_base),
                "max_pred": max(errs_pred),
                "max_base": max(errs_base),
            })
    return results


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    random.seed(42)

    all_athletes = build_dataset()
    print(f"Total athletes in dataset: {len(all_athletes)}")
    for level in ["elite", "highschool", "recreational"]:
        n = sum(1 for a in all_athletes if a.level == level)
        nm = sum(1 for a in all_athletes if a.level == level and a.sex == "M")
        nf = sum(1 for a in all_athletes if a.level == level and a.sex == "F")
        print(f"  {level:12s}: {n:2d} total  (M={nm}, F={nf})")

    # ── Train / test split: 80/20, stratified by sex ──────────────────────
    men   = [a for a in all_athletes if a.sex == "M"]
    women = [a for a in all_athletes if a.sex == "F"]
    random.shuffle(men)
    random.shuffle(women)

    n_train_m = int(len(men) * 0.8)
    n_train_f = int(len(women) * 0.8)
    train = men[:n_train_m] + women[:n_train_f]
    test  = men[n_train_m:] + women[n_train_f:]

    print(f"\nTrain: {len(train)} athletes  |  Test: {len(test)} athletes")
    print(f"  Train: M={sum(1 for a in train if a.sex=='M')}  F={sum(1 for a in train if a.sex=='F')}")
    print(f"  Test:  M={sum(1 for a in test  if a.sex=='M')}  F={sum(1 for a in test  if a.sex=='F')}")

    # ── Train ─────────────────────────────────────────────────────────────
    model = train_tau_model(train)

    print(f"\nTrained τ models:")
    print(f"  Male:     τ = {model['M'][0]:+.4f} × finish_time  {model['M'][1]:+.4f}")
    print(f"  Female:   τ = {model['F'][0]:+.4f} × finish_time  {model['F'][1]:+.4f}")
    print(f"  Combined: τ = {model['combined'][0]:+.4f} × finish_time  {model['combined'][1]:+.4f}")

    # ── Evaluate ───────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("TEST SET RESULTS")
    print("=" * 70)

    for label, key in [("Combined model", "combined"), ("Sex-specific model", None), ("Baseline (τ=1.5)", "baseline")]:
        all_mae_pred, all_mae_base, all_max_pred = [], [], []

        for a in test:
            sex_key = (a.sex if key is None else key)

            if key == "baseline":
                tau_use = 1.5
            else:
                tau_use = predict_tau(a.finish_time, model, sex_key)
                tau_use = max(0.2, min(tau_use, 8.0))

            q_marks = [25.0, 50.0, 75.0]
            errs = []
            for d in q_marks:
                lower = int(d // 10) * 10
                upper = lower + 10
                frac = (d - lower) / 10.0
                t_low  = a.splits.get(lower, 0.0)
                t_high = a.splits.get(upper)
                if t_high is None:
                    continue
                t_true = t_low + frac * (t_high - t_low)
                denom = a.finish_time + tau_use * math.exp(-a.finish_time / tau_use) - tau_use
                v = 100.0 / denom
                t_pred = invert_dist(v, tau_use, d, a.finish_time * 2)
                errs.append(abs(t_pred - t_true))

            if errs:
                all_mae_pred.append(sum(errs) / len(errs))
                all_max_pred.append(max(errs))

        print(f"\n  {label}:")
        print(f"    Quarter split MAE:  {sum(all_mae_pred)/len(all_mae_pred):.4f}s")
        print(f"    Quarter split max:  {max(all_max_pred):.4f}s")
        within_10 = sum(1 for e in all_mae_pred if e <= 0.10)
        within_20 = sum(1 for e in all_mae_pred if e <= 0.20)
        print(f"    Athletes within 0.10s MAE: {within_10}/{len(all_mae_pred)}")
        print(f"    Athletes within 0.20s MAE: {within_20}/{len(all_mae_pred)}")

    # ── Per-athlete detail ────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("PER-ATHLETE TEST RESULTS (sex-specific model)")
    print("=" * 70)
    print(f"  {'Name':18s} {'Sex'} {'~Time':>6s} {'Level':12s} {'τ_true':>7s} {'τ_pred':>7s} {'MAE_model':>10s} {'MAE_base':>9s}")
    print(f"  {'─'*80}")

    for a in sorted(test, key=lambda x: x.finish_time):
        sex_key = a.sex
        tau_pred = max(0.2, min(predict_tau(a.finish_time, model, sex_key), 8.0))
        tau_true, _ = fit_tau_from_splits(a.finish_time, 100.0, a.splits)

        errs_model, errs_base = [], []
        for d in [25.0, 50.0, 75.0]:
            lower = int(d // 10) * 10
            upper = lower + 10
            frac = (d - lower) / 10.0
            t_low  = a.splits.get(lower, 0.0)
            t_high = a.splits.get(upper)
            if t_high is None:
                continue
            t_true = t_low + frac * (t_high - t_low)
            for tau_use, err_list in [(tau_pred, errs_model), (1.5, errs_base)]:
                denom = a.finish_time + tau_use * math.exp(-a.finish_time / tau_use) - tau_use
                v = 100.0 / denom
                t_p = invert_dist(v, tau_use, d, a.finish_time * 2)
                err_list.append(abs(t_p - t_true))

        mae_m = sum(errs_model) / len(errs_model) if errs_model else float("nan")
        mae_b = sum(errs_base)  / len(errs_base)  if errs_base  else float("nan")
        improvement = "↑" if mae_m < mae_b else "↓"
        gun_approx = a.finish_time + 0.15
        print(f"  {a.name:18s} {a.sex:3s} {gun_approx:>6.2f}s {a.level:12s} {tau_true:>7.3f}  {tau_pred:>7.3f}  {mae_m:>9.4f}s  {mae_b:>8.4f}s {improvement}")