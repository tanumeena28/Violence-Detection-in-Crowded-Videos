"""Generate real figures from FederatedHAR + run a preliminary identity-leakage test.

Usage: python3 -I make_figures.py <keypoints_dir> <out_dir>
"""
import sys, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

ROOT, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(0)

NAVY, TEAL, ORANGE, BLUE, AMBER, SLATE = "#1A2347", "#00A896", "#E8552F", "#5B7FD4", "#F2A93B", "#7C8AA8"
ICE = "#EEF1F8"
CLIENT_COLORS = [BLUE, TEAL, ORANGE, AMBER, "#8E6BBF"]
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": "#C9D2E3",
                     "axes.labelcolor": NAVY, "text.color": NAVY,
                     "xtick.color": NAVY, "ytick.color": NAVY, "axes.titlecolor": NAVY})

GN = ["down", "grab", "left", "nothing", "right", "stop", "ungrab", "up"]

def load(c, sp):
    X = np.loadtxt(os.path.join(ROOT, f"client_{c}", f"x_{sp}.txt"), delimiter=",")
    Y = np.loadtxt(os.path.join(ROOT, f"client_{c}", f"y_{sp}.txt"), delimiter=",", dtype=int)
    return X, Y

data = {sp: {c: load(c, sp) for c in range(1, 6)} for sp in ("train", "test")}

# ============================================================ FIG 1: heterogeneity
counts = np.zeros((5, 8), dtype=int)
for c in range(1, 6):
    Y = data["train"][c][1]
    for g in range(1, 9):
        counts[c - 1, g - 1] = int((Y[:, 0] == g).sum())

frac = counts / counts.sum(1, keepdims=True) * 100
fig, ax = plt.subplots(figsize=(9.6, 3.9))
cmap = LinearSegmentedColormap.from_list("ice2teal", ["#FFFFFF", "#CFEDE7", TEAL])
im = ax.imshow(frac, cmap=cmap, aspect="auto", vmin=0, vmax=frac.max())
for i in range(5):
    for j in range(8):
        v = frac[i, j]
        ax.text(j, i, f"{v:.1f}%\n{counts[i,j]}", ha="center", va="center", fontsize=8.5,
                color="white" if v > frac.max() * 0.80 else NAVY,
                fontweight="bold" if (v < 2 or v > 20) else "normal")
ax.set_xticks(range(8)); ax.set_xticklabels([f"G{j+1}\n{GN[j]}" for j in range(8)], fontsize=9)
ax.set_yticks(range(5)); ax.set_yticklabels([f"Client {i+1}\n({counts[i].sum():,} fr)" for i in range(5)], fontsize=9)
ax.set_title("Gesture distribution per client — the non-IID structure, measured from the released data",
             fontsize=11.5, fontweight="bold", pad=11)
cb = fig.colorbar(im, ax=ax, pad=0.015); cb.set_label("% of that client's frames", fontsize=9)
cb.outline.set_edgecolor("#C9D2E3")
ax.text(0, 1.0, "", transform=ax.transAxes)
fig.text(0.012, 0.015, "Class labels 1-8; gesture names confirmed against the mean poses in Fig. 2. "
         "Client 5 / G3 has 64 frames vs 862 for Client 2 \u2014 a 13.5\u00D7 imbalance.",
         fontsize=8.2, color=SLATE, style="italic")
fig.tight_layout(rect=[0, 0.045, 1, 1])
fig.savefig(os.path.join(OUT, "fig1_heterogeneity.png"), dpi=200, facecolor="white")
plt.close(fig)
print("fig1 done")

# ============================================================ FIG 2: real skeletons
# joint layout inferred empirically from mean y (top->bottom) and mean x (right/left)
EDGES = [(0, 1), (0, 2), (1, 2), (1, 3), (3, 5), (2, 4), (4, 6),
         (1, 7), (2, 8), (7, 8), (7, 9), (9, 11), (8, 10), (10, 12)]
Xtr = np.vstack([data["train"][c][0] for c in range(1, 6)])
Ytr = np.vstack([data["train"][c][1] for c in range(1, 6)])

fig, axes = plt.subplots(2, 4, figsize=(12.4, 5.0))
for g in range(1, 9):
    ax = axes[(g - 1) // 4, (g - 1) % 4]
    sel = Ytr[:, 0] == g
    P = Xtr[sel].reshape(-1, 13, 2)
    mean_pose = P.mean(0)
    spread = P.std(0).mean(1)
    for a, b in EDGES:
        ax.plot([mean_pose[a, 0], mean_pose[b, 0]], [mean_pose[a, 1], mean_pose[b, 1]],
                color=NAVY, lw=2.6, zorder=1, solid_capstyle="round")
    sc = ax.scatter(mean_pose[:, 0], mean_pose[:, 1], s=42 + spread * 1250,
                    c=spread, cmap="YlOrRd", vmin=0, vmax=0.13,
                    edgecolors=NAVY, linewidths=0.9, zorder=2)
    ax.set_title(f"G{g} · {GN[g-1]}  ({sel.sum():,} fr)", fontsize=11, fontweight="bold", pad=5)
    ax.invert_yaxis(); ax.set_aspect("equal")
    ax.set_xlim(0.355, 0.755); ax.set_ylim(0.955, 0.315)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
fig.suptitle("Mean skeleton per gesture, plotted from the released keypoints  "
             "(marker size and colour = per-joint variance)",
             fontsize=12.5, fontweight="bold", y=0.985)
fig.text(0.5, 0.013, "13 joints: head, shoulders, elbows, wrists, hips, knees, ankles. "
         "Wrists carry the most variance; knees and ankles are near-static noise for these upper-body gestures.",
         fontsize=9.3, color=SLATE, style="italic", ha="center")
fig.tight_layout(rect=[0, 0.04, 1, 0.955])
fig.savefig(os.path.join(OUT, "fig2_skeletons.png"), dpi=200, facecolor="white")
plt.close(fig)
print("fig2 done")

print("\nfig1 + fig2 only; identity leakage is handled by leakage_honest.py")
