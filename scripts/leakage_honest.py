"""Honest identity-leakage test: cross-gesture transfer.

The 88/6/6 split is stratified WITHIN contiguous gesture blocks, so test frames sit
temporally adjacent to train frames. A within-split probe can therefore near-memorise.
This script instead trains the attacker on one disjoint set of gestures and evaluates on
another, so no train window is temporally adjacent to any test window and the motion
itself differs.

Usage: python3 -I leakage_honest.py <keypoints_dir> <out_dir>
"""
import sys, os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
NAVY, TEAL, ORANGE, BLUE, AMBER, SLATE = "#1A2347", "#00A896", "#E8552F", "#5B7FD4", "#F2A93B", "#7C8AA8"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": "#C9D2E3",
                     "text.color": NAVY, "xtick.color": NAVY, "ytick.color": NAVY,
                     "axes.labelcolor": NAVY})
GN = ["down", "grab", "left", "nothing", "right", "stop", "ungrab", "up"]
W = 20

def load_all(c):
    Xs, Ys = [], []
    for sp in ("train", "val", "test"):
        Xs.append(np.loadtxt(os.path.join(ROOT, f"client_{c}", f"x_{sp}.txt"), delimiter=","))
        Ys.append(np.loadtxt(os.path.join(ROOT, f"client_{c}", f"y_{sp}.txt"), delimiter=",", dtype=int))
    return Xs, Ys

RAW = {c: load_all(c) for c in range(1, 6)}

def windows_for(gestures, stride):
    """All windows whose gesture is in `gestures`, pooled over train/val/test files."""
    Xo, co, go = [], [], []
    for c in range(1, 6):
        Xs, Ys = RAW[c]
        for X, Y in zip(Xs, Ys):
            g = Y[:, 0]
            for s in range(0, len(X) - W + 1, stride):
                if g[s] != g[s + W - 1] or g[s] not in gestures:
                    continue
                Xo.append(X[s:s + W].ravel()); co.append(c - 1); go.append(g[s])
    return np.array(Xo), np.array(co), np.array(go)

def softmax_fit(Z, y, k, iters=1200, lr=0.5, l2=3e-3):
    n, d = Z.shape
    Zb = np.hstack([Z, np.ones((n, 1))])
    Wt = np.zeros((d + 1, k)); vel = np.zeros_like(Wt); Yh = np.eye(k)[y]
    for _ in range(iters):
        s = Zb @ Wt; s -= s.max(1, keepdims=True)
        p = np.exp(s); p /= p.sum(1, keepdims=True)
        gr = Zb.T @ (p - Yh) / n; gr[:-1] += l2 * Wt[:-1]
        vel = 0.9 * vel - lr * gr; Wt += vel
    return Wt

def run(train_g, test_g, tag):
    Xa, ca, _ = windows_for(set(train_g), 3)
    Xb, cb, _ = windows_for(set(test_g), 3)
    mu, sd = Xa.mean(0), Xa.std(0) + 1e-8
    Wt = softmax_fit((Xa - mu) / sd, ca, 5)
    pred = np.argmax(np.hstack([(Xb - mu) / sd, np.ones((len(Xb), 1))]) @ Wt, 1)
    acc = (pred == cb).mean()
    maj = np.bincount(cb, minlength=5).max() / len(cb)
    print(f"{tag:<34} train {len(Xa):>5}w  test {len(Xb):>5}w   acc {acc*100:5.1f}%   "
          f"(majority {maj*100:.1f}%)")
    return acc, maj, len(Xa), len(Xb), pred, cb

print("=== CROSS-GESTURE SUBJECT IDENTIFICATION (5-way) ===")
print("attacker never sees the gesture it is tested on; no temporal adjacency\n")
folds = [([1, 2, 3, 4], [5, 6, 7, 8], "train G1-G4 -> test G5-G8"),
         ([5, 6, 7, 8], [1, 2, 3, 4], "train G5-G8 -> test G1-G4"),
         ([1, 3, 5, 7], [2, 4, 6, 8], "train odd G  -> test even G"),
         ([2, 4, 6, 8], [1, 3, 5, 7], "train even G -> test odd G")]
res = [run(a, b, t) for a, b, t in folds]
accs = np.array([r[0] for r in res]); majs = np.array([r[1] for r in res])
print(f"\nmean cross-gesture accuracy : {accs.mean()*100:.1f}%  (sd {accs.std()*100:.1f})")
print(f"mean majority-class baseline: {majs.mean()*100:.1f}%")
print(f"chance                      : 20.0%")

# leave-one-gesture-out: train on 7 gestures, test on the held-out one
print("\n=== LEAVE-ONE-GESTURE-OUT ===")
loo = {}
for g in range(1, 9):
    others = [x for x in range(1, 9) if x != g]
    a, m, _, _, _, _ = run(others, [g], f"hold out G{g} ({GN[g-1]})")
    loo[g] = a
loo_mean = float(np.mean(list(loo.values())))
print(f"\nmean leave-one-gesture-out  : {loo_mean*100:.1f}%")

# ---------------------------------------------------------------- figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.2, 4.8), gridspec_kw={"width_ratios": [1, 1.25]})

bars = [("Chance\n(uniform)", 20.0, SLATE),
        ("Majority\nclass", majs.mean() * 100, SLATE),
        ("Cross-gesture\ntransfer", accs.mean() * 100, ORANGE),
        ("Leave-one-\ngesture-out", loo_mean * 100, ORANGE)]
xs = np.arange(len(bars))
ax1.bar(xs, [b[1] for b in bars], color=[b[2] for b in bars], width=0.6, zorder=2)
ax1.errorbar(2, accs.mean() * 100, yerr=accs.std() * 100, color=NAVY, capsize=5, lw=1.4, zorder=3)
for i, b in enumerate(bars):
    off = accs.std() * 100 + 2.6 if i == 2 else 2.6
    ax1.text(i, b[1] + off, f"{b[1]:.1f}%", ha="center", fontsize=11.5, fontweight="bold", color=b[2])
ax1.axhline(20, color=SLATE, ls="--", lw=1.1, zorder=1)
ax1.set_xticks(xs); ax1.set_xticklabels([b[0] for b in bars], fontsize=8.8)
ax1.set_ylim(0, 112); ax1.set_ylabel("Subject identification accuracy (%)", fontsize=9.5)
ax1.set_title("Identity survives a gesture change", fontsize=10.5, fontweight="bold", pad=8)
ax1.grid(axis="y", alpha=0.16, color=SLATE, zorder=0)
for sp in ax1.spines.values():
    sp.set_color("#C9D2E3")

gl = list(range(1, 9))
ax2.bar([g - 0.0 for g in gl], [loo[g] * 100 for g in gl], color=TEAL, width=0.62, zorder=2)
for g in gl:
    ax2.text(g, loo[g] * 100 + 2.4, f"{loo[g]*100:.0f}", ha="center", fontsize=9.5,
             fontweight="bold", color=TEAL)
ax2.axhline(20, color=SLATE, ls="--", lw=1.1, zorder=1, label="chance (20%)")
ax2.set_xticks(gl); ax2.set_xticklabels([f"G{g}\n{GN[g-1]}" for g in gl], fontsize=8.5)
ax2.set_ylim(0, 112); ax2.set_ylabel("Accuracy (%)", fontsize=9.5)
ax2.set_title("Leave-one-gesture-out: identified from an unseen motion",
              fontsize=10.5, fontweight="bold", pad=8)
ax2.legend(fontsize=9, frameon=False, loc="upper left")
ax2.grid(axis="y", alpha=0.16, color=SLATE, zorder=0)
for sp in ax2.spines.values():
    sp.set_color("#C9D2E3")

fig.suptitle("Subject identity is recoverable from the \"anonymous\" skeleton representation",
             fontsize=12.5, fontweight="bold", y=0.985)
fig.text(0.5, 0.075,
         "Linear probe (multinomial logistic regression) on standardised 26x20 keypoint windows, 5-way subject ID.",
         fontsize=9.3, color=SLATE, style="italic", ha="center")
fig.text(0.5, 0.043,
         "Attacker trained and tested on disjoint gesture sets: no test window is temporally adjacent to a training window, and the motion differs.",
         fontsize=9.3, color=SLATE, style="italic", ha="center")
fig.text(0.5, 0.011,
         "Limitation: one recording session per subject, so this measures identity-plus-session linkage, not cross-session re-identification.",
         fontsize=9.3, color=SLATE, style="italic", ha="center")
fig.tight_layout(rect=[0, 0.10, 1, 0.945])
fig.savefig(os.path.join(OUT, "fig3_leakage.png"), dpi=200, facecolor="white")
plt.close(fig)

json.dump({"cross_gesture_mean": float(accs.mean()), "cross_gesture_sd": float(accs.std()),
           "majority_mean": float(majs.mean()), "loo_mean": loo_mean,
           "loo": {str(k): float(v) for k, v in loo.items()}},
          open(os.path.join(OUT, "leakage.json"), "w"), indent=2)
print("\nfig3 rewritten ->", OUT)
