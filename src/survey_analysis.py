"""
survey_analysis.py
==================
Descriptive statistical analysis of the BeSU ride-hailing survey data
(n = 60 college students, Bulacan State University).

This module reads data/survey_data_n60.csv and computes all summary
statistics referenced in the research paper, then saves them to:
  results/survey_summary_stats.csv
  results/survey_descriptive_report.txt

Run from the repo root:
    python src/survey_analysis.py
"""

import csv
import math
import os
from collections import Counter, OrderedDict


# ---------------------------------------------------------------------------
# 1.  DATA LOADING
# ---------------------------------------------------------------------------

DATA_PATH = "data/survey_data_n60.csv"


def load_data(path: str = DATA_PATH) -> tuple[list[dict], list[str]]:
    """
    Load the survey CSV.

    Returns
    -------
    (rows, fieldnames) : list of row dicts, list of column names
    """
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)
    print(f"  Loaded {len(rows)} responses from '{path}'")
    return rows, fieldnames


# ---------------------------------------------------------------------------
# 2.  HELPER STATISTICS
# ---------------------------------------------------------------------------

def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return math.sqrt(sum((v - m) ** 2 for v in values) / (len(values) - 1))


def median(values: list[float]) -> float:
    s = sorted(values)
    n = len(s)
    if n == 0:
        return 0.0
    mid = n // 2
    return (s[mid - 1] + s[mid]) / 2 if n % 2 == 0 else s[mid]


def freq_table(values: list) -> dict:
    """Return {value: count} ordered by frequency descending."""
    c = Counter(values)
    return OrderedDict(sorted(c.items(), key=lambda x: -x[1]))


def pct(count: int, total: int) -> str:
    return f"{count} ({count / total * 100:.1f}%)"


# ---------------------------------------------------------------------------
# 3.  ANALYSIS FUNCTIONS
# ---------------------------------------------------------------------------

def analyse_demographics(rows: list[dict], n: int) -> dict:
    """Compute frequency tables for all demographic variables."""
    return {
        "age":        freq_table(r["Age_Group"] for r in rows),
        "gender":     freq_table(r["Gender"] for r in rows),
        "year_level": freq_table(r["Year_Level"] for r in rows),
        "weekly_usage": freq_table(r["Weekly_Usage"] for r in rows),
    }


def analyse_usage(rows: list[dict], n: int) -> dict:
    """Platform preference, monthly trips, and derived demand estimate."""
    pref = freq_table(r["Preferred_Platform"] for r in rows)
    trips_raw = freq_table(r["Monthly_Trips"] for r in rows)

    # Midpoint mapping for average trip calculation
    midpoint = {"1-3": 2, "4-7": 5.5, "8-12": 10, "13-20": 16.5, ">20": 25}
    avg_trips = mean([midpoint[r["Monthly_Trips"]] for r in rows])

    joy  = pref.get("JoyRide", 0)
    move = pref.get("MoveIt", 0)
    duo_total = joy + move
    joy_duo_share  = joy  / duo_total if duo_total else 0
    move_duo_share = move / duo_total if duo_total else 0

    return {
        "preferred_platform": pref,
        "monthly_trips": trips_raw,
        "avg_trips_per_month": round(avg_trips, 2),
        "avg_trips_per_week": round(avg_trips / 4, 2),
        "joyride_duopoly_share_pct": round(joy_duo_share * 100, 1),
        "moveit_duopoly_share_pct":  round(move_duo_share * 100, 1),
        "estimated_daily_demand": round(avg_trips * 3600 / 30),
    }


def analyse_pricing(rows: list[dict], n: int) -> dict:
    """Willingness to pay, switching behaviour, scenario responses."""
    wtp = [float(r["Max_WTP"]) for r in rows]

    switch_20 = freq_table(r["Switch_20pct_Increase"] for r in rows)
    switch_low = [float(r["Switch_Likelihood_15-20_Lower"]) for r in rows]
    promo      = [float(r["Promo_Influence"]) for r in rows]
    sc1 = freq_table(r["Scenario_Joy70_Move50"] for r in rows)
    sc2 = freq_table(r["Scenario_All80_Angkas60"] for r in rows)

    leave_20 = (switch_20.get("Temp_switch", 0) +
                switch_20.get("Perm_switch", 0) +
                switch_20.get("Stop", 0))
    stay_20  = switch_20.get("Continue", 0) + switch_20.get("Reduce", 0)

    sc1_switch = (sc1.get("Switch_temp", 0) + sc1.get("Switch_perm", 0))
    sc1_stay   = sc1.get("Stay_Joy", 0)
    sc2_switch = sc2.get("Angkas", 0)
    sc2_stay   = sc2.get("Preferred", 0)

    return {
        "wtp_mean":    round(mean(wtp), 2),
        "wtp_median":  round(median(wtp), 2),
        "wtp_sd":      round(std(wtp), 2),
        "wtp_le_80_n": sum(1 for v in wtp if v <= 80),
        "wtp_gt_80_n": sum(1 for v in wtp if v > 80),
        "switch_on_20pct_increase": switch_20,
        "leave_on_20pct_pct": round(leave_20 / n * 100, 1),
        "stay_on_20pct_pct":  round(stay_20 / n * 100, 1),
        "switch_likelihood_mean": round(mean(switch_low), 2),
        "switch_likelihood_sd":   round(std(switch_low), 2),
        "switch_likely_pct":      round(sum(1 for v in switch_low if v >= 4) / n * 100, 1),
        "promo_influence_mean":   round(mean(promo), 2),
        "promo_influence_sd":     round(std(promo), 2),
        "promo_high_pct":         round(sum(1 for v in promo if v >= 4) / n * 100, 1),
        "scenario1_switch_n":  sc1_switch,
        "scenario1_switch_pct": round(sc1_switch / n * 100, 1),
        "scenario1_stay_n":    sc1_stay,
        "scenario1_stay_pct":  round(sc1_stay / n * 100, 1),
        "scenario2_switch_n":  sc2_switch,
        "scenario2_switch_pct": round(sc2_switch / n * 100, 1),
        "scenario2_stay_n":    sc2_stay,
        "scenario2_stay_pct":  round(sc2_stay / n * 100, 1),
    }


def analyse_perceptions(rows: list[dict], n: int) -> dict:
    """Mean and SD for affordability, safety, and price-vs-quality."""
    results = {}
    for platform in ["JoyRide", "MoveIt", "Angkas"]:
        afford = [float(r[f"Afford_{platform}"]) for r in rows]
        safety = [float(r[f"Safety_{platform}"]) for r in rows]
        results[f"afford_{platform.lower()}_mean"] = round(mean(afford), 2)
        results[f"afford_{platform.lower()}_sd"]   = round(std(afford),  2)
        results[f"safety_{platform.lower()}_mean"] = round(mean(safety), 2)
        results[f"safety_{platform.lower()}_sd"]   = round(std(safety),  2)

    pvq = [float(r["Price_vs_Quality"]) for r in rows]
    results["price_vs_quality_mean"] = round(mean(pvq), 2)
    results["price_vs_quality_sd"]   = round(std(pvq),  2)
    return results


# ---------------------------------------------------------------------------
# 4.  SAVE RESULTS
# ---------------------------------------------------------------------------

def save_summary_csv(stats: dict, path: str) -> None:
    """Save all flat key-value stats to CSV."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Value"])
        for k, v in stats.items():
            writer.writerow([k, v])
    print(f"  [saved] {path}")


def save_report(sections: list[str], path: str) -> None:
    """Save human-readable report to text file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(sections) + "\n")
    print(f"  [saved] {path}")


def build_report(n: int, demo: dict, usage: dict,
                 pricing: dict, perc: dict) -> list[str]:
    """Assemble a human-readable descriptive statistics report."""
    lines = [
        "=" * 60,
        "  BeSU RIDE-HAILING SURVEY — DESCRIPTIVE STATISTICS",
        f"  Sample size: n = {n}",
        "=" * 60,
        "",
        "--- 1. RESPONDENT PROFILE ---",
    ]

    for var, counts in demo.items():
        lines.append(f"\n  {var.upper().replace('_', ' ')}:")
        total = sum(counts.values())
        for cat, cnt in counts.items():
            lines.append(f"    {cat:<25} {pct(cnt, total)}")

    lines += [
        "",
        "--- 2. RIDE-HAILING USAGE ---",
        f"\n  Preferred Platform:",
    ]
    total_pref = sum(usage["preferred_platform"].values())
    for k, v in usage["preferred_platform"].items():
        lines.append(f"    {k:<20} {pct(v, total_pref)}")
    lines += [
        f"\n  Average monthly trips : {usage['avg_trips_per_month']}",
        f"  Average weekly trips  : {usage['avg_trips_per_week']}",
        f"  JoyRide duopoly share : {usage['joyride_duopoly_share_pct']}%",
        f"  MoveIt duopoly share  : {usage['moveit_duopoly_share_pct']}%",
        f"  Est. daily demand (Q0): {usage['estimated_daily_demand']} trips",
        "",
        "--- 3. PRICING SENSITIVITY ---",
        f"\n  WTP Mean   : ₱{pricing['wtp_mean']}  (SD = ₱{pricing['wtp_sd']})",
        f"  WTP Median : ₱{pricing['wtp_median']}",
        f"  WTP ≤ ₱80  : {pct(pricing['wtp_le_80_n'], n)}",
        f"  WTP > ₱80  : {pct(pricing['wtp_gt_80_n'], n)}",
        f"\n  On 20% fare increase — would switch/stop : {pricing['leave_on_20pct_pct']}%",
        f"  On 20% fare increase — would stay/reduce  : {pricing['stay_on_20pct_pct']}%",
        f"\n  Switch likelihood (₱15-20 lower) mean : {pricing['switch_likelihood_mean']}/5 "
        f"(SD={pricing['switch_likelihood_sd']})",
        f"  Likely/Very Likely (≥4)               : {pricing['switch_likely_pct']}%",
        f"\n  Promo influence mean                  : {pricing['promo_influence_mean']}/5 "
        f"(SD={pricing['promo_influence_sd']})",
        f"  High influence (≥4)                   : {pricing['promo_high_pct']}%",
        f"\n  Scenario 1 (₱70 vs ₱50, ~28% gap):",
        f"    Switch to MoveIt : {pct(pricing['scenario1_switch_n'], n)} "
        f"=> 68/32 split used in H vs D payoff cell",
        f"    Stay with JoyRide: {pct(pricing['scenario1_stay_n'], n)}",
        f"\n  Scenario 2 (₱80 vs ₱60, 25% gap):",
        f"    Switch to Angkas : {pct(pricing['scenario2_switch_n'], n)} "
        f"=> ~57/43 split (rounded to 60/40 for M vs D cell)",
        f"    Stay preferred   : {pct(pricing['scenario2_stay_n'], n)}",
        "",
        "--- 4. PLATFORM PERCEPTIONS ---",
        "",
        f"  {'Dimension':<35} {'JoyRide':>10} {'MoveIt':>10} {'Angkas':>10}",
        f"  {'-'*65}",
        f"  {'Affordability (mean/5)':<35} "
        f"{perc['afford_joyride_mean']:>10} "
        f"{perc['afford_moveit_mean']:>10} "
        f"{perc['afford_angkas_mean']:>10}",
        f"  {'Safety & Reliability (mean/5)':<35} "
        f"{perc['safety_joyride_mean']:>10} "
        f"{perc['safety_moveit_mean']:>10} "
        f"{perc['safety_angkas_mean']:>10}",
        f"\n  Price vs. Quality orientation : mean = {perc['price_vs_quality_mean']}/5 "
        f"(SD = {perc['price_vs_quality_sd']})",
        "",
        "=" * 60,
        "  END OF REPORT",
        "=" * 60,
    ]
    return lines


# ---------------------------------------------------------------------------
# 5.  MAIN
# ---------------------------------------------------------------------------

def main():
    print("\n" + "=" * 60)
    print("  SURVEY ANALYSIS — BeSU Ride-Hailing Study (n = 60)")
    print("=" * 60)

    rows, _ = load_data()
    n = len(rows)

    demo    = analyse_demographics(rows, n)
    usage   = analyse_usage(rows, n)
    pricing = analyse_pricing(rows, n)
    perc    = analyse_perceptions(rows, n)

    # Flat stats dict for CSV export
    flat_stats = {"n": n}
    for d in [usage, pricing, perc]:
        for k, v in d.items():
            if not isinstance(v, dict):
                flat_stats[k] = v

    report_lines = build_report(n, demo, usage, pricing, perc)
    for line in report_lines:
        print(line)

    print("\n--- Saving Results ---")
    save_summary_csv(flat_stats, "results/survey_summary_stats.csv")
    save_report(report_lines, "results/survey_descriptive_report.txt")
    print("\n[DONE] All survey results saved to results/")


if __name__ == "__main__":
    main()
