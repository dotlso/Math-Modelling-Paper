# 🏍️ Game-Theoretic Fare Competition: JoyRide vs. MoveIt (Malolos City)

> **A Non-Zero-Sum Duopoly Approach**  
> Bulacan State University — College of Science  
> Mathematical Modeling and Applications  
> Academic Year 2024–2025

---

## 📋 Overview

This repository contains the complete Python implementation for the research paper:

**"A Game-Theoretic Analysis of Fare Competition Between JoyRide and MoveIt in Malolos City: A Non-Zero-Sum Duopoly Approach"**

The study models fare competition between two motorcycle ride-hailing platforms as a static, two-player, non-zero-sum game in normal form. Demand parameters are calibrated from a survey of **60 BeSU college students** (data in `data/`).

### Key Results
| Equilibrium | Strategies | π_A | π_B | Combined |
|---|---|---|---|---|
| Pure-Strategy NE 1 | (High, Medium) | 25,200 | 25,200 | 50,400 |
| Pure-Strategy NE 2 | (Medium, High) | 25,200 | 25,200 | 50,400 |
| Mixed-Strategy NE | Pr(H) ≈ 74.3% | ~23,863 | ~23,863 | ~47,726 |

---

## 📁 Repository Structure

```
📦 joyride-moveit-game-theory/
├── 📂 data/
│   └── survey_data_n60.csv          ← Raw survey data (n = 60 BeSU students)
│
├── 📂 src/
│   ├── payoff_matrix.py             ← Payoff computation & Nash equilibrium
│   ├── survey_analysis.py           ← Descriptive statistics from survey data
│   └── 📂 visualizations/
│       └── visualizations.py        ← All 6 figures for the paper
│
├── 📂 results/                      ← Auto-generated outputs (created on run)
│   ├── payoff_matrix.csv
│   ├── equilibrium_summary.csv
│   ├── dominance_analysis.txt
│   ├── mixed_strategy.txt
│   ├── survey_summary_stats.csv
│   ├── survey_descriptive_report.txt
│   └── figure1_*.png ... figure6_*.png
│
├── 📂 docs/
│   └── paper_summary.md             ← Short summary of the research paper
│
├── run_all.py                       ← ⭐ Master script: runs everything
├── requirements.txt                 ← Python dependencies
└── README.md                        ← This file
```

---

## ⚙️ Setup Instructions

### Prerequisites
- **Python 3.9 or higher**
- `pip` (Python package manager)

### Step 1 — Clone the Repository
```bash
git clone https://github.com/your-username/joyride-moveit-game-theory.git
cd joyride-moveit-game-theory
```

### Step 2 — Install Dependencies
```bash
pip install -r requirements.txt
```

Only two packages are needed:

| Package | Purpose |
|---|---|
| `numpy` | Matrix operations, payoff calculations |
| `matplotlib` | All figures and plots |

### Step 3 — Run the Full Pipeline
```bash
python run_all.py
```

This runs all three steps in sequence and saves every output to `results/`.

---

## ▶️ Running Individual Scripts

You can also run each script independently from the **repo root**:

```bash
# Step 1: Survey descriptive statistics
python src/survey_analysis.py

# Step 2: Payoff matrix and Nash equilibrium analysis
python src/payoff_matrix.py

# Step 3: Generate all figures
python src/visualizations/visualizations.py
```

---

## 📊 Expected Outputs

After running `python run_all.py`, the `results/` folder will contain:

| File | Description |
|---|---|
| `payoff_matrix.csv` | 9-row table of all (sA, sB) payoff pairs |
| `equilibrium_summary.csv` | Pure and mixed Nash equilibria with payoffs |
| `dominance_analysis.txt` | Step-by-step IESDS trace |
| `mixed_strategy.txt` | Mixed-strategy equilibrium derivation |
| `survey_summary_stats.csv` | All key stats from n=60 survey |
| `survey_descriptive_report.txt` | Human-readable statistics report |
| `figure1_payoff_bar_chart.png` | Payoff comparison across all 9 profiles |
| `figure2_platform_preference.png` | Platform preference pie chart |
| `figure3_wtp_histogram.png` | Willingness-to-pay distribution |
| `figure4_perception_bars.png` | Affordability & safety ratings |
| `figure5_switching_behaviour.png` | Switching behaviour under fare scenarios |
| `figure6_payoff_heatmap.png` | Firm A payoff heatmap with NE highlighted |

---

## 🔢 Model Parameters

All demand parameters are calibrated from the survey (n = 60, BeSU students):

```python
FARES  = {"H": 120, "M": 100, "D": 80}   # fare units per trip
COST   = 60                                # common cost per trip

# Survey-derived market share splits
SHARE_LOW = {
    frozenset(["H", "M"]): 0.60,  # 51.7% likely to switch on ₱15–20 gap
    frozenset(["H", "D"]): 0.68,  # 68.3% switched in Scenario 1 (₱70 vs ₱50)
    frozenset(["M", "D"]): 0.60,  # Scenario 2 approximation
}
```

To experiment with alternative parameters, edit the constants at the top of `src/payoff_matrix.py`.

---

## 📈 Sample Console Output

```
======================================================================
  GAME-THEORETIC FARE COMPETITION MODEL
  JoyRide vs. MoveIt — Malolos City
  Survey data: n = 60 BeSU students
======================================================================

  PAYOFF MATRIX  (π_A ; π_B)
======================================================================
Firm A \ Firm B                    H                    M                    D
----------------------------------------------------------------------
H                    (23,400 ; 23,400)    (25,200 ; 25,200)    (22,272 ; 15,776)
M                    (25,200 ; 25,200)    (20,000 ; 20,000)    (17,600 ; 13,200)
D                    (15,776 ; 22,272)    (13,200 ; 17,600)    (12,400 ; 12,400)

--- Dominance Analysis (IESDS) ---
  > Firm A: 'D' is strictly dominated by 'H'
  > Firm B: 'D' is strictly dominated by 'H'

--- Pure-Strategy Nash Equilibria ---
  (H, M)  =>  pi_A = 25,200 ;  pi_B = 25,200  |  Combined = 50,400
  (M, H)  =>  pi_A = 25,200 ;  pi_B = 25,200  |  Combined = 50,400

--- Mixed-Strategy Nash Equilibrium ---
  p* = 52/70 ≈ 0.7429  (~74.3%)
  Expected payoff per firm: ~23,863 units/period
```

---

## 📚 Data Description

**`data/survey_data_n60.csv`** — 60 responses, 21 columns:

| Column | Type | Description |
|---|---|---|
| `ID` | int | Respondent ID |
| `Age_Group` | categorical | 17-below / 18-20 / 21-23 / 24+ |
| `Gender` | categorical | Male / Female / Prefer not |
| `Year_Level` | categorical | 1st–5th Year |
| `Weekly_Usage` | categorical | Frequency of ride-hailing use |
| `Preferred_Platform` | categorical | JoyRide / MoveIt / Angkas |
| `Monthly_Trips` | categorical | Trip frequency bracket |
| `Max_WTP` | numeric | Maximum willingness to pay (₱) |
| `Switch_20pct_Increase` | categorical | Behavior on 20% fare increase |
| `Switch_Likelihood_15-20_Lower` | 1–5 Likert | Likelihood to switch on ₱15–20 lower fare |
| `Promo_Influence` | 1–5 Likert | Influence of promotions on choice |
| `Scenario_Joy70_Move50` | categorical | Response to JoyRide ₱70 vs MoveIt ₱50 |
| `Scenario_All80_Angkas60` | categorical | Response to all ₱80 vs Angkas ₱60 |
| `Afford_JoyRide/MoveIt/Angkas` | 1–5 Likert | Perceived affordability per platform |
| `Safety_JoyRide/MoveIt/Angkas` | 1–5 Likert | Perceived safety per platform |
| `Price_vs_Quality` | 1–5 Likert | Price vs. quality orientation |

---

## 📜 References

- Nash, J. F. (1950). Equilibrium points in n-person games. *PNAS*, 36(1), 48–49.
- Osborne, M. J., & Rubinstein, A. (1994). *A course in game theory*. MIT Press.
- Gibbons, R. (1992). *A primer in game theory*. Harvester Wheatsheaf.
- Cai et al. (2024). Pricing competition in ride-hailing platforms. *Transportation Research Part C*, 158.
- Walunj et al. (2025). Competitive pricing equilibria in ride-hailing duopolies. *Transportation Research Part B*, 181.

---

## 👥 Authors

Bulacan State University — College of Science  
Mathematical Modeling and Applications  
Malolos City, Bulacan, Philippines

---

## 📄 License

For academic use only. Not for commercial distribution.
