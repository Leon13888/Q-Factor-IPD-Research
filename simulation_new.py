import random
import numpy as np
import matplotlib.pyplot as plt

def apply_noise(m, n):
    if random.random() < n:
        return 'D' if m == 'C' else 'C'
    return m

def payoff(a, b):
    if a == 'C' and b == 'C': return 3
    if a == 'C' and b == 'D': return 0
    if a == 'D' and b == 'C': return 5
    return 1

# ==========================================
# --- STRATEGIES ---
# ==========================================
class TFT:
    def __init__(self): self.name = "TFT"
    def move(self, opp_h, my_h): return 'C' if not opp_h else opp_h[-1]

class TF2T:
    def __init__(self): self.name = "TF2T"
    def move(self, opp_h, my_h):
        if len(opp_h) < 2: return 'C'
        return 'D' if opp_h[-1] == 'D' and opp_h[-2] == 'D' else 'C'

class Pavlov:
    def __init__(self): self.name = "Pavlov"
    def move(self, opp_h, my_h):
        if not opp_h: return 'C'
        won = (my_h[-1] == 'C' and opp_h[-1] == 'C') or (my_h[-1] == 'D' and opp_h[-1] == 'C')
        return my_h[-1] if won else ('D' if my_h[-1] == 'C' else 'C')

class Grudger:
    def __init__(self): self.name = "Grudger"
    def move(self, opp_h, my_h): return 'D' if 'D' in opp_h else 'C'

class STFT:
    def __init__(self): self.name = "STFT"
    def move(self, opp_h, my_h): return 'D' if not opp_h else opp_h[-1]

class AllC:
    def __init__(self): self.name = "AllC"
    def move(self, opp_h, my_h): return 'C'

class AllD:
    def __init__(self): self.name = "AllD"
    def move(self, opp_h, my_h): return 'D'

class Rand:
    def __init__(self): self.name = "Random"
    def move(self, opp_h, my_h): return 'C' if random.random() < 0.5 else 'D'

class GTFT:
    def __init__(self): self.name = "GTFT"
    def move(self, opp_h, my_h):
        if not opp_h: return 'C'
        if opp_h[-1] == 'D':
            return 'C' if random.random() < 0.33 else 'D'
        return 'C'

class CTFT:
    def __init__(self):
        self.name = "CTFT"
        self.intended = []
        self.contrite = False
    def move(self, opp_h, my_h):
        move = 'C'
        r = len(opp_h)
        if r > 0:
            if self.intended[-1] == 'C' and my_h[-1] == 'D':
                self.contrite = True
            elif my_h[-1] == 'C':
                self.contrite = False

            if self.contrite:
                move = 'C'
            else:
                justified = False
                if r >= 2 and self.intended[-2] == 'C' and my_h[-2] == 'D':
                    justified = True
                move = 'D' if (opp_h[-1] == 'D' and not justified) else 'C'
        self.intended.append(move)
        return move

class QFactor:
    def __init__(self):
        self.name = "QFac"
        self.isTFT = False
        self.isAllC = False
        self.qScore = 0.0

    def move(self, opp_h, my_h):
        # ACTIVE DISCRIMINATOR PROBE: Consecutive 'D's at positions 3 and 4
        # Forces threshold-based strategies (TF2T) to reveal themselves
        PROBE = ['C','C','D','D','C','C','C','C','C','C','C','C','C','C','C']
        
        r = len(opp_h)
        
        # 1. Probe Phase (Rounds 0-14)
        if r < 15: 
            return PROBE[r]
            
        # 2. Evaluation Phase (Round 15)
        if r == 15:
            # Measure similarity to TFT's reactive logic
            tft_m = sum(1 for i in range(1, 15) if opp_h[i] == my_h[i-1])
            self.isTFT = (tft_m / 14.0) >= 0.72
            
            # Measure unconditional cooperation
            cr = sum(1 for m in opp_h if m == 'C') / 15.0
            self.isAllC = (cr == 1.0)
            self.qScore = cr

        # 3. Execution Phase (Rounds 15+)
        if self.isAllC: return 'D'   # Ruthlessly exploit naive cooperators
        if self.isTFT: return 'C'    # Cooperate with strict reciprocators
        
        # Q(t) Memory Ledger for complex/mean environments
        alpha, theta = 0.70, 0.50
        x_t = 1 if opp_h[-1] == 'C' else 0
        self.qScore = alpha * self.qScore + (1 - alpha) * x_t
        return 'C' if self.qScore >= theta else 'D'

class ZDExtort:
    def __init__(self): 
        self.name = "ZDExtort"
        
    def move(self, opp_h, my_h):
        if not opp_h: return 'C'
        m_prev, o_prev = my_h[-1], opp_h[-1]
        
        # Canonical Extort-2 probabilities (Chi=2) for R=3, S=0, T=5, P=1
        if m_prev == 'C' and o_prev == 'C': p = 8.0/9.0
        elif m_prev == 'C' and o_prev == 'D': p = 1.0/2.0
        elif m_prev == 'D' and o_prev == 'C': p = 1.0/3.0
        else: p = 0.0
        
        return 'C' if random.random() < p else 'D'

# ==========================================
# --- SIMULATION ENGINE ---
# ==========================================
# Roster balanced: 7 Nice, 7 Mean (including ZDExtort replacing AllD II)
strategies = [
    ("TFT", TFT), ("TF2T", TF2T), ("Pavlov", Pavlov), 
    ("Grudger", Grudger), ("STFT", STFT), ("STFT II", STFT), 
    ("AllC", AllC), ("AllD", AllD), ("ZDExtort", ZDExtort), 
    ("Random", Rand), ("GTFT", GTFT), ("CTFT", CTFT), 
    ("QFac", QFactor), ("QFac II", QFactor)
]

noises = np.linspace(0, 0.30, 61) 
rounds = 500
reps = 50 # 50 reps x 500 rounds x 105 pairings x 61 noise levels ≈ 160M interactions

results = {name: [] for name, _ in strategies}

print(f"Running evolutionary simulation for 14-player ecology...")
print(f"Calculating interactions across the noise spectrum. Please wait...")

for noise in noises:
    totals = {name: 0.0 for name, _ in strategies}
    for rep in range(reps):
        for i in range(len(strategies)):
            for j in range(i, len(strategies)):
                sA_name, clsA = strategies[i]
                sB_name, clsB = strategies[j]
                sA, sB = clsA(), clsB()
                hA, hB = [], []
                scoreA, scoreB = 0, 0
                
                for _ in range(rounds):
                    iA, iB = sA.move(hB, hA), sB.move(hA, hB)
                    a, b = apply_noise(iA, noise), apply_noise(iB, noise)
                    scoreA += payoff(a, b)
                    scoreB += payoff(b, a)
                    hA.append(a)
                    hB.append(b)
                
                if i == j:
                    totals[sA_name] += scoreA
                else:
                    totals[sA_name] += scoreA
                    totals[sB_name] += scoreB
                    
    n_opponents = len(strategies)
    for name, _ in strategies:
        avg_score = totals[name] / (n_opponents * rounds * reps)
        results[name].append(avg_score)

print("\nSimulation complete. Generating Figure 2...")
# ==========================================
# --- PLOTTING: FIGURE 2 (NUMBERED LINES) ---
# ==========================================
plt.figure(figsize=(11, 8), facecolor='#ffffff') # Slightly wider to accommodate legend
ax = plt.gca()
ax.set_facecolor('#ffffff')

# Dictionary assigning a specific number and style to every unique strategy
strategy_styles = {
    "QFac":     {"num": "1",  "color": "#ea580c", "lw": 3.0, "z": 10},
    "CTFT":     {"num": "2",  "color": "#16a34a", "lw": 2.5, "z": 9},
    "ZDExtort": {"num": "3",  "color": "#000000", "lw": 2.5, "z": 9, "ls": "--"},
    "TFT":      {"num": "4",  "color": "#2563eb", "lw": 2.5, "z": 8},
    "TF2T":     {"num": "5",  "color": "#9333ea", "lw": 2.5, "z": 9},
    "AllD":     {"num": "6",  "color": "#dc2626", "lw": 2.5, "z": 8},
    "Pavlov":   {"num": "7",  "color": "#6b7280", "lw": 1.5, "z": 5},
    "Random":   {"num": "8",  "color": "#6b7280", "lw": 1.5, "z": 5},
    "Grudger":  {"num": "9",  "color": "#6b7280", "lw": 1.5, "z": 5},
    "GTFT":     {"num": "10", "color": "#6b7280", "lw": 1.5, "z": 5},
    "STFT":     {"num": "11", "color": "#6b7280", "lw": 1.5, "z": 5},
    "AllC":     {"num": "12", "color": "#6b7280", "lw": 1.5, "z": 4}
}

# Create an offset counter to stagger the markers
offset = 0 

# Plot unique strategies only
for name, style in strategy_styles.items():
    if name in results:
        # Use MathText to render the number directly on the line
        marker_str = f'${style["num"]}$' 
        legend_label = f'{style["num"]}. {name}'
        
        # STAGGER LOGIC: (start_index, step_size)
        # Using offset % 6 ensures the start index cycles safely (0, 1, 2, 3, 4, 5)
        staggered_markevery = (offset % 6, 6)
        
        plt.plot(noises * 100, results[name], label=legend_label, 
                 color=style["color"], linewidth=style["lw"], 
                 linestyle=style.get("ls", "-"), marker=marker_str, 
                 markersize=9, markevery=staggered_markevery, zorder=style["z"])
        
        # Increase the offset for the next strategy line
        offset += 1
# Add Phase Transition Boundaries
for threshold in [1, 10, 16.8, 25]:
    plt.axvline(x=threshold, color='black', linestyle=':', alpha=0.4, zorder=2)

# Text labels for the Regimes 
y_text = 2.6
plt.text(5, y_text, 'Rule of Law', ha='center', fontsize=9, alpha=0.7)
plt.text(13.4, y_text, 'Grace\n(CTFT)', ha='center', fontsize=9, alpha=0.7)
plt.text(21, y_text, 'Paranoia', ha='center', fontsize=9, alpha=0.7)
plt.text(28, y_text, 'Collapse', ha='center', fontsize=9, alpha=0.7)

plt.suptitle("The Limits of Cooperation: Payoff vs. Noise", fontfamily='serif', fontsize=18, y=0.96)
plt.title("14-Player IPD Ecology (All Strategies Numbered)", fontsize=10, color="#52525b", pad=10)
plt.xlabel("Noise Level (%)", fontweight='bold', color="#52525b")
plt.ylabel("Average Payoff per Round", fontweight='bold', color="#52525b")

# Position legend outside the plot so it doesn't cover data lines
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=True, fontsize=10)
plt.grid(True, color="#e4e4e7", linestyle='-', linewidth=1, alpha=0.8)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()

# Save as vector graphic for publication
plt.savefig("Figure2_NoiseSweep_Numbered.pdf", format='pdf', dpi=300, bbox_inches='tight')
print("\nFigure 2 saved successfully with numbered lines.")
plt.show()
import csv

# ==========================================
# --- EXPORT APPENDIX A TO CSV (WITH SYSTEMIC AVERAGE) ---
# ==========================================
print("\nGenerating Appendix A Table...")
csv_filename = "AppendixA_DominanceReport.csv"

with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    # Added "Systemic Avg" to the headers
    writer.writerow(["Noise Level", "Systemic Avg", "1st Place Strategy", "Score", "2nd Place Strategy", "Score"])
    
    for idx in range(0, len(noises), 2):
        noise = noises[idx]
        
        # Calculate Systemic Average (the overall health of the ecology)
        total_system_score = sum(results[name][idx] for name in results)
        systemic_avg = total_system_score / len(results)
        
        current_scores = [(name, results[name][idx]) for name in results]
        current_scores.sort(key=lambda x: x[1], reverse=True)
        
        first_name, first_score = current_scores[0]
        second_name, second_score = current_scores[1]
        
        noise_pct = f"{int(round(noise * 100))}%"
        
        # Write the new row data
        writer.writerow([noise_pct, f"{systemic_avg:.3f}", first_name, f"{first_score:.3f}", second_name, f"{second_score:.3f}"])

print(f"Successfully saved '{csv_filename}'.")