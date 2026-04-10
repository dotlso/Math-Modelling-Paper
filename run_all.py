"""
run_all.py
==========
Master script — runs the full analysis pipeline in order:

    Step 1: Survey descriptive statistics   (src/survey_analysis.py)
    Step 2: Payoff matrix construction      (src/payoff_matrix.py)
    Step 3: Generate all figures            (src/visualizations/visualizations.py)

Run from the repo root:
    python run_all.py

All outputs are saved to results/.
"""

import sys
import os

# Ensure src/ is on the import path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src", "visualizations"))


def step(number: int, description: str) -> None:
    print(f"\n{'='*60}")
    print(f"  STEP {number}: {description}")
    print(f"{'='*60}")


def main():
    print("\n" + "#" * 60)
    print("#  GAME-THEORETIC FARE COMPETITION MODEL")
    print("#  JoyRide vs. MoveIt — Malolos City")
    print("#  Bulacan State University | n = 60 BeSU Students")
    print("#" * 60)

    os.makedirs("results", exist_ok=True)

    # ── Step 1: Survey analysis ──────────────────────────────────────────────
    step(1, "Survey Descriptive Statistics")
    try:
        import survey_analysis
        survey_analysis.main()
    except Exception as e:
        print(f"  [ERROR] Survey analysis failed: {e}")
        raise

    # ── Step 2: Payoff matrix & Nash equilibria ──────────────────────────────
    step(2, "Payoff Matrix Construction & Nash Equilibrium Analysis")
    try:
        import payoff_matrix
        payoff_matrix.main()
    except Exception as e:
        print(f"  [ERROR] Payoff matrix failed: {e}")
        raise

    # ── Step 3: Visualizations ───────────────────────────────────────────────
    step(3, "Generating All Figures")
    try:
        import visualizations
        visualizations.main()
    except Exception as e:
        print(f"  [ERROR] Visualizations failed: {e}")
        raise

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "#" * 60)
    print("#  PIPELINE COMPLETE")
    print("#  Check the results/ folder for all outputs:")
    outputs = [
        "results/survey_summary_stats.csv",
        "results/survey_descriptive_report.txt",
        "results/payoff_matrix.csv",
        "results/equilibrium_summary.csv",
        "results/dominance_analysis.txt",
        "results/mixed_strategy.txt",
        "results/figure1_payoff_bar_chart.png",
        "results/figure2_platform_preference.png",
        "results/figure3_wtp_histogram.png",
        "results/figure4_perception_bars.png",
        "results/figure5_switching_behaviour.png",
        "results/figure6_payoff_heatmap.png",
    ]
    for f in outputs:
        status = "[OK]" if os.path.exists(f) else "[MISSING]"
        print(f"#  {status}  {f}")
    print("#" * 60 + "\n")


if __name__ == "__main__":
    main()
