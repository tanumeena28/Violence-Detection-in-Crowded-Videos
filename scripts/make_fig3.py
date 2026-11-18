"""Rebuild fig3 as a privacy-utility figure from privacy_utility.json.

Replaces the earlier (positionally confounded) 58.1% headline with the corrected result:
most leakage in the released representation is absolute position, and hip-centring removes
it almost for free.

Usage: python3 -I make_fig3.py <json_path> <out_dir>
"""
import sys, os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

JS, OUT = sys.argv[1], sys.argv[2]
R = json.load(open(JS))
NAVY, TEAL, ORANGE, BLUE, AMBER, SLATE = "#1A2347", "#00A896", "#E8552F", "#5B7FD4", "#F2A93B", "#7C8AA8"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": "#C9D2E3",
                     "text.color": NAVY, "xtick.color": NAVY, "ytick.color": NAVY,
                     "axes.labelcolor": NAVY})

MODES = [("raw", "As released\n(raw coords)", ORANGE),
         ("centred", "Hip-centred", TEAL),
         ("cen+scaled", "Hip-centred\n+ scaled", TEAL),
         ("velocity", "Velocity only", SLATE)]
CHANCE, MAJ = 20.0, 26.6

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.6, 5.0), gridspec_kw={"width_ratios": [1.05, 1]})

# ---------------- left: identity leakage by representation
xs = np.arange(len(MODES))
vals = [R[m]["id"] * 100 for m, _, _ in MODES]
errs = [R[m]["id_sd"] * 100 for m, _, _ in MODES]
cols = [c for _, _, c in MODES]
ax1.bar(xs, vals, color=cols, width=0.6, zorder=2)
ax1.errorbar(xs, vals, yerr=errs, fmt="none", ecolor=NAVY, capsize=5, lw=1.3, zorder=3)
for i, v in enumerate(vals):
    ax1.text(i, v + errs[i] + 2.4, f"{v:.1f}%", ha="center", fontsize=12, fontweight="bold", color=cols[i])
ax1.axhline(MAJ, color=SLATE, ls="-", lw=1.1, zorder=1)
ax1.axhline(CHANCE, color=SLATE, ls="--", lw=1.1, zorder=1)
ax1.set_xlim(-0.62, 4.25)
ax1.text(4.18, MAJ + 1.4, "majority class", fontsize=8.4, color="#5A6B86", ha="right")
ax1.text(4.18, CHANCE - 4.0, "chance", fontsize=8.4, color="#5A6B86", ha="right")
ax1.set_xticks(xs); ax1.set_xticklabels([l for _, l, _ in MODES], fontsize=9)
ax1.set_ylim(0, 88); ax1.set_ylabel("Subject identification accuracy (%)", fontsize=9.5)
ax1.set_title("Most leakage is absolute position, not body shape", fontsize=10.8, fontweight="bold", pad=8)
ax1.grid(axis="y", alpha=0.16, color=SLATE, zorder=0)
ax1.annotate("", xy=(0.93, 43), xytext=(0.42, 62),
             arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.6))
ax1.text(0.80, 64, f"-{vals[0]-vals[1]:.0f} points", ha="center", fontsize=10.5,
         fontweight="bold", color=NAVY)
for sp in ax1.spines.values():
    sp.set_color("#C9D2E3")

# ---------------- right: privacy vs utility
for m in ("raw", "centred", "cen+scaled", "velocity"):
    c = ORANGE if m == "raw" else (SLATE if m == "velocity" else TEAL)
    ax2.scatter(R[m]["id"] * 100, R[m]["gesture_acc"] * 100, s=200, c=c,
                edgecolors=NAVY, linewidths=1.3, zorder=3)
ax2.annotate("As released", (R["raw"]["id"] * 100, R["raw"]["gesture_acc"] * 100),
             textcoords="offset points", xytext=(0, 17), ha="center",
             fontsize=9.5, fontweight="bold", color=NAVY, zorder=4)
ax2.annotate("Hip-centred\n(\u00B1 scaling)", (35.25, 97.5), textcoords="offset points",
             xytext=(-46, 2), ha="center", va="center", fontsize=9.5, fontweight="bold",
             color=NAVY, zorder=4)
ax2.annotate("Velocity only", (R["velocity"]["id"] * 100, R["velocity"]["gesture_acc"] * 100),
             textcoords="offset points", xytext=(52, 0), ha="center", va="center",
             fontsize=9.5, fontweight="bold", color=NAVY, zorder=4)
ax2.axvline(CHANCE, color=SLATE, ls="--", lw=1.1, zorder=1)
ax2.text(CHANCE + 2.0, 58, "chance identity", fontsize=8.4, color="#5A6B86", rotation=90, va="center")
ax2.set_xlim(13, 74); ax2.set_ylim(2, 122)
ax2.set_yticks([20, 40, 60, 80, 100])
ax2.set_xlabel("Identity leakage \u2014 subject ID accuracy (%)", fontsize=9.5)
ax2.set_ylabel("Utility \u2014 gesture accuracy (%)", fontsize=9.5)
ax2.set_title("Hip-centring is a near-free defense", fontsize=10.8, fontweight="bold", pad=8)
ax2.grid(alpha=0.16, color=SLATE, zorder=0)
for sp in ax2.spines.values():
    sp.set_color("#C9D2E3")

fig.suptitle("Identity leakage in the \"anonymous\" skeleton representation is largely positional, and removable",
             fontsize=12.3, fontweight="bold", y=0.985)
fig.text(0.5, 0.072, "Linear probe on 26\u00D720 windows. Identity = 5-way subject ID, attacker trained and tested on disjoint gesture sets. Utility = 8-way gesture accuracy.",
         fontsize=8.9, color=SLATE, style="italic", ha="center")
fig.text(0.5, 0.040, "Hip-centring cuts leakage 59.3% \u2192 35.2% for 0.4 points of gesture accuracy. The two hip-centred variants nearly coincide. Velocity-only destroys the task.",
         fontsize=8.9, color=SLATE, style="italic", ha="center")
fig.text(0.5, 0.008, "Limitations: one session per subject, so this is identity-plus-session linkage. Absolute gesture accuracy is inflated by temporal adjacency; row-to-row comparisons remain valid.",
         fontsize=8.9, color=SLATE, style="italic", ha="center")
fig.tight_layout(rect=[0, 0.10, 1, 0.945])
fig.savefig(os.path.join(OUT, "fig3_leakage.png"), dpi=200, facecolor="white")
print("fig3 rebuilt as privacy-utility ->", OUT)
