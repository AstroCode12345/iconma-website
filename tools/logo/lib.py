import struct, numpy as np
BG = np.array([246.0, 248.0, 252.0])

def load(path):
    d = open(path, "rb").read()
    off = struct.unpack_from("<I", d, 10)[0]
    w, h = struct.unpack_from("<ii", d, 18)
    bpp = struct.unpack_from("<H", d, 28)[0]; Bpp = bpp // 8
    flip = h > 0; h = abs(h)
    row = (w * Bpp + 3) // 4 * 4
    a = np.frombuffer(d, np.uint8, count=row * h, offset=off).reshape(h, row)[:, : w * Bpp].reshape(h, w, Bpp)
    a = a[:, :, [2, 1, 0]].astype(float)
    if flip: a = a[::-1]
    return a

def coverage(img, ink):
    """per-pixel fraction of `ink` over BG (0..1), by projection."""
    ink = np.asarray(ink, float)
    v = ink - BG
    return np.clip(((img - BG) @ v) / (v @ v), 0, 1)

def residual(img, ink):
    ink = np.asarray(ink, float)
    v = ink - BG
    a = np.clip(((img - BG) @ v) / (v @ v), 0, 1)[..., None]
    return np.linalg.norm(img - (BG + a * v), axis=-1)
