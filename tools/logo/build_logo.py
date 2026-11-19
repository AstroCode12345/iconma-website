"""Measure the president's logo image and rebuild it as clean SVG.

The mark (dome, crescent, star) is circles, lines and a polygon fitted to the image. The lettering is
TRACED: each letter's outline is found at the 50 percent edge, split at its corners, and fitted with
smooth cubic curves. (Version 1 of the logo used DejaVu Sans, so its letters could be taken from the font;
this one is a different typeface, so it cannot.)

    sips -s format bmp _source/logo-original.webp --out /tmp/iconma-logo.bmp
    uv run --with numpy python tools/logo/build_logo.py /tmp/iconma-logo.bmp images
"""
import sys, os, json, math
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
import lib
from lib import load, coverage, residual
from geom import *

RASTER, OUT = sys.argv[1], sys.argv[2]
img = load(RASTER); H, W, _ = img.shape
lib.BG = np.median(img[5:40, 5:40].reshape(-1, 3), axis=0)
ys, xs = np.mgrid[0:H, 0:W]; px = xs + 0.5; py = ys + 0.5
f2 = lambda v: ("%.2f" % v).rstrip("0").rstrip(".")
hexof = lambda c: "#%02X%02X%02X" % tuple(int(round(v)) for v in c)

# ---------- 1. which ink is where ----------
# Rough colours (measured once); the final colours are re-measured below from solid pixels.
INK = {"G": (2, 81, 7), "Au": (202, 152, 4), "D": (1, 68, 5), "L": (65, 148, 17)}
dist = np.linalg.norm(img - lib.BG, axis=-1)
cov = {k: coverage(img, v) for k, v in INK.items()}
res = {k: residual(img, v) for k, v in INK.items()}
Y = ys; ink_ok = dist > 6
in_mark = Y < 470
green = res["G"] <= res["Au"]
C = {
    "G": np.where(in_mark & green & ink_ok, cov["G"], 0.0),
    "Au": np.where(((in_mark & ~green) | ((Y >= 790) & (Y < 840))) & ink_ok, cov["Au"], 0.0),
    "D": np.where((((Y >= 500) & (Y < 790)) | ((Y >= 860) & (Y < 960))) & ink_ok, cov["D"], 0.0),
    "L": np.where((Y >= 960) & ink_ok, cov["L"], 0.0),
}
G, Au = C["G"], C["Au"]

def solid(M, box=None):
    m = M >= 0.97
    if box: yy0, yy1, xx0, xx1 = box; z = np.zeros_like(m); z[yy0:yy1, xx0:xx1] = m[yy0:yy1, xx0:xx1]; m = z
    return tuple(float(v) for v in np.median(img[m], axis=0))
COL = {"G": hexof(solid(G)), "Au": hexof(solid(Au, (0, 470, 0, W))), "rule": hexof(solid(Au, (790, 840, 0, W))),
       "word": hexof(solid(C["D"], (500, 790, 0, W))), "name": hexof(solid(C["D"], (860, 960, 0, W))), "url": hexof(solid(C["L"]))}
print("colours", COL)

def edges_1d(prof, thr=0.5):
    idx = np.where(prof >= thr)[0]; a, b = idx[0], idx[-1]
    ra = a - 1 + (thr - prof[a - 1]) / (prof[a] - prof[a - 1]) if a > 0 else float(a)
    rb = b + (prof[b] - thr) / (prof[b] - prof[b + 1]) if b + 1 < len(prof) else float(b)
    return ra + 0.5, rb + 0.5

# ---------- 2. straight parts of the mark ----------
P = {}
band = G[415:460, 560:700].mean(1); e = edges_1d(band); P["base_y"] = (e[0] + e[1]) / 2 + 415
P["base_w"] = float(G[415:460, 560:700].sum(0).mean())
row = G[int(P["base_y"]) - 1:int(P["base_y"]) + 2, 400:1080].mean(0); e = edges_1d(row); P["base_x0"], P["base_x1"] = e[0] + 400, e[1] + 400
cp = G[200:400, 700:770].mean(0); e = edges_1d(cp); P["pillar_x"] = (e[0] + e[1]) / 2 + 700
P["pillar_w"] = float(G[200:400, 700:770].sum(1).mean())
vp = G[100:200, int(P["pillar_x"]) - 3:int(P["pillar_x"]) + 4].mean(1)
i0 = int(np.argmax(vp >= 0.5)); P["pillar_top"] = 100 + i0 - 1 + (0.5 - vp[i0 - 1]) / (vp[i0] - vp[i0 - 1]) + 0.5
for nm, x0, x1 in (("postL", 520, 565), ("postR", 905, 950)):
    cp = G[340:400, x0:x1].mean(0); e = edges_1d(cp); P[nm + "_x"] = (e[0] + e[1]) / 2 + x0
    P[nm + "_w"] = float(G[340:400, x0:x1].sum(1).mean())
    xi = int(round(P[nm + "_x"])); vp = G[260:350, xi - 2:xi + 3].mean(1); e = edges_1d(vp); P[nm + "_top"] = e[0] + 260
rp = Au[790:830, 100:1300].mean(1); e = edges_1d(rp); P["rule_y0"], P["rule_y1"] = e[0] + 790, e[1] + 790

# ---------- 3. arcs ----------
pillar_mask = (np.abs(px - P["pillar_x"]) < 12) & (py > 130)
def arc(M, guess, rlo, rhi, ymin):
    d = np.hypot(px - guess[0], py - guess[1])
    m = (M > 0.05) & (d > rlo) & (d < rhi) & (py > ymin) & (py < 306) & ~pillar_mask
    cx, cy, r, _ = fit_circle(np.c_[px[m], py[m]], M[m])
    d = np.hypot(px - cx, py - cy); th = np.arctan2(py - cy, px - cx)
    tot = 0; span = 0
    for a, b in ((-2.95, -2.0), (-1.1, -0.2)):
        s = (np.abs(d - r) < 14) & (th > a) & (th < b) & ~pillar_mask & (py > ymin)
        tot += M[s].sum(); span += (b - a)
    return cx, cy, r, tot / (r * span)
def refine(M, c, r, angles, rounds=3):
    """Re-fit a ring from where its two edges cross 50 percent along rays from the centre:
    the middle of each edge pair is a point on the centre line, and their distance is the stroke width."""
    cx_, cy_ = c
    for _ in range(rounds):
        pts, wid = [], []
        for a in angles:
            t = math.radians(a); rs = np.linspace(r - 18, r + 18, 361)
            xx = cx_ + rs * math.cos(t); yy = cy_ + rs * math.sin(t)
            x0_ = np.floor(xx - 0.5).astype(int); y0_ = np.floor(yy - 0.5).astype(int); fx = xx - 0.5 - x0_; fy = yy - 0.5 - y0_
            v = (M[y0_, x0_] * (1 - fx) * (1 - fy) + M[y0_, x0_ + 1] * fx * (1 - fy) + M[y0_ + 1, x0_] * (1 - fx) * fy + M[y0_ + 1, x0_ + 1] * fx * fy)
            on = rs[v >= 0.5]
            if len(on) < 2: continue
            lo, hi = on.min(), on.max(); rm = (lo + hi) / 2
            pts.append((cx_ + rm * math.cos(t), cy_ + rm * math.sin(t))); wid.append(hi - lo)
        cx_, cy_, r, _ = fit_circle(np.array(pts))
    return cx_, cy_, r, float(np.median(wid))
outer0 = arc(G, (733.8, 307.6), 200, 260, 60)
inner0 = arc(Au, (733.7, 300), 130, 185, 138)
ang_out = [a for a in range(-172, -8, 3) if not (-108 < a < -70)]
ang_in = [a for a in range(-172, -8, 3) if abs(a + 90) > 12]
P["outer"] = refine(G, outer0[:2], outer0[2], ang_out)
P["inner"] = refine(Au, inner0[:2], inner0[2], ang_in)
print("arc refit  outer", [round(v, 2) for v in outer0], "->", [round(v, 2) for v in P["outer"]])
print("arc refit  inner", [round(v, 2) for v in inner0], "->", [round(v, 2) for v in P["inner"]])
cx, cy, r, w = P["outer"]; d = np.hypot(px - cx, py - cy); th = np.degrees(np.arctan2(py - cy, px - cx))
cuts = {}
for side, lo, hi in (("L", -140, -85), ("R", -95, -40)):
    vals = []
    for rb in np.linspace(r - w / 2 + 1.5, r + w / 2 - 1.5, 5):
        s = (np.abs(d - rb) < 0.7) & (th > lo) & (th < hi); on = th[s][G[s] >= 0.5]
        vals.append(on.max() if side == "L" else on.min())
    cuts[side] = float(np.median(vals))
P["cutL"], P["cutR"] = cuts["L"], cuts["R"]

# ---------- 4. crescent and star ----------
x0, x1, y0, y1 = 660, 830, 10, 138
loops = sorted(contours(Au[y0:y1, x0:x1], 0.5, x0, y0), key=lambda l: -abs(area(l)))
cres, star = loops[0], loops[1]
oc, inl = ransac_circle(cres, tol=0.8, iters=4000, rmin=30); ic, _ = ransac_circle(cres[~inl], tol=0.8, iters=4000, rmin=20)
(ox, oy, cor, _), (ix, iy, cir, _) = oc, ic
d_ = math.hypot(ix - ox, iy - oy); a_ = (cor**2 - cir**2 + d_**2) / (2 * d_); h_ = math.sqrt(cor**2 - a_**2)
mx, my = ox + a_ * (ix - ox) / d_, oy + a_ * (iy - oy) / d_
tips = [(mx + h_ * (iy - oy) / d_, my - h_ * (ix - ox) / d_), (mx - h_ * (iy - oy) / d_, my + h_ * (ix - ox) / d_)]
sc = star.mean(0); R_, r_ = 26.1, 10.0
ideal = np.array([sc + (R_ if k % 2 == 0 else r_) * np.array([math.cos(math.radians(-90 + 36 * k)), math.sin(math.radians(-90 + 36 * k))]) for k in range(10)])
def seg_dist(p, a, b):
    ab = b - a; t = np.clip(((p - a) @ ab) / (ab @ ab), 0, 1); return np.linalg.norm(p - (a + t[:, None] * ab), axis=1), t
lines = []
for k in range(10):
    a, b = ideal[k], ideal[(k + 1) % 10]
    ds = np.stack([seg_dist(star, ideal[j], ideal[(j + 1) % 10])[0] for j in range(10)])
    mine = ds.argmin(0) == k; dd, t = seg_dist(star, a, b)
    sel = mine & (t > 0.18) & (t < 0.82) & (dd < 3)
    lines.append(fit_line(star[sel]))
corners = np.array([intersect(lines[k - 1], lines[k]) for k in range(10)])
print("star centre", corners.mean(0).round(1), "crescent circles", [round(v, 1) for v in (ox, oy, cor, ix, iy, cir)])

# ---------- 5. trace the lettering ----------
def unit(v): n = np.linalg.norm(v); return v / n if n > 1e-9 else v

def bez(c, t):
    t = np.asarray(t)[:, None]
    return (1 - t)**3 * c[0] + 3 * t * (1 - t)**2 * c[1] + 3 * t**2 * (1 - t) * c[2] + t**3 * c[3]

def gen_bezier(pts, u, t1, t2):
    p0, p3 = pts[0], pts[-1]
    b0, b1, b2, b3 = (1 - u)**3, 3 * u * (1 - u)**2, 3 * u**2 * (1 - u), u**3
    A1, A2 = t1[None, :] * b1[:, None], t2[None, :] * b2[:, None]
    Cm = np.array([[(A1 * A1).sum(), (A1 * A2).sum()], [(A1 * A2).sum(), (A2 * A2).sum()]])
    tmp = pts - (p0[None, :] * (b0 + b1)[:, None] + p3[None, :] * (b2 + b3)[:, None])
    X = np.array([(A1 * tmp).sum(), (A2 * tmp).sum()])
    det = Cm[0, 0] * Cm[1, 1] - Cm[0, 1] * Cm[1, 0]
    seg = np.linalg.norm(p3 - p0)
    if abs(det) > 1e-12:
        a1 = (X[0] * Cm[1, 1] - X[1] * Cm[0, 1]) / det; a2 = (Cm[0, 0] * X[1] - Cm[1, 0] * X[0]) / det
    else: a1 = a2 = seg / 3
    if a1 < 1e-6 * seg or a2 < 1e-6 * seg: a1 = a2 = seg / 3
    return np.array([p0, p0 + t1 * a1, p3 + t2 * a2, p3])

def reparam(c, pts, u):
    d = bez(c, u) - pts
    d1c = 3 * np.array([c[1] - c[0], c[2] - c[1], c[3] - c[2]]); d2c = 6 * np.array([c[2] - 2 * c[1] + c[0], c[3] - 2 * c[2] + c[1]])
    t = u[:, None]
    d1 = (1 - t)**2 * d1c[0] + 2 * t * (1 - t) * d1c[1] + t**2 * d1c[2]; d2 = (1 - t) * d2c[0] + t * d2c[1]
    num = (d * d1).sum(1); den = (d1 * d1).sum(1) + (d * d2).sum(1)
    return np.clip(np.where(np.abs(den) > 1e-9, u - num / den, u), 0, 1)

def fit_cubic(pts, t1, t2, err):
    if len(pts) == 2:
        s = np.linalg.norm(pts[1] - pts[0]) / 3; return [np.array([pts[0], pts[0] + t1 * s, pts[1] + t2 * s, pts[1]])]
    u = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]; u = u / u[-1]
    c = gen_bezier(pts, u, t1, t2)
    for _ in range(6):
        dd = np.linalg.norm(bez(c, u) - pts, axis=1); split = int(np.argmax(dd))
        if dd[split] < err: return [c]
        u = reparam(c, pts, u); c = gen_bezier(pts, u, t1, t2)
    dd = np.linalg.norm(bez(c, u) - pts, axis=1); split = int(np.clip(np.argmax(dd), 1, len(pts) - 2))
    tc = unit(pts[split - 1] - pts[split + 1])
    return fit_cubic(pts[:split + 1], t1, tc, err) + fit_cubic(pts[split:], -tc, t2, err)

def circle_path(cx_, cy_, r):
    k = 0.5523 * r
    return (f"M{f2(cx_ + r)} {f2(cy_)}C{f2(cx_ + r)} {f2(cy_ + k)} {f2(cx_ + k)} {f2(cy_ + r)} {f2(cx_)} {f2(cy_ + r)}"
            f"C{f2(cx_ - k)} {f2(cy_ + r)} {f2(cx_ - r)} {f2(cy_ + k)} {f2(cx_ - r)} {f2(cy_)}"
            f"C{f2(cx_ - r)} {f2(cy_ - k)} {f2(cx_ - k)} {f2(cy_ - r)} {f2(cx_)} {f2(cy_ - r)}"
            f"C{f2(cx_ + k)} {f2(cy_ - r)} {f2(cx_ + r)} {f2(cy_ - k)} {f2(cx_ + r)} {f2(cy_)}Z")

def trace_loop(Pt, err=0.3, k=3):
    n = len(Pt); perim = np.linalg.norm(Pt - np.roll(Pt, -1, axis=0), axis=1).sum()
    if perim < 6: return ""
    if perim < 40:                                   # a dot
        cx_, cy_, r_, _ = fit_circle(Pt); return circle_path(cx_, cy_, r_)
    v1 = Pt - np.roll(Pt, k, axis=0); v2 = np.roll(Pt, -k, axis=0) - Pt
    ang = np.degrees(np.arccos(np.clip((v1 * v2).sum(1) / (np.linalg.norm(v1, axis=1) * np.linalg.norm(v2, axis=1) + 1e-12), -1, 1)))
    win = np.max([np.roll(ang, s) for s in range(-k - 1, k + 2)], axis=0)
    cand = [i for i in range(n) if ang[i] > 42 and ang[i] >= win[i] - 1e-9]
    corners_ = []
    for i in cand:                                    # one corner per cluster
        if not corners_ or (i - corners_[-1]) > 2 * k: corners_.append(i)
    if len(corners_) > 1 and (corners_[0] + n - corners_[-1]) <= 2 * k: corners_.pop()
    segs = []
    if not corners_:                                  # smooth closed curve: cut it into pieces
        m = max(3, int(round(perim / 55))); cuts_ = [int(round(j * n / m)) for j in range(m)]
        for a, b in zip(cuts_, cuts_[1:] + [cuts_[0] + n]):
            idx = [i % n for i in range(a, b + 1)]
            ta = unit(Pt[(a + 2) % n] - Pt[(a - 2) % n]); tb = unit(Pt[(b - 2) % n] - Pt[(b + 2) % n])
            segs.append(dict(pts=Pt[idx], t1=ta, t2=tb, straight=False))
        verts = [Pt[c % n] for c in cuts_]
    else:
        for a, b in zip(corners_, corners_[1:] + [corners_[0] + n]):
            idx = [i % n for i in range(a, b + 1)]; seg = Pt[idx]
            ln, dr = fit_line(seg); dev = dist_to_line(seg, (ln, dr)).max()
            s = dict(pts=seg, straight=dev < 0.3, line=(ln, dr))
            kk = min(3, len(seg) - 1); s["t1"] = unit(seg[kk] - seg[0]); s["t2"] = unit(seg[-1 - kk] - seg[-1]); segs.append(s)
        verts = [Pt[c] for c in corners_]
        for i in range(len(segs)):                    # sharpen a corner between two straight edges
            a, b = segs[i - 1], segs[i]
            if a["straight"] and b["straight"] and abs(np.dot(a["line"][1], b["line"][1])) < 0.98:
                q = intersect(a["line"], b["line"])
                if np.linalg.norm(q - verts[i]) < 3: verts[i] = q
    d = f"M{f2(verts[0][0])} {f2(verts[0][1])}"
    for i, s in enumerate(segs):
        v0, v1 = verts[i], verts[(i + 1) % len(verts)]
        if s["straight"]: d += f"L{f2(v1[0])} {f2(v1[1])}"; continue
        cs = fit_cubic(s["pts"], s["t1"], s["t2"], err)
        cs[0][0] = v0; cs[-1][3] = v1
        for c in cs: d += "C" + " ".join(f"{f2(p[0])} {f2(p[1])}" for p in c[1:])
    return d + "Z"

def trace(M, box):
    yy0, yy1, xx0, xx1 = box
    loops_ = contours(M[yy0:yy1, xx0:xx1], 0.5, xx0, yy0)
    return "".join(trace_loop(l) for l in loops_ if len(l) >= 4)

TEXT = {"word": trace(C["D"], (500, 790, 100, 1370)), "name": trace(C["D"], (860, 960, 100, 1370)), "url": trace(C["L"], (960, 1065, 100, 1370))}
for k, v in TEXT.items(): print(f"traced {k}: {len(v)} bytes")

# ---------- 6. write the SVGs ----------
ocx, ocy, orr, ow = P["outer"]; icx, icy, irr, iw = P["inner"]
def on_circle(cx_, cy_, r_, deg): return (cx_ + r_ * math.cos(math.radians(deg)), cy_ + r_ * math.sin(math.radians(deg)))
a0 = (ocx - orr, ocy); a1 = on_circle(ocx, ocy, orr, P["cutL"]); b0 = on_circle(ocx, ocy, orr, P["cutR"]); b1 = (ocx + orr, ocy)
def arc_between(c, p, q, want, inside):
    cx_, cy_, r_ = c; ap = math.atan2(p[1] - cy_, p[0] - cx_); aq = math.atan2(q[1] - cy_, q[0] - cx_)
    for sweep in (1, 0):
        da = (aq - ap) % (2 * math.pi) if sweep else -((ap - aq) % (2 * math.pi)); am = ap + da / 2
        m = (cx_ + r_ * math.cos(am), cy_ + r_ * math.sin(am)); ok = math.hypot(m[0] - want[0], m[1] - want[1]) < want[2]
        if ok == inside: return (1 if abs(da) > math.pi else 0), sweep
tA, tB = tips
lg1, sw1 = arc_between((ox, oy, cor), tA, tB, (ix, iy, cir), False)
lg2, sw2 = arc_between((ix, iy, cir), tB, tA, (ox, oy, cor), True)
cres_d = f"M{f2(tA[0])} {f2(tA[1])}A{f2(cor)} {f2(cor)} 0 {lg1} {sw1} {f2(tB[0])} {f2(tB[1])}A{f2(cir)} {f2(cir)} 0 {lg2} {sw2} {f2(tA[0])} {f2(tA[1])}Z"
star_d = "M" + "L".join(f"{f2(x)} {f2(y)}" for x, y in corners) + "Z"
pb, bw = P["base_y"], P["base_w"]
mark = f'''<g id="mark">
    <g fill="none" stroke="{COL['G']}">
      <path id="outer-arc-left" stroke-width="{f2(ow)}" d="M{f2(a0[0])} {f2(a0[1])}A{f2(orr)} {f2(orr)} 0 0 1 {f2(a1[0])} {f2(a1[1])}"/>
      <path id="outer-arc-right" stroke-width="{f2(ow)}" d="M{f2(b0[0])} {f2(b0[1])}A{f2(orr)} {f2(orr)} 0 0 1 {f2(b1[0])} {f2(b1[1])}"/>
    </g>
    <circle fill="{COL['G']}" cx="{f2(a0[0])}" cy="{f2(a0[1])}" r="{f2(ow/2)}"/>
    <circle fill="{COL['G']}" cx="{f2(b1[0])}" cy="{f2(b1[1])}" r="{f2(ow/2)}"/>
    <path id="inner-arc" fill="none" stroke="{COL['Au']}" stroke-width="{f2(iw)}" stroke-linecap="round" d="M{f2(icx-irr)} {f2(icy)}A{f2(irr)} {f2(irr)} 0 0 1 {f2(icx+irr)} {f2(icy)}"/>
    <g fill="none" stroke="{COL['G']}">
      <line id="pillar" x1="{f2(P['pillar_x'])}" y1="{f2(P['pillar_top'])}" x2="{f2(P['pillar_x'])}" y2="{f2(pb)}" stroke-width="{f2(P['pillar_w'])}"/>
      <line id="post-left" x1="{f2(P['postL_x'])}" y1="{f2(P['postL_top']+P['postL_w']/2)}" x2="{f2(P['postL_x'])}" y2="{f2(pb)}" stroke-width="{f2(P['postL_w'])}" stroke-linecap="round"/>
      <line id="post-right" x1="{f2(P['postR_x'])}" y1="{f2(P['postR_top']+P['postR_w']/2)}" x2="{f2(P['postR_x'])}" y2="{f2(pb)}" stroke-width="{f2(P['postR_w'])}" stroke-linecap="round"/>
      <line id="base" x1="{f2(P['base_x0']+bw/2)}" y1="{f2(pb)}" x2="{f2(P['base_x1']-bw/2)}" y2="{f2(pb)}" stroke-width="{f2(bw)}" stroke-linecap="round"/>
    </g>
    <path id="crescent" fill="{COL['Au']}" d="{cres_d}"/>
    <path id="star" fill="{COL['Au']}" d="{star_d}"/>
  </g>'''
lock = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t">
  <title id="t">ICON, Islamic Center of Newton, Massachusetts</title>
  {mark}
  <path id="wordmark" fill="{COL['word']}" fill-rule="evenodd" d="{TEXT['word']}"/>
  <rect id="rule" x="0" y="{f2(P['rule_y0'])}" width="{W}" height="{f2(P['rule_y1']-P['rule_y0'])}" fill="{COL['rule']}"/>
  <path id="caption-name" fill="{COL['name']}" fill-rule="evenodd" d="{TEXT['name']}"/>
  <path id="caption-url" fill="{COL['url']}" fill-rule="evenodd" d="{TEXT['url']}"/>
</svg>
'''
vb = (440, 21, 589, 426)
markonly = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb[0]} {vb[1]} {vb[2]} {vb[3]}" role="img" aria-labelledby="t">
  <title id="t">ICON mark: a dome with a crescent and star</title>
  {mark}
</svg>
'''
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, "logo-lockup.svg"), "w").write(lock); open(os.path.join(OUT, "logo-mark.svg"), "w").write(markonly)
json.dump({k: v for k, v in P.items()}, open(os.path.join(here, "params.json"), "w"), indent=1, default=float)
print("wrote", OUT, "lockup bytes", len(lock), "mark bytes", len(markonly))
print("base_y", round(P["base_y"], 2), "outer", [round(v, 2) for v in P["outer"]], "inner", [round(v, 2) for v in P["inner"]])
