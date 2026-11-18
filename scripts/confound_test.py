"""Is the 58.1% identity result a positional artifact?

The released coordinates look frame-normalised (means ~0.4-0.9), not torso-centred, so
absolute position in the frame may be encoded. If each participant stood in a slightly
different spot, an attacker could identify them from WHERE they are rather than from body
geometry - a recording artifact, not a biometric.

This re-runs the cross-gesture attack under four representations of increasing invariance:
  raw        - as released
  centred    - hip-midpoint subtracted (translation invariant)
  cen+scaled - also divided by shoulder width (translation + scale invariant)
  velocity   - frame differences only (no absolute position at all)

Also reports a gesture-balanced variant (equal windows per gesture per client).

Usage: python3 -I confound_test.py <keypoints_dir>
"""
import sys, os, json
import numpy as np

ROOT = sys.argv[1]
W = 20
rng = np.random.default_rng(0)

# joint indices recovered empirically (see explore.py)
HEAD, RSH, LSH = 0, 1, 2
RHIP, LHIP = 7, 8

def load_all(c):
    out = []
    for sp in ("train", "val", "test"):
        X = np.loadtxt(os.path.join(ROOT, f"client_{c}", f"x_{sp}.txt"), delimiter=",")
        Y = np.loadtxt(os.path.join(ROOT, f"client_{c}", f"y_{sp}.txt"), delimiter=",", dtype=int)
        out.append((X, Y))
    return out

RAW = {c: load_all(c) for c in range(1, 6)}

def transform(win, mode):
    """win: (W,26) -> (W,13,2) -> transformed -> flat"""
    P = win.reshape(W, 13, 2).copy()
    if mode == "raw":
        pass
    elif mode in ("centred", "cen+scaled"):
        hip = (P[:, RHIP] + P[:, LHIP]) / 2.0            # (W,2)
        P = P - hip[:, None, :]
        if mode == "cen+scaled":
            sh = np.linalg.norm(P[:, RSH] - P[:, LSH], axis=1)  # (W,)
            sh = np.maximum(sh, 1e-3)
            P = P / sh[:, None, None]
    elif mode == "velocity":
        P = np.diff(P, axis=0)                            # (W-1,13,2)
    else:
        raise ValueError(mode)
    return P.ravel()

def windows(gestures, mode, stride, cap_per_cell=None):
    Xo, co = [], []
    for c in range(1, 6):
        per_g = {}
        for X, Y in RAW[c]:
            g = Y[:, 0]
            for s in range(0, len(X) - W + 1, stride):
                if g[s] != g[s + W - 1] or g[s] not in gestures:
                    continue
                per_g.setdefault(g[s], []).append(transform(X[s:s + W], mode))
        for gg, lst in per_g.items():
            if cap_per_cell is not None and len(lst) > cap_per_cell:
                idx = rng.choice(len(lst), cap_per_cell, replace=False)
                lst = [lst[i] for i in idx]
            Xo.extend(lst); co.extend([c - 1] * len(lst))
    return np.array(Xo), np.array(co)

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

def evaluate(mode, cap=None):
    folds = [([1, 2, 3, 4], [5, 6, 7, 8]), ([5, 6, 7, 8], [1, 2, 3, 4]),
             ([1, 3, 5, 7], [2, 4, 6, 8]), ([2, 4, 6, 8], [1, 3, 5, 7])]
    accs, majs = [], []
    for tr, te in folds:
        Xa, ca = windows(set(tr), mode, 3, cap)
        Xb, cb = windows(set(te), mode, 3, cap)
        mu, sd = Xa.mean(0), Xa.std(0) + 1e-8
        Wt = softmax_fit((Xa - mu) / sd, ca, 5)
        pred = np.argmax(np.hstack([(Xb - mu) / sd, np.ones((len(Xb), 1))]) @ Wt, 1)
        accs.append((pred == cb).mean())
        majs.append(np.bincount(cb, minlength=5).max() / len(cb))
    return np.mean(accs), np.std(accs), np.mean(majs)

print("=== POSITIONAL CONFOUND TEST: cross-gesture subject ID, 5-way, chance 20% ===\n")
print(f"{'representation':<14}{'invariance':<34}{'accuracy':>12}{'majority':>11}")
print("-" * 71)
INV = {"raw": "none (as released)",
       "centred": "translation (hip-centred)",
       "cen+scaled": "translation + scale",
       "velocity": "position removed entirely"}
res = {}
for mode in ("raw", "centred", "cen+scaled", "velocity"):
    a, s, m = evaluate(mode)
    res[mode] = {"acc": float(a), "sd": float(s), "maj": float(m)}
    print(f"{mode:<14}{INV[mode]:<34}{a*100:>8.1f} ±{s*100:<3.1f}{m*100:>10.1f}%")

print("\n=== gesture-balanced (equal windows per gesture per client) ===")
for mode in ("raw", "cen+scaled"):
    a, s, m = evaluate(mode, cap=60)
    res[mode + "_balanced"] = {"acc": float(a), "sd": float(s), "maj": float(m)}
    print(f"{mode:<14}{'balanced cells':<34}{a*100:>8.1f} ±{s*100:<3.1f}{m*100:>10.1f}%")

# how much absolute position varies between subjects
print("\n=== subject mean hip position (frame-normalised coords) ===")
for c in range(1, 6):
    P = np.vstack([X for X, _ in RAW[c]]).reshape(-1, 13, 2)
    hip = (P[:, RHIP] + P[:, LHIP]) / 2.0
    print(f"  client {c}: hip x = {hip[:,0].mean():.3f} ± {hip[:,0].std():.3f}   "
          f"hip y = {hip[:,1].mean():.3f} ± {hip[:,1].std():.3f}")
sh = []
for c in range(1, 6):
    P = np.vstack([X for X, _ in RAW[c]]).reshape(-1, 13, 2)
    sh.append(np.linalg.norm(P[:, RSH] - P[:, LSH], axis=1).mean())
print("  mean shoulder width per client:", " ".join(f"{v:.3f}" for v in sh))

json.dump(res, open("confound_results.json", "w"), indent=2)
print("\nsaved confound_results.json")
