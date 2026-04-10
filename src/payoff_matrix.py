"""
payoff_matrix.py
================
Game-Theoretic Analysis of Fare Competition Between JoyRide and MoveIt
in Malolos City — A Non-Zero-Sum Duopoly Approach

Authors : BeSU College of Science — Mathematical Modeling Group
Course  : Mathematical Modeling and Applications
School  : Bulacan State University, Malolos City, Bulacan

Description
-----------
This module builds and solves the 3x3 non-zero-sum game in normal form
that models fare competition between JoyRide (Firm A) and MoveIt (Firm B).

Demand parameters are calibrated from survey data of 60 BeSU students
(see data/survey_data_n60.csv).

Outputs (written to results/)
------------------------------
- payoff_matrix.csv      : full 3x3 payoff table
- equilibrium_summary.csv: identified Nash equilibria
- dominance_analysis.txt : step-by-step IESDS trace
- mixed_strategy.txt     : mixed-strategy equilibrium derivation
"""

import numpy as np
import itertools
import csv
import os

# ---------------------------------------------------------------------------
# 1.  PARAMETERS  (calibrated from survey, n = 60)
# ---------------------------------------------------------------------------

STRATEGIES = ["H", "M", "D"]          # High, Medium, Discounted fare
STRATEGY_LABELS = {
    "H": "High Fare (120 units)",
    "M": "Medium Fare (100 units)",
    "D": "Discounted Fare (80 units)",
}

FARES = {"H": 120, "M": 100, "D": 80}  # arbitrary fare units per trip
COST  = 60                              # common operating cost per trip

# Per-trip profit margins
MARGIN = {s: FARES[s] - COST for s in STRATEGIES}
# => {"H": 60, "M": 40, "D": 20}

# Symmetric demand: both firms choose the same fare
# Reflects inverse price-demand relationship
Q_SYM = {"H": 780, "M": 1000, "D": 1240}

# Asymmetric total demand: firms choose different fares
Q_ASYM = {
    ("H", "M"): 1050, ("M", "H"): 1050,
    ("H", "D"): 1160, ("D", "H"): 1160,
    ("M", "D"): 1100, ("D", "M"): 1100,
}

# Market share for the LOWER-priced firm (survey-calibrated, n = 60)
# H vs M : 60% to lower  — mean switch likelihood 3.60/5, 51.7% likely (₱15-20 gap)
# H vs D : 68% to lower  — 68.3% switched in Scenario 1 (₱70 vs ₱50, ~28% gap)
# M vs D : 60% to lower  — Scenario 2 intermediate behavior (56.7% switched, rounded)
SHARE_LOW = {
    frozenset(["H", "M"]): 0.60,
    frozenset(["H", "D"]): 0.68,
    frozenset(["M", "D"]): 0.60,
}

FARE_RANK = {"D": 0, "M": 1, "H": 2}  # lower rank = cheaper fare


# ---------------------------------------------------------------------------
# 2.  DEMAND ALLOCATION
# ---------------------------------------------------------------------------

def get_quantities(sA: str, sB: str) -> tuple[float, float]:
    """
    Return the number of trips served by Firm A and Firm B
    given their chosen strategies sA and sB.

    Parameters
    ----------
    sA : str  Strategy of Firm A ("H", "M", or "D")
    sB : str  Strategy of Firm B ("H", "M", or "D")

    Returns
    -------
    (qA, qB) : tuple of floats
    """
    if sA == sB:
        q = Q_SYM[sA] / 2
        return q, q

    total_demand = Q_ASYM[(sA, sB)]
    key = frozenset([sA, sB])
    share_low = SHARE_LOW[key]

    low_firm_strategy = sA if FARE_RANK[sA] < FARE_RANK[sB] else sB

    qA = total_demand * (share_low if sA == low_firm_strategy else 1 - share_low)
    qB = total_demand * (share_low if sB == low_firm_strategy else 1 - share_low)
    return qA, qB


# ---------------------------------------------------------------------------
# 3.  PAYOFF MATRICES
# ---------------------------------------------------------------------------

def build_payoff_matrices() -> tuple[np.ndarray, np.ndarray]:
    """
    Compute the 3x3 payoff matrices for Firm A and Firm B.

    Returns
    -------
    (pA, pB) : np.ndarray shape (3, 3) each
        pA[i, j] = profit of Firm A when A plays STRATEGIES[i], B plays STRATEGIES[j]
        pB[i, j] = profit of Firm B under the same profile
    """
    n = len(STRATEGIES)
    pA = np.zeros((n, n))
    pB = np.zeros((n, n))

    for i, sA in enumerate(STRATEGIES):
        for j, sB in enumerate(STRATEGIES):
            qA, qB = get_quantities(sA, sB)
            pA[i, j] = MARGIN[sA] * qA
            pB[i, j] = MARGIN[sB] * qB

    return pA, pB


def print_payoff_matrix(pA: np.ndarray, pB: np.ndarray) -> None:
    """Print the payoff matrix in a readable table format."""
    col_w = 22
    header = f"{'Firm A \\ Firm B':<20}" + "".join(
        f"{STRATEGIES[j]:>{col_w}}" for j in range(len(STRATEGIES))
    )
    print("\n" + "=" * 70)
    print("  PAYOFF MATRIX  (π_A ; π_B)")
    print("=" * 70)
    print(header)
    print("-" * 70)
    for i, sA in enumerate(STRATEGIES):
        row = f"{sA:<20}"
        for j in range(len(STRATEGIES)):
            cell = f"({pA[i,j]:,.0f} ; {pB[i,j]:,.0f})"
            row += f"{cell:>{col_w}}"
        print(row)
    print("=" * 70)


# ---------------------------------------------------------------------------
# 4.  DOMINANCE ANALYSIS  (IESDS)
# ---------------------------------------------------------------------------

def dominance_analysis(pA: np.ndarray, pB: np.ndarray) -> dict:
    """
    Perform Iterative Elimination of Strictly Dominated Strategies (IESDS).

    Returns a dict with:
      - 'dominated_A': list of dominated strategy indices for Firm A
      - 'dominated_B': list of dominated strategy indices for Firm B
      - 'trace': list of strings describing each elimination step
    """
    trace = []
    dominated_A = []
    dominated_B = []

    # Check each strategy of Firm A
    for i, sA in enumerate(STRATEGIES):
        for k, sK in enumerate(STRATEGIES):
            if k == i:
                continue
            # Does sK strictly dominate sA for every rival strategy?
            if all(pA[k, j] > pA[i, j] for j in range(len(STRATEGIES))):
                dominated_A.append(i)
                trace.append(
                    f"Firm A: '{sA}' is strictly dominated by '{sK}' "
                    f"(payoffs: {[int(pA[k,j]) for j in range(3)]} > "
                    f"{[int(pA[i,j]) for j in range(3)]})"
                )
                break

    # Check each strategy of Firm B (symmetric)
    for j, sB in enumerate(STRATEGIES):
        for k, sK in enumerate(STRATEGIES):
            if k == j:
                continue
            if all(pB[i, k] > pB[i, j] for i in range(len(STRATEGIES))):
                dominated_B.append(j)
                trace.append(
                    f"Firm B: '{sB}' is strictly dominated by '{sK}' "
                    f"(payoffs: {[int(pB[i,k]) for i in range(3)]} > "
                    f"{[int(pB[i,j]) for i in range(3)]})"
                )
                break

    return {
        "dominated_A": dominated_A,
        "dominated_B": dominated_B,
        "trace": trace,
    }


# ---------------------------------------------------------------------------
# 5.  PURE-STRATEGY NASH EQUILIBRIA
# ---------------------------------------------------------------------------

def find_pure_nash(pA: np.ndarray, pB: np.ndarray) -> list[tuple[str, str]]:
    """
    Identify all pure-strategy Nash equilibria.

    A strategy profile (i, j) is a Nash equilibrium if:
      pA[i, j] >= pA[k, j]  for all k   (Firm A cannot improve by deviating)
      pB[i, j] >= pB[i, k]  for all k   (Firm B cannot improve by deviating)

    Returns
    -------
    List of (strategy_A, strategy_B) tuples that are Nash equilibria.
    """
    equilibria = []
    n = len(STRATEGIES)
    for i, j in itertools.product(range(n), repeat=2):
        a_best = pA[i, j] >= np.max(pA[:, j])   # A's best response to B=j
        b_best = pB[i, j] >= np.max(pB[i, :])   # B's best response to A=i
        if a_best and b_best:
            equilibria.append((STRATEGIES[i], STRATEGIES[j]))
    return equilibria


# ---------------------------------------------------------------------------
# 6.  MIXED-STRATEGY NASH EQUILIBRIUM  (2x2 reduced game)
# ---------------------------------------------------------------------------

def compute_mixed_strategy(pA: np.ndarray, pB: np.ndarray) -> dict:
    """
    Compute the mixed-strategy Nash equilibrium for the 2x2 subgame
    {H, M} x {H, M} obtained after eliminating dominated strategy D.

    Firm B's indifference condition (equating expected payoffs):
        U_B(H) = U_B(M)
        pB[H,H]*p + pB[M,H]*(1-p) = pB[H,M]*p + pB[M,M]*(1-p)
    Solving for p* gives Firm A's mixing probability for H.

    By symmetry, q* = p* for Firm B.

    Returns
    -------
    dict with keys:
      p_star  : Pr(A plays H)
      q_star  : Pr(B plays H)  [= p_star by symmetry]
      exp_payoff_A : expected payoff to Firm A
      exp_payoff_B : expected payoff to Firm B
      derivation   : list of step strings
    """
    # Indices: H=0, M=1 in the original matrix
    H, M = 0, 1

    # Payoffs in the reduced 2x2 subgame
    a_HH = pA[H, H];  a_HM = pA[H, M]
    a_MH = pA[M, H];  a_MM = pA[M, M]
    b_HH = pB[H, H];  b_HM = pB[H, M]
    b_MH = pB[M, H];  b_MM = pB[M, M]

    # Firm A's indifference (solve for q* = Pr(B plays H))
    # U_A(H) = U_A(M)
    # a_HH*q + a_HM*(1-q) = a_MH*q + a_MM*(1-q)
    # q*(a_HH - a_HM - a_MH + a_MM) = a_MM - a_HM
    denom_q = (a_HH - a_HM - a_MH + a_MM)
    numer_q = (a_MM - a_HM)
    q_star = numer_q / denom_q if denom_q != 0 else None

    # Firm B's indifference (solve for p* = Pr(A plays H))
    denom_p = (b_HH - b_MH - b_HM + b_MM)
    numer_p = (b_MM - b_MH)
    p_star = numer_p / denom_p if denom_p != 0 else None

    exp_A = (a_HH * p_star * q_star
             + a_HM * p_star * (1 - q_star)
             + a_MH * (1 - p_star) * q_star
             + a_MM * (1 - p_star) * (1 - q_star)) if p_star and q_star else None

    exp_B = (b_HH * p_star * q_star
             + b_HM * p_star * (1 - q_star)
             + b_MH * (1 - p_star) * q_star
             + b_MM * (1 - p_star) * (1 - q_star)) if p_star and q_star else None

    derivation = [
        "Mixed-Strategy Nash Equilibrium Derivation",
        "=" * 50,
        "Reduced 2x2 subgame payoffs after IESDS (H=0, M=1):",
        f"  (H,H): A={a_HH:,.0f}, B={b_HH:,.0f}",
        f"  (H,M): A={a_HM:,.0f}, B={b_HM:,.0f}",
        f"  (M,H): A={a_MH:,.0f}, B={b_MH:,.0f}",
        f"  (M,M): A={a_MM:,.0f}, B={b_MM:,.0f}",
        "",
        "Firm B indifference condition: U_B(H) = U_B(M)",
        f"  {b_HH:,.0f}p + {b_MH:,.0f}(1-p) = {b_HM:,.0f}p + {b_MM:,.0f}(1-p)",
        f"  {b_HH - b_MH:,.0f}p + {b_MH:,.0f} = {b_HM - b_MM:,.0f}p + {b_MM:,.0f}",
        f"  {b_HH - b_MH - b_HM + b_MM:,.0f}p = {b_MM - b_MH:,.0f}",
        f"  p* = {numer_p:,.0f} / {denom_p:,.0f} = {p_star:.4f}  (~{p_star*100:.1f}%)",
        "",
        "By symmetry, q* = p*:",
        f"  q* = {q_star:.4f}  (~{q_star*100:.1f}%)",
        "",
        f"Mixed-Strategy NE: sigma_A* = sigma_B* = (H={p_star:.4f}, M={1-p_star:.4f})",
        f"Expected payoff per firm: ~{exp_A:,.0f} units/period",
    ]

    return {
        "p_star": p_star,
        "q_star": q_star,
        "exp_payoff_A": exp_A,
        "exp_payoff_B": exp_B,
        "derivation": derivation,
    }


# ---------------------------------------------------------------------------
# 7.  SAVE RESULTS
# ---------------------------------------------------------------------------

def save_payoff_csv(pA: np.ndarray, pB: np.ndarray, path: str) -> None:
    """Save the payoff matrix to a CSV file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Firm_A_Strategy", "Firm_B_Strategy",
                         "pi_A", "pi_B", "Combined"])
        for i, sA in enumerate(STRATEGIES):
            for j, sB in enumerate(STRATEGIES):
                writer.writerow([sA, sB,
                                  round(pA[i, j], 2),
                                  round(pB[i, j], 2),
                                  round(pA[i, j] + pB[i, j], 2)])
    print(f"  [saved] {path}")


def save_equilibrium_csv(equilibria: list, mixed: dict, path: str) -> None:
    """Save equilibrium summary to CSV."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Type", "Strategy_A", "Strategy_B",
                         "pi_A", "pi_B", "Combined"])
        for idx, (sA, sB) in enumerate(equilibria, 1):
            i = STRATEGIES.index(sA)
            j = STRATEGIES.index(sB)
            pA_val, pB_val = _get_payoff(sA, sB)
            writer.writerow([f"Pure-Strategy NE {idx}", sA, sB,
                              round(pA_val, 2), round(pB_val, 2),
                              round(pA_val + pB_val, 2)])
        writer.writerow(["Mixed-Strategy NE",
                         f"Pr(H)={mixed['p_star']:.4f}",
                         f"Pr(H)={mixed['q_star']:.4f}",
                         round(mixed["exp_payoff_A"], 2),
                         round(mixed["exp_payoff_B"], 2),
                         round(mixed["exp_payoff_A"] + mixed["exp_payoff_B"], 2)])
    print(f"  [saved] {path}")


def _get_payoff(sA: str, sB: str) -> tuple[float, float]:
    """Helper: compute a single payoff pair."""
    qA, qB = get_quantities(sA, sB)
    return MARGIN[sA] * qA, MARGIN[sB] * qB


def save_text(lines: list[str], path: str) -> None:
    """Save a list of strings as a text file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  [saved] {path}")


# ---------------------------------------------------------------------------
# 8.  MAIN
# ---------------------------------------------------------------------------

def main():
    print("\n" + "=" * 70)
    print("  GAME-THEORETIC FARE COMPETITION MODEL")
    print("  JoyRide vs. MoveIt — Malolos City")
    print("  Survey data: n = 60 BeSU students")
    print("=" * 70)

    # Build payoff matrices
    pA, pB = build_payoff_matrices()
    print_payoff_matrix(pA, pB)

    # Dominance analysis
    dom = dominance_analysis(pA, pB)
    print("\n--- Dominance Analysis (IESDS) ---")
    for step in dom["trace"]:
        print(f"  > {step}")
    if not dom["trace"]:
        print("  No strictly dominated strategies found.")

    # Pure-strategy Nash equilibria
    equilibria = find_pure_nash(pA, pB)
    print("\n--- Pure-Strategy Nash Equilibria ---")
    for eq in equilibria:
        pAv, pBv = _get_payoff(*eq)
        print(f"  ({eq[0]}, {eq[1]})  =>  pi_A = {pAv:,.0f} ;  pi_B = {pBv:,.0f}  "
              f"|  Combined = {pAv + pBv:,.0f}")
    if not equilibria:
        print("  No pure-strategy Nash equilibrium found.")

    # Mixed-strategy Nash equilibrium
    mixed = compute_mixed_strategy(pA, pB)
    print("\n--- Mixed-Strategy Nash Equilibrium ---")
    for line in mixed["derivation"]:
        print("  " + line)

    # Save results
    print("\n--- Saving Results ---")
    save_payoff_csv(pA, pB, "results/payoff_matrix.csv")
    save_equilibrium_csv(equilibria, mixed, "results/equilibrium_summary.csv")
    dom_lines = (
        ["Dominance Analysis — IESDS Trace", "=" * 50] +
        dom["trace"] +
        ["", f"Eliminated from Firm A: {[STRATEGIES[i] for i in dom['dominated_A']]}",
            f"Eliminated from Firm B: {[STRATEGIES[j] for j in dom['dominated_B']]}",
            "Reduced game: {H, M} x {H, M}"]
    )
    save_text(dom_lines, "results/dominance_analysis.txt")
    save_text(mixed["derivation"], "results/mixed_strategy.txt")

    print("\n[DONE] All results saved to results/")


if __name__ == "__main__":
    main()
