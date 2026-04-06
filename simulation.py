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

# --- STRATEGIES ---
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

class DiplomatRP:
    def __init__(self):
        self.name = "DipRP"
        self.isTFT = False
        self.isAllC = False
        self.qScore = 0.0
    def move(self, opp_h, my_h):
        PROBE = ['C','C','D','D','C','C','D','C','C','C','C','C','C','C','C']
        r = len(opp_h)
        if r < 15: return PROBE[r]
        if r == 15:
            tft_m = sum(1 for i in range(1, 15) if opp_h[i] == my_h[i-1])
            self.isTFT = (tft_m / 14.0) >= 0.72
            cr = sum(1 for m in opp_h if m == 'C') / 15.0
            self.isAllC = (cr == 1.0)
            self.qScore = cr

        if self.isTFT: return 'C'
        if self.isAllC: return 'D'

        alpha, theta = 0.70, 0.50
        x_t = 1 if opp_h[-1] == 'C' else 0
        self.qScore = alpha * self.qScore + (1 - alpha) * x_t
        return 'C' if self.qScore >= theta else 'D'

# --- SIMULATION ENGINE ---
strategies = [
    ("TFT", TFT), ("TF2T", TF2T), ("Pavlov", Pavlov), 
    ("Grudger", Grudger), ("STFT", STFT), ("STFT II", STFT), 
    ("AllC", AllC), ("AllD", AllD), ("AllD II", AllD), 
    ("Random", Rand), ("GTFT", GTFT), ("CTFT", CTFT), 
    ("DipRP", DiplomatRP), ("DipRP II", DiplomatRP)
]

noises = np.linspace(0, 0.30, 61) 
rounds = 500
reps = 50

results = {name: [] for name, _ in strategies}

print(f"Running evolutionary simulation for 14-player ecology...")
print(f"Calculating over 160 million interactions. Please wait ~3 minutes...")

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

print("\nSimulation complete. Plotting...")

# --- RANGE ANALYZER ---
print("\n=== EVOLUTIONARY DOMINANCE REPORT ===")

# range(31) will check every single integer from 0 to 30 (1% increments)
check_points = range(31) 

for pct in check_points:
    # CRUCIAL: This math maps the 1% step to the exact 61-point data array 
    idx = int(pct / 100.0 * 60 / 0.30) 
    
    scores_at_pct = [(name, results[name][idx]) for name, _ in strategies]
    scores_at_pct.sort(key=lambda x: x[1], reverse=True)
    print(f"At {pct:02d}% Noise: 1st place -> {scores_at_pct[0][0]:<9} ({scores_at_pct[0][1]:.3f}) | 2nd place -> {scores_at_pct[1][0]:<9} ({scores_at_pct[1][1]:.3f})")
print("=====================================\n")

# --- PLOTTING ---
plt.figure(figsize=(8.27, 11.69), facecolor='#ffffff')

# High-contrast color palette, distinct markers, and matching clones
styles = {
    "DipRP":    {"color": "#ea580c", "ls": "-",  "lw": 2.5, "marker": "X", "z": 10},
    "DipRP II": {"color": "#ea580c", "ls": ":",  "lw": 2.5, "marker": "X", "z": 9},
    "CTFT":     {"color": "#16a34a", "ls": "-",  "lw": 2.0, "marker": "h", "z": 8},
    "GTFT":     {"color": "#06b6d4", "ls": "-",  "lw": 1.5, "marker": "p", "z": 7},
    "TFT":      {"color": "#2563eb", "ls": "-",  "lw": 1.5, "marker": "o", "z": 6},
    "TF2T":     {"color": "#8b5cf6", "ls": "-",  "lw": 1.5, "marker": "s", "z": 5},
    "AllD":     {"color": "#dc2626", "ls": "-",  "lw": 2.0, "marker": "D", "z": 8},
    "AllD II":  {"color": "#dc2626", "ls": ":",  "lw": 2.0, "marker": "D", "z": 7},
    "Pavlov":   {"color": "#d97706", "ls": "-",  "lw": 1.5, "marker": "^", "z": 4},
    "AllC":     {"color": "#10b981", "ls": "-",  "lw": 1.5, "marker": "v", "z": 2},
    "Grudger":  {"color": "#ec4899", "ls": "-",  "lw": 1.5, "marker": "*", "z": 1},
    "STFT":     {"color": "#64748b", "ls": "-",  "lw": 1.5, "marker": "x", "z": 4},
    "STFT II":  {"color": "#64748b", "ls": ":",  "lw": 1.5, "marker": "x", "z": 3},
    "Random":   {"color": "#171717", "ls": "-.", "lw": 1.0, "marker": ".", "z": 1}
}

ax = plt.gca()
ax.set_facecolor('#ffffff')

# Plot every strategy (This is likely what got deleted!)
for name in [s[0] for s in strategies]:
    plt.plot(noises * 100, results[name], label=name, 
             color=styles[name]["color"], 
             linestyle=styles[name]["ls"], 
             linewidth=styles[name]["lw"],
             marker=styles[name]["marker"],
             markersize=6,
             markevery=3, 
             zorder=styles[name]["z"])

# 1. Main Title: Reduced size to 22, pushed up to y=0.97
plt.suptitle("The Thermodynamic Limits of Cooperation", 
             fontfamily='serif', fontsize=22, fontweight='normal', color="#171717", y=0.97)

# 2. Subtitle: Adjusted padding to prevent overlap
plt.title("11-STRATEGY 14-PLAYER IPD ECOLOGY (160M INTERACTIONS)", 
          fontfamily='monospace', fontsize=10, color="#52525b", pad=12)

plt.xlabel("Noise Level (%)", fontfamily='sans-serif', fontsize=12, fontweight='bold', color="#52525b")
plt.ylabel("Average Payoff per Round", fontfamily='sans-serif', fontsize=12, fontweight='bold', color="#52525b")

# 3. Legend: Moved inside to the lower right corner. 
# Using 2 columns (ncol=2) and slightly smaller font (fontsize=9) to fit perfectly in the empty space.
plt.legend(loc='lower right', facecolor='#fafafa', edgecolor='#d4d4d8', labelcolor='#171717', ncol=2, fontsize=9)

plt.grid(True, color="#e4e4e7", linestyle='-', linewidth=1, alpha=0.8)

# Axis formatting
ax.spines['bottom'].set_color('#52525b')
ax.spines['left'].set_color('#52525b')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.tick_params(axis='x', colors='#171717')
ax.tick_params(axis='y', colors='#171717')

# Apply tight layout, but reserve the top 5% of the figure so the titles have room to breathe
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig("full_ecology_sweep_portrait.pdf", format='pdf', dpi=300, facecolor='#ffffff', bbox_inches='tight')
plt.show()
# ==========================================
# --- MACRO-SIMULATION: REPLICATOR DYNAMICS ---
# ==========================================
print("\n=== REPLICATOR DYNAMICS (GENERATION 200 @ 5% NOISE) ===")

# 1. Find the exact data column for 5% noise
idx_5pct = int(0.05 / 0.30 * 60) 

# 2. Set Generation 0: Equal population shares (1/14 each)
pop_shares = {name: 1.0 / len(strategies) for name, _ in strategies}

generations = 200

# 3. Run the Evolutionary Math (The x_i equation from the paper)
for gen in range(generations):
    # Get the static fitness (average scores) we already calculated
    fitness = {name: results[name][idx_5pct] for name, _ in strategies}
    
    # Calculate the average fitness of the entire ecosystem
    mean_fitness = sum(pop_shares[name] * fitness[name] for name, _ in strategies)
    
    # Update populations: Winners breed, losers starve
    for name in pop_shares:
        pop_shares[name] = pop_shares[name] * (fitness[name] / mean_fitness)

# 4. Print the final demographic breakdown
final_population = sorted(pop_shares.items(), key=lambda x: x[1], reverse=True)
for rank, (name, share) in enumerate(final_population, 1):
    print(f"{rank}. {name:<9} : {share*100:>5.2f}% population share")
print("=======================================================\n")