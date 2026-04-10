"""
visualizations.py
=================
Generates all plots used in the research paper:

  Figure 1 — Payoff Bar Chart (all 9 strategy profiles)
  Figure 2 — Platform Preference Pie Chart (n = 60)
  Figure 3 — WTP Distribution Histogram
  Figure 4 — Perception Radar Chart (affordability & safety)
  Figure 5 — Switching Behaviour Stacked Bar
  Figure 6 — Heatmap of Firm A Payoffs (3x3 matrix)

All figures are saved to results/ as high-resolution PNG files.

Run from repo root:
    python src/visualizations.py

Dependencies: matplotlib, numpy  (see requirements.txt)
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")          # non-interactive backend — safe for servers
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import csv
import math

# Try to import survey data (needed for Figures 2, 3, 4, 5)
DATA_PATH = "data/survey_data_n60.csv"
RESULTS_DIR = "results"

# ── colour palette ────────────────────────────────────────────────────────────
C_JOYRIDE = "#1A6BAA"    # blue
C_MOVEIT  = "#E05A2B"    # orange-red
C_ANGKAS  = "#2C9E44"    # green
C_HIGH    = "#2F5496"    # dark blue
C_MED     = "#4472C4"    # medium blue
C_DISC    = "#9DC3E6"    # light blue
C_NE      = "#FFC000"    # golden — Nash equilibrium highlight
C_BG      = "#F8F9FA"
C_GRID    = "#DEE2E6"

STRATEGY_LABELS = ["High (H)", "Medium (M)", "Discounted (D)"]


# ---------------------------------------------------------------------------
# helper: load survey data
# ---------------------------------------------------------------------------
def load_survey(path: str = DATA_PATH) -> list[dict]:
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


def savefig(fig, name: str) -> None:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [saved] {path}")


# ---------------------------------------------------------------------------
# FIGURE 1 — Payoff Bar Chart (all 9 strategy profiles)
# ---------------------------------------------------------------------------
def fig1_payoff_bar_chart() -> None:
    """
    Grouped bar chart comparing π_A and π_B across all 9 strategy profiles.
    Nash equilibrium profiles (H,M) and (M,H) are highlighted.
    """
    # Payoff values (from payoff_matrix.py output)
    profiles = ["(H,H)", "(H,M)", "(H,D)", "(M,H)", "(M,M)",
                "(M,D)", "(D,H)", "(D,M)", "(D,D)"]
    pi_A = [23400, 25200, 22272, 25200, 20000, 17600, 15776, 13200, 12400]
    pi_B = [23400, 25200, 15776, 25200, 20000, 13200, 22272, 17600, 12400]
    ne_idx = [1, 3]     # (H,M) and (M,H) are Nash equilibria

    x   = np.arange(len(profiles))
    w   = 0.35

    fig, ax = plt.subplots(figsize=(12, 6), facecolor=C_BG)
    ax.set_facecolor(C_BG)

    bars_A = ax.bar(x - w/2, pi_A, w, label="JoyRide (Firm A)",
                    color=C_JOYRIDE, edgecolor="white", linewidth=0.8, zorder=3)
    bars_B = ax.bar(x + w/2, pi_B, w, label="MoveIt (Firm B)",
                    color=C_MOVEIT,  edgecolor="white", linewidth=0.8, zorder=3)

    # Highlight Nash equilibrium profiles
    for idx in ne_idx:
        ax.axvspan(idx - 0.55, idx + 0.55, color=C_NE, alpha=0.25, zorder=1)
        ax.text(idx, 26800, "NE", ha="center", va="bottom",
                fontsize=9, fontweight="bold", color="#996600")

    # Equilibrium reference line
    ax.axhline(25200, color=C_NE, linewidth=1.5, linestyle="--",
               label="NE payoff = 25,200", zorder=2)

    ax.set_xticks(x)
    ax.set_xticklabels(profiles, fontsize=10)
    ax.set_ylabel("Profit (arbitrary units / period)", fontsize=11)
    ax.set_xlabel("Strategy Profile (Firm A, Firm B)", fontsize=11)
    ax.set_title("Figure 1. Payoff Comparison Across All Strategy Profiles\n"
                 "JoyRide vs. MoveIt — Malolos City (n = 60 BeSU Students)",
                 fontsize=12, fontweight="bold", pad=12)
    ax.set_ylim(0, 30000)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.grid(axis="y", color=C_GRID, linewidth=0.8, zorder=0)
    ax.legend(fontsize=10, loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Value labels
    for bar in list(bars_A) + list(bars_B):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 200,
                f"{h/1000:.1f}k", ha="center", va="bottom",
                fontsize=7.5, color="#333333")

    savefig(fig, "figure1_payoff_bar_chart.png")


# ---------------------------------------------------------------------------
# FIGURE 2 — Platform Preference Pie Chart
# ---------------------------------------------------------------------------
def fig2_platform_preference() -> None:
    """Pie chart showing platform preference distribution among 60 BeSU students."""
    rows  = load_survey()
    prefs = {}
    for r in rows:
        p = r["Preferred_Platform"]
        prefs[p] = prefs.get(p, 0) + 1

    labels = list(prefs.keys())
    sizes  = list(prefs.values())
    colours = {"JoyRide": C_JOYRIDE, "MoveIt": C_MOVEIT, "Angkas": C_ANGKAS}
    clrs   = [colours.get(l, "#999999") for l in labels]
    explode = [0.04] * len(labels)

    fig, ax = plt.subplots(figsize=(7, 6), facecolor=C_BG)
    ax.set_facecolor(C_BG)

    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=clrs,
        autopct="%1.1f%%", startangle=90,
        explode=explode, pctdistance=0.78,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
    )
    for at in autotexts:
        at.set_fontsize(11)
        at.set_fontweight("bold")
        at.set_color("white")
    for t in texts:
        t.set_fontsize(12)

    ax.set_title("Figure 2. Preferred Ride-Hailing Platform\n"
                 f"(n = {len(rows)} BeSU Students)",
                 fontsize=12, fontweight="bold", pad=14)

    # n counts in legend
    legend_labels = [f"{l}: {prefs[l]}" for l in labels]
    ax.legend(legend_labels, loc="lower center", fontsize=10,
              bbox_to_anchor=(0.5, -0.08), ncol=3)

    savefig(fig, "figure2_platform_preference.png")


# ---------------------------------------------------------------------------
# FIGURE 3 — WTP Distribution Histogram
# ---------------------------------------------------------------------------
def fig3_wtp_histogram() -> None:
    """Histogram of maximum willingness to pay among 60 respondents."""
    rows = load_survey()
    wtp  = [float(r["Max_WTP"]) for r in rows]
    wtp_mean   = sum(wtp) / len(wtp)
    wtp_median = sorted(wtp)[len(wtp) // 2]

    fig, ax = plt.subplots(figsize=(9, 5), facecolor=C_BG)
    ax.set_facecolor(C_BG)

    n_bins = 8
    ax.hist(wtp, bins=n_bins, color=C_JOYRIDE, edgecolor="white",
            linewidth=1.2, alpha=0.85, zorder=3)

    ax.axvline(wtp_mean,   color="#CC0000",  linewidth=2,
               linestyle="--", label=f"Mean = ₱{wtp_mean:.2f}", zorder=4)
    ax.axvline(wtp_median, color="#FF8800", linewidth=2,
               linestyle=":",  label=f"Median = ₱{wtp_median:.2f}", zorder=4)
    ax.axvspan(0, 80, color="#CCFFCC", alpha=0.25, zorder=1,
               label="WTP ≤ ₱80  (55.0%)")
    ax.axvspan(80, 120, color="#FFCCCC", alpha=0.25, zorder=1,
               label="WTP > ₱80  (45.0%)")

    ax.set_xlabel("Maximum Willingness to Pay per Trip (₱)", fontsize=11)
    ax.set_ylabel("Number of Respondents", fontsize=11)
    ax.set_title("Figure 3. Distribution of Maximum Willingness to Pay\n"
                 f"(n = {len(rows)} BeSU Students)",
                 fontsize=12, fontweight="bold", pad=12)
    ax.legend(fontsize=10)
    ax.grid(axis="y", color=C_GRID, linewidth=0.8, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    savefig(fig, "figure3_wtp_histogram.png")


# ---------------------------------------------------------------------------
# FIGURE 4 — Perception Grouped Bar Chart
# ---------------------------------------------------------------------------
def fig4_perception_bars() -> None:
    """Grouped bar chart: affordability and safety ratings per platform."""
    rows = load_survey()
    n    = len(rows)

    platforms = ["JoyRide", "MoveIt", "Angkas"]
    colours   = [C_JOYRIDE, C_MOVEIT, C_ANGKAS]

    afford = {p: sum(float(r[f"Afford_{p}"]) for r in rows) / n
              for p in platforms}
    safety = {p: sum(float(r[f"Safety_{p}"]) for r in rows) / n
              for p in platforms}

    x = np.arange(2)   # Affordability, Safety
    w = 0.22
    offsets = [-w, 0, w]

    fig, ax = plt.subplots(figsize=(8, 5), facecolor=C_BG)
    ax.set_facecolor(C_BG)

    for i, (plat, clr, off) in enumerate(zip(platforms, colours, offsets)):
        vals = [afford[plat], safety[plat]]
        bars = ax.bar(x + off, vals, w, label=plat, color=clr,
                      edgecolor="white", linewidth=0.8, zorder=3)
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.04,
                    f"{h:.2f}", ha="center", va="bottom",
                    fontsize=9, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(["Perceived Affordability", "Perceived Safety & Reliability"],
                       fontsize=11)
    ax.set_ylabel("Mean Rating (out of 5)", fontsize=11)
    ax.set_ylim(0, 5.5)
    ax.set_title("Figure 4. Platform Perception Ratings by Dimension\n"
                 f"(n = {n} BeSU Students, Scale: 1–5)",
                 fontsize=12, fontweight="bold", pad=12)
    ax.legend(fontsize=10, loc="upper right")
    ax.grid(axis="y", color=C_GRID, linewidth=0.8, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.axhline(5, color=C_GRID, linewidth=0.5)

    savefig(fig, "figure4_perception_bars.png")


# ---------------------------------------------------------------------------
# FIGURE 5 — Switching Behaviour Stacked Bar
# ---------------------------------------------------------------------------
def fig5_switching_behaviour() -> None:
    """
    Horizontal stacked bar showing how respondents would react to:
    - A 20% fare increase on their preferred platform
    - Scenario 1: JoyRide ₱70 vs MoveIt ₱50
    - Scenario 2: All ₱80 vs Angkas ₱60
    """
    rows = load_survey()
    n    = len(rows)

    # Category colours
    colours = {
        "Temp_switch":  "#1A6BAA",
        "Perm_switch":  "#0D3F6B",
        "Continue":     "#4CAF50",
        "Reduce":       "#8BC34A",
        "Stop":         "#E53935",
        "Switch_temp":  "#1A6BAA",
        "Switch_perm":  "#0D3F6B",
        "Stay_Joy":     "#4CAF50",
        "Compare":      "#9C27B0",
        "Fastest":      "#FF9800",
        "Angkas":       "#2C9E44",
        "Preferred":    "#4CAF50",
        "Reviews":      "#9C27B0",
        "Other":        "#999999",
    }

    # Count responses for each question
    sw20  = {}
    sc1   = {}
    sc2   = {}
    for r in rows:
        k20 = r["Switch_20pct_Increase"]
        sw20[k20] = sw20.get(k20, 0) + 1
        k1 = r["Scenario_Joy70_Move50"]
        sc1[k1] = sc1.get(k1, 0) + 1
        k2 = r["Scenario_All80_Angkas60"]
        sc2[k2] = sc2.get(k2, 0) + 1

    questions = [
        ("20% Fare\nIncrease", sw20),
        ("Scenario 1\n(₱70 vs ₱50)", sc1),
        ("Scenario 2\n(₱80 vs ₱60)", sc2),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(14, 5), facecolor=C_BG)
    fig.suptitle(
        "Figure 5. Switching Behaviour Under Different Fare Scenarios\n"
        f"(n = {n} BeSU Students)",
        fontsize=12, fontweight="bold", y=1.02,
    )

    for ax, (title, counts) in zip(axes, questions):
        ax.set_facecolor(C_BG)
        labels = list(counts.keys())
        values = [counts[l] / n * 100 for l in labels]
        clrs   = [colours.get(l, "#AAAAAA") for l in labels]
        bars   = ax.bar(labels, values, color=clrs, edgecolor="white",
                        linewidth=0.8, zorder=3)
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.5,
                    f"{h:.1f}%", ha="center", va="bottom", fontsize=8.5)

        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_ylabel("% of Respondents", fontsize=9)
        ax.set_ylim(0, 75)
        ax.grid(axis="y", color=C_GRID, linewidth=0.8, zorder=0)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize=8)

    plt.tight_layout()
    savefig(fig, "figure5_switching_behaviour.png")


# ---------------------------------------------------------------------------
# FIGURE 6 — Payoff Heatmap (Firm A)
# ---------------------------------------------------------------------------
def fig6_payoff_heatmap() -> None:
    """
    Heatmap of Firm A's payoff matrix. Nash equilibrium cells are outlined.
    """
    pA = np.array([
        [23400, 25200, 22272],
        [25200, 20000, 17600],
        [15776, 13200, 12400],
    ])
    ne_cells = [(0, 1), (1, 0)]   # (H,M) and (M,H)

    fig, ax = plt.subplots(figsize=(7, 5.5), facecolor=C_BG)
    ax.set_facecolor(C_BG)

    im = ax.imshow(pA, cmap="Blues", aspect="auto", vmin=10000, vmax=27000)
    plt.colorbar(im, ax=ax, label="Profit Units (π_A)")

    # Annotate each cell
    for i in range(3):
        for j in range(3):
            is_ne = (i, j) in ne_cells
            colour = "#AA6600" if is_ne else "white" if pA[i, j] > 21000 else "#333333"
            ax.text(j, i, f"{pA[i, j]:,}", ha="center", va="center",
                    fontsize=12, fontweight="bold" if is_ne else "normal",
                    color=colour)
            if is_ne:
                rect = plt.Rectangle(
                    (j - 0.49, i - 0.49), 0.98, 0.98,
                    linewidth=3, edgecolor=C_NE, facecolor="none"
                )
                ax.add_patch(rect)

    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["High (H)", "Medium (M)", "Discounted (D)"], fontsize=11)
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(["High (H)", "Medium (M)", "Discounted (D)"], fontsize=11)
    ax.set_xlabel("Firm B (MoveIt) Strategy", fontsize=11)
    ax.set_ylabel("Firm A (JoyRide) Strategy", fontsize=11)
    ax.set_title("Figure 6. Firm A (JoyRide) Payoff Heatmap\n"
                 "Nash Equilibrium Cells Outlined in Gold",
                 fontsize=12, fontweight="bold", pad=12)

    ne_patch = mpatches.Patch(edgecolor=C_NE, facecolor="none",
                               linewidth=3, label="Nash Equilibrium")
    ax.legend(handles=[ne_patch], loc="lower right", fontsize=10)

    savefig(fig, "figure6_payoff_heatmap.png")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    print("\n" + "=" * 60)
    print("  GENERATING ALL FIGURES")
    print("=" * 60)
    os.makedirs(RESULTS_DIR, exist_ok=True)

    fig1_payoff_bar_chart()
    print("  Figure 1: Payoff Bar Chart ..................... done")

    fig2_platform_preference()
    print("  Figure 2: Platform Preference Pie ............. done")

    fig3_wtp_histogram()
    print("  Figure 3: WTP Histogram ........................ done")

    fig4_perception_bars()
    print("  Figure 4: Perception Grouped Bars ............. done")

    fig5_switching_behaviour()
    print("  Figure 5: Switching Behaviour Bars ............ done")

    fig6_payoff_heatmap()
    print("  Figure 6: Payoff Heatmap ....................... done")

    print("\n[DONE] All figures saved to results/")


if __name__ == "__main__":
    main()
