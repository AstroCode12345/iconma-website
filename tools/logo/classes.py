from lib import *
INK = {
  "G":  (13, 94, 31),    # mid green (mark)
  "Au": (198, 155, 55),  # gold
  "D":  (18, 56, 28),    # dark green (wordmark, caption)
  "L":  (87, 145, 76),   # light green (url line)
}
def class_maps(img):
    names = list(INK)
    res = np.stack([residual(img, INK[k]) for k in names])
    cov = np.stack([coverage(img, INK[k]) for k in names])
    best = res.argmin(0)
    dist = np.linalg.norm(img - BG, axis=-1)
    out = {}
    for i, k in enumerate(names):
        m = (best == i) & (dist > 6)
        out[k] = np.where(m, cov[i], 0.0)
    return out
