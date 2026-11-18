import numpy as np, math

# ---------- marching squares (sub-pixel contours at an iso level) ----------
_SEG = {1:[("L","B")],2:[("B","R")],3:[("L","R")],4:[("T","R")],6:[("T","B")],7:[("T","L")],
        8:[("T","L")],9:[("T","B")],11:[("T","R")],12:[("L","R")],13:[("B","R")],14:[("L","B")]}
def contours(f, iso=0.5, x0=0, y0=0):
    """closed loops of the f==iso contour, as arrays of (x,y) in image px (pixel centres at +0.5)."""
    H, W = f.shape
    inside = f >= iso
    tl = inside[:-1, :-1]; tr = inside[:-1, 1:]; br = inside[1:, 1:]; bl = inside[1:, :-1]
    case = tl*8 + tr*4 + br*2 + bl*1
    ii, jj = np.nonzero((case != 0) & (case != 15))
    segs = []
    for i, j in zip(ii, jj):
        c = int(case[i, j])
        if c in (5, 10):
            center = (f[i,j] + f[i,j+1] + f[i+1,j+1] + f[i+1,j]) / 4 >= iso
            if c == 5:   pairs = [("T","L"),("B","R")] if center else [("T","R"),("L","B")]
            else:        pairs = [("T","R"),("L","B")] if center else [("T","L"),("B","R")]
        else:
            pairs = _SEG[c]
        for a, b in pairs:
            segs.append((_eid(a, i, j), _eid(b, i, j)))
    adj = {}
    for a, b in segs:
        adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
    def pt(e):
        k, i, j = e
        if k == "h":
            a, b = f[i, j], f[i, j+1]; t = (iso - a) / (b - a); return (j + t + 0.5 + x0, i + 0.5 + y0)
        a, b = f[i, j], f[i+1, j]; t = (iso - a) / (b - a); return (j + 0.5 + x0, i + t + 0.5 + y0)
    seen = set(); loops = []
    for start in adj:
        if start in seen: continue
        loop = [start]; seen.add(start); prev = None; cur = start
        while True:
            nxt = [n for n in adj[cur] if n != prev and n not in seen]
            if not nxt:
                break
            prev, cur = cur, nxt[0]; seen.add(cur); loop.append(cur)
        loops.append(np.array([pt(e) for e in loop]))
    return loops
def _eid(side, i, j):
    return {"T":("h",i,j), "B":("h",i+1,j), "L":("v",i,j), "R":("v",i,j+1)}[side]

def area(p):
    x, y = p[:,0], p[:,1]; return 0.5 * np.sum(x*np.roll(y,-1) - np.roll(x,-1)*y)

# ---------- circles ----------
def fit_circle(p, w=None, iters=20):
    p = np.asarray(p, float); w = np.ones(len(p)) if w is None else np.asarray(w, float)
    x, y = p[:,0], p[:,1]
    A = np.c_[2*x, 2*y, np.ones(len(x))]; b = x*x + y*y
    sol = np.linalg.lstsq(A * w[:,None]**.5, b * w**.5, rcond=None)[0]
    cx, cy = sol[0], sol[1]; r = math.sqrt(max(sol[2] + cx*cx + cy*cy, 1e-9))
    for _ in range(iters):
        d = np.hypot(x-cx, y-cy); res = d - r
        J = np.c_[-(x-cx)/d, -(y-cy)/d, -np.ones(len(x))]
        step = np.linalg.lstsq(J * w[:,None]**.5, -res * w**.5, rcond=None)[0]
        cx += step[0]; cy += step[1]; r += step[2]
        if abs(step).max() < 1e-7: break
    d = np.hypot(x-cx, y-cy)
    return cx, cy, r, float(np.sqrt(np.average((d-r)**2, weights=w)))

def ransac_circle(p, tol=0.7, iters=3000, seed=1, rmin=5, rmax=1e4):
    rng = np.random.default_rng(seed); best = None; n = len(p)
    for _ in range(iters):
        a, b, c = p[rng.choice(n, 3, replace=False)]
        d = 2*(a[0]*(b[1]-c[1]) + b[0]*(c[1]-a[1]) + c[0]*(a[1]-b[1]))
        if abs(d) < 1e-9: continue
        ux = ((a@a)*(b[1]-c[1]) + (b@b)*(c[1]-a[1]) + (c@c)*(a[1]-b[1])) / d
        uy = ((a@a)*(c[0]-b[0]) + (b@b)*(a[0]-c[0]) + (c@c)*(b[0]-a[0])) / d
        r = math.hypot(a[0]-ux, a[1]-uy)
        if not (rmin < r < rmax): continue
        inl = np.abs(np.hypot(p[:,0]-ux, p[:,1]-uy) - r) < tol
        if best is None or inl.sum() > best.sum(): best = inl
    cx, cy, r, rms = fit_circle(p[best]); 
    inl = np.abs(np.hypot(p[:,0]-cx, p[:,1]-cy) - r) < tol
    cx, cy, r, rms = fit_circle(p[inl])
    return (cx, cy, r, rms), inl

# ---------- lines ----------
def fit_line(p):
    """total least squares: returns point on line (centroid) and unit direction"""
    p = np.asarray(p, float); c = p.mean(0)
    u, s, vt = np.linalg.svd(p - c); return c, vt[0]
def intersect(l1, l2):
    (p1, d1), (p2, d2) = l1, l2
    A = np.array([d1, -d2]).T
    t = np.linalg.solve(A, p2 - p1); return p1 + t[0]*d1
def dist_to_line(p, line):
    c, d = line; v = p - c; return np.abs(v[:,0]*d[1] - v[:,1]*d[0])

# ---------- Ramer-Douglas-Peucker (closed loop) ----------
def rdp(pts, eps):
    pts = np.asarray(pts, float)
    if len(pts) < 3: return pts
    a, b = pts[0], pts[-1]
    d = dist_to_line(pts[1:-1], (a, (b-a)/max(np.linalg.norm(b-a),1e-9)))
    i = int(np.argmax(d)) + 1
    if d[i-1] > eps:
        l = rdp(pts[:i+1], eps); r = rdp(pts[i:], eps); return np.vstack([l[:-1], r])
    return np.array([a, b])
def rdp_closed(pts, eps):
    pts = np.asarray(pts, float)
    # split at the two points farthest apart so neither end is a smooth point by accident
    i = int(np.argmax(np.linalg.norm(pts - pts[0], axis=1)))
    a = rdp(pts[:i+1], eps); b = rdp(np.vstack([pts[i:], pts[:1]]), eps)
    return np.vstack([a[:-1], b[:-1]])
