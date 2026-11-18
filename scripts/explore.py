"""Explore FederatedHAR: infer joint layout, per-client/gesture distribution."""
import sys, os
import numpy as np

ROOT = sys.argv[1]

def load(split_x, split_y):
    X = np.loadtxt(split_x, delimiter=",")
    Y = np.loadtxt(split_y, delimiter=",", dtype=int)
    return X, Y

# per-client train data
parts = []
for c in range(1, 6):
    X, Y = load(os.path.join(ROOT, f"client_{c}", "x_train.txt"),
                os.path.join(ROOT, f"client_{c}", "y_train.txt"))
    print(f"client_{c}: X{X.shape} Y{Y.shape}  gesture range {Y[:,0].min()}-{Y[:,0].max()}  "
          f"client col unique {np.unique(Y[:,1])}")
    parts.append((X, Y))

Xall = np.vstack([p[0] for p in parts])
Yall = np.vstack([p[1] for p in parts])
print("\nTOTAL train:", Xall.shape, "  coord range", Xall.min().round(3), Xall.max().round(3))

# ---- infer joint layout from mean positions (assume interleaved x,y pairs)
P = Xall.reshape(-1, 13, 2)
mx, my = P[:, :, 0].mean(0), P[:, :, 1].mean(0)
sx, sy = P[:, :, 0].std(0), P[:, :, 1].std(0)
print("\njoint |  mean x  mean y |  std x  std y   (y larger = lower in frame)")
for j in range(13):
    print(f"  {j:2d}  |  {mx[j]:.3f}   {my[j]:.3f}  |  {sx[j]:.3f}  {sy[j]:.3f}")

order = np.argsort(my)
print("\njoints sorted top->bottom by mean y:", order.tolist())

# ---- per-client x per-gesture frame counts
print("\nframe counts  rows=client, cols=gesture 1..8")
counts = np.zeros((5, 8), dtype=int)
for c in range(1, 6):
    Y = parts[c - 1][1]
    for g in range(1, 9):
        counts[c - 1, g - 1] = int(((Y[:, 0] == g)).sum())
print(counts)
print("row totals:", counts.sum(1), " grand total:", counts.sum())
np.save("/tmp/counts.npy", counts)
