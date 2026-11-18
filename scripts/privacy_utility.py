"""Privacy-utility trade-off of coordinate normalisation.

The confound test showed most identity leakage in the released representation is positional.
This asks the question that matters: if you remove absolute position, do you keep gesture
accuracy? If yes, normalisation is a free privacy defense.

Identity  = 5-way subject ID, cross-gesture transfer (attacker never sees the test gesture).
Utility   = 8-way gesture classification, released train split -> released test split.

Both use the same linear probe so the comparison is apples-to-apples.

Usage: python3 -I privacy_utility.py <keypoints_dir>
"""
import sys, os, json
import numpy as np

ROOT = sys.argv[1]
W = 20
rng = np.random.default_rng(0)
RSH, LSH, RHIP, LHIP = 1, 2, 7, 8

def load(c, sp):
    X = np.loadtxt(os.path.join(ROOT, f"client_{c}", f"x_{sp}.txt"), delimiter=",")
    Y = np.loadtxt(os.path.join(ROOT, f"client_{c}", f"y_{sp}.txt"), delimiter=",", dtype=int)
    return X, Y

DATA = {sp: {c: load(c, sp) for c in range(1, 6)} for sp in ("train", "test")}
ALL = {c: [DATA["train"][c], DATA["test"][c]] for c in range(1, 6)}

def transform(win, mode):
    P = win.reshape(W, 13, 2).copy()
    if mode == "raw":
        pass
    elif mode == "centred":
        hip = (P[:, RHIP] + P[:, LHIP]) / 2.0
        P = P - hip[:, None, :]
    elif mode == "cen+scaled":
        hip = (P[:, RHIP] + P[:, LHIP]) / 2.0
        P = P - hip[:, None, :]
        sh = np.maximum(np.linalg.norm(P[:, RSH] - P[:, LSH], axis=1), 1e-3)
        P = P / sh[:, None, None]
    elif mode == "velocity":
        P = np.diff(P, axis=0)
    return P.ravel()

def softmax_fit(Z, y, k, iters=700, lr=0.5, l2=3e-3):
    n, d = Z.shape
    Zb = np.hstack([Z, np.ones((n, 1))])
    Wt = np.zeros((d + 1, k)); vel = np.zeros_like(Wt); Yh = np.eye(k)[y]
    for _ in range(iters):
        s = Zb @ Wt; s -= s.max(1, keepdims=True)
        p = np.exp(s); p /= p.sum(1, keepdims=True)
        gr = Zb.T @ (p - Yh) / n; gr[:-1] += l2 * Wt[:-1]
        vel = 0.9 * vel - lr * gr; Wt += vel
    return Wt

def fit_eval(Xa, ya, Xb, yb, k):
    mu, sd = Xa.mean(0), Xa.std(0) + 1e-8
    Wt = softmax_fit((Xa - mu) / sd, ya, k)
    pred = np.argmax(np.hstack([(Xb - mu) / sd, np.ones((len(Xb), 1))]) @ Wt, 1)
    acc = (pred == yb).mean()
    f1s = []
    for c in range(k):
        tp = ((pred == c) & (yb == c)).sum(); fp = ((pred == c) & (yb != c)).sum()
        fn = ((pred != c) & (yb == c)).sum()
        pr = tp / (tp + fp) if tp + fp else 0.0
        rc = tp / (tp + fn) if tp + fn else 0.0
        f1s.append(2 * pr * rc / (pr + rc) if pr + rc else 0.0)
    return acc, float(np.mean(f1s))

# ---------------- utility: 8-way gesture, released splits
def gesture_windows(split, mode, stride):
    Xo, go = [], []
    for c in range(1, 6):
        X, Y = DATA[split][c]
        g = Y[:, 0]
        for s in range(0, len(X) - W + 1, stride):
            if g[s] != g[s + W - 1]:
                continue
            Xo.append(transform(X[s:s + W], mode)); go.append(g[s] - 1)
    return np.array(Xo), np.array(go)

# ---------------- privacy: 5-way subject, cross-gesture
def id_windows(gestures, mode, stride):
    Xo, co = [], []
    for c in range(1, 6):
        for X, Y in ALL[c]:
            g = Y[:, 0]
            for s in range(0, len(X) - W + 1, stride):
                if g[s] != g[s + W - 1] or g[s] not in gestures:
                    continue
                Xo.append(transform(X[s:s + W], mode)); co.append(c - 1)
    return np.array(Xo), np.array(co)

FOLDS = [([1, 2, 3, 4], [5, 6, 7, 8]), ([5, 6, 7, 8], [1, 2, 3, 4]),
         ([1, 3, 5, 7], [2, 4, 6, 8]), ([2, 4, 6, 8], [1, 3, 5, 7])]

print("=== PRIVACY-UTILITY TRADE-OFF OF COORDINATE NORMALISATION ===")
print("identity: 5-way subject ID, cross-gesture transfer (chance 20%, majority 26.6%)")
print("utility : 8-way gesture, released train->test splits (chance 12.5%)\n")
print(f"{'representation':<14}{'identity acc':>14}{'gesture acc':>14}{'gesture F1':>13}")
print("-" * 55)

out = {}
for mode in ("raw", "centred", "cen+scaled", "velocity"):
    ids = []
    for tr, te in FOLDS:
        Xa, ca = id_windows(set(tr), mode, 3)
        Xb, cb = id_windows(set(te), mode, 3)
        a, _ = fit_eval(Xa, ca, Xb, cb, 5)
        ids.append(a)
    Xa, ga = gesture_windows("train", mode, 3)
    Xb, gb = gesture_windows("test", mode, 1)
    gacc, gf1 = fit_eval(Xa, ga, Xb, gb, 8)
    out[mode] = {"id": float(np.mean(ids)), "id_sd": float(np.std(ids)),
                 "gesture_acc": float(gacc), "gesture_f1": float(gf1)}
    print(f"{mode:<14}{np.mean(ids)*100:>9.1f} ±{np.std(ids)*100:<3.1f}"
          f"{gacc*100:>13.1f}%{gf1*100:>12.1f}%")

print("\ninterpretation:")
r, cs = out["raw"], out["cen+scaled"]
print(f"  hip-centring + scale normalisation cuts identity leakage by "
      f"{(r['id']-cs['id'])*100:.1f} points ({r['id']*100:.1f}% -> {cs['id']*100:.1f}%)")
print(f"  gesture accuracy changes by {(cs['gesture_acc']-r['gesture_acc'])*100:+.1f} points "
      f"({r['gesture_acc']*100:.1f}% -> {cs['gesture_acc']*100:.1f}%)")
print("  NOTE: gesture numbers are inflated by temporal adjacency in the 88/6/6 within-block")
print("        split, but the inflation is identical across representations, so the")
print("        comparison between rows is valid even though the absolute level is not.")

json.dump(out, open("privacy_utility.json", "w"), indent=2)
print("\nsaved privacy_utility.json")
