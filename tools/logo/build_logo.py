"""Measure the president's logo raster and rebuild it as clean SVG.
Mark = circles, lines and polygons fitted to the raster. Lettering = DejaVu Sans outlines placed
glyph by glyph where the raster has them.   uv run --with numpy --with fonttools --with matplotlib python build_logo.py RASTER.bmp OUTDIR
"""
import sys, os, json, math
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
from lib import *; from classes import *; import classes; from geom import *
import matplotlib
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen

RASTER, OUT = sys.argv[1], sys.argv[2]
img = load(RASTER); H, W, _ = img.shape
ys, xs = np.mgrid[0:H, 0:W]; px = xs + 0.5; py = ys + 0.5

# ---- 1. solid ink colours (two passes) ----
for _ in range(2):
    C = class_maps(img)
    for k in classes.INK:
        m = C[k] >= 0.97
        classes.INK[k] = tuple(float(v) for v in np.median(img[m], axis=0))
C = class_maps(img); G, Au, D, L = C["G"], C["Au"], C["D"], C["L"]
hexof = lambda c: "#%02X%02X%02X" % tuple(int(round(v)) for v in c)
COL = {k: hexof(v) for k, v in classes.INK.items()}
print("colours", COL)

def edges_1d(prof, thr=0.5):
    idx = np.where(prof >= thr)[0]; a, b = idx[0], idx[-1]
    ra = a - 1 + (thr - prof[a-1]) / (prof[a] - prof[a-1]) if a > 0 else float(a)
    rb = b + (prof[b] - thr) / (prof[b] - prof[b+1]) if b + 1 < len(prof) else float(b)
    return ra + 0.5, rb + 0.5
P = {}
# ---- 2. straight parts ----
band = G[415:460, 560:700].mean(1); e = edges_1d(band); P["base_y"] = (e[0] + e[1]) / 2 + 415
P["base_w"] = float(G[415:460, 560:700].sum(0).mean())
row = G[int(P["base_y"]) - 1:int(P["base_y"]) + 2, 400:1080].mean(0); e = edges_1d(row); P["base_x0"], P["base_x1"] = e[0] + 400, e[1] + 400
cp = G[200:400, 700:770].mean(0); e = edges_1d(cp); P["pillar_x"] = (e[0] + e[1]) / 2 + 700
P["pillar_w"] = float(G[200:400, 700:770].sum(1).mean())
vp = G[100:200, int(P["pillar_x"]) - 3:int(P["pillar_x"]) + 4].mean(1); P["pillar_top"] = None
# flat top: first row crossing 0.5 with sub-pixel interpolation
i0 = int(np.argmax(vp >= 0.5)); P["pillar_top"] = 100 + i0 - 1 + (0.5 - vp[i0 - 1]) / (vp[i0] - vp[i0 - 1]) + 0.5
for nm, x0, x1 in (("postL", 520, 565), ("postR", 905, 950)):
    cp = G[340:400, x0:x1].mean(0); e = edges_1d(cp); P[nm + "_x"] = (e[0] + e[1]) / 2 + x0
    P[nm + "_w"] = float(G[340:400, x0:x1].sum(1).mean())
    xi = int(round(P[nm + "_x"])); vp = G[260:350, xi - 2:xi + 3].mean(1); e = edges_1d(vp); P[nm + "_top"] = e[0] + 260
rp = Au[790:830, 100:1300].mean(1); e = edges_1d(rp); P["rule_y0"], P["rule_y1"] = e[0] + 790, e[1] + 790
P["rule_t"] = float(Au[790:830, 100:1300].sum(0).mean())
# ---- 3. arcs ----
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
P["outer"] = arc(G, (733.8, 307.6), 200, 260, 60)
P["inner"] = arc(Au, (733.7, 300), 130, 185, 138)
cx, cy, r, w = P["outer"]; d = np.hypot(px - cx, py - cy); th = np.degrees(np.arctan2(py - cy, px - cx))
cuts = {}
for side, lo, hi in (("L", -140, -85), ("R", -95, -40)):
    vals = []
    for rb in np.linspace(r - w / 2 + 1.5, r + w / 2 - 1.5, 5):
        s = (np.abs(d - rb) < 0.7) & (th > lo) & (th < hi); on = th[s][G[s] >= 0.5]
        vals.append(on.max() if side == "L" else on.min())
    cuts[side] = float(np.median(vals))
P["cutL"], P["cutR"] = cuts["L"], cuts["R"]
# ---- 4. crescent + star ----
x0, x1, y0, y1 = 660, 830, 10, 138
loops = sorted(contours(Au[y0:y1, x0:x1], 0.5, x0, y0), key=lambda l: -abs(area(l)))
cres, star = loops[0], loops[1]
oc, inl = ransac_circle(cres, tol=0.8, iters=4000, rmin=30); ic, _ = ransac_circle(cres[~inl], tol=0.8, iters=4000, rmin=20)
(ox, oy, cor, _), (ix, iy, cir, _) = oc, ic
d_ = math.hypot(ix - ox, iy - oy); a_ = (cor**2 - cir**2 + d_**2) / (2 * d_); h_ = math.sqrt(cor**2 - a_**2)
mx, my = ox + a_ * (ix - ox) / d_, oy + a_ * (iy - oy) / d_
tips = [(mx + h_ * (iy - oy) / d_, my - h_ * (ix - ox) / d_), (mx - h_ * (iy - oy) / d_, my + h_ * (ix - ox) / d_)]
P["crescent"] = dict(outer=[ox, oy, cor], inner=[ix, iy, cir], tips=tips)
# star: assign contour points to ideal edges, fit a line per edge, intersect
cen = np.array([758.9, 70.1]); R_, r_ = 26.1, 10.0
ideal = np.array([cen + (R_ if k % 2 == 0 else r_) * np.array([math.cos(math.radians(-90 + 36 * k)), math.sin(math.radians(-90 + 36 * k))]) for k in range(10)])
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
P["star"] = corners.tolist()
# ---- 5. lettering from DejaVu Sans ----
fontpath = os.path.join(matplotlib.get_data_path(), "fonts", "ttf", "DejaVuSans.ttf")
font = TTFont(fontpath); glyf = font["glyf"]; cmap = font.getBestCmap()
def gcontours(ch):
    g = glyf[cmap[ord(ch)]]; coords, ends, flags = g.getCoordinates(glyf); out = []; s = 0
    for e in ends:
        out.append([(float(coords[i][0]), float(coords[i][1]), bool(flags[i] & 1)) for i in range(s, e + 1)]); s = e + 1
    return out
def gbounds(ch):
    bp = BoundsPen(font.getGlyphSet()); font.getGlyphSet()[cmap[ord(ch)]].draw(bp); return bp.bounds
def embolden(c, df):
    n = len(c); out = []
    for i, (x, y, on) in enumerate(c):
        px_, py_, _ = c[i - 1]; nx_, ny_, _ = c[(i + 1) % n]
        tx, ty = nx_ - px_, ny_ - py_; L_ = math.hypot(tx, ty) or 1
        nxn = -ty / L_
        out.append((x + df * math.copysign(min(1.0, abs(nxn) / 0.35), nxn), y, on))
    return out
def contour_path(c, tf):
    n = len(c); st = next(i for i, p in enumerate(c) if p[2]); c = c[st:] + c[:st]
    T = lambda p: tf(p[0], p[1]); f = lambda v: ("%.2f" % v).rstrip("0").rstrip(".")
    pt = lambda q: f(q[0]) + " " + f(q[1])
    d = "M" + pt(T(c[0])); off = []
    for p in c[1:] + [c[0]]:
        if p[2]:
            if not off: d += "L" + pt(T(p))
            else:
                for k, o in enumerate(off):
                    if k < len(off) - 1:
                        mid = ((o[0] + off[k + 1][0]) / 2, (o[1] + off[k + 1][1]) / 2, True); d += "Q" + pt(T(o)) + " " + pt(T(mid))
                    else: d += "Q" + pt(T(o)) + " " + pt(T(p))
                off = []
        else: off.append(p)
    return d + "Z"
def tight(ch_contours):
    pts = [(x, y) for c in ch_contours for x, y, _ in c]; xs_ = [p[0] for p in pts]; ys_ = [p[1] for p in pts]; return min(xs_), min(ys_), max(xs_), max(ys_)
lines_spec = [("wordmark", D, (540, 770, 120, 1340), "ICONMA"),
              ("caption1", D, (870, 945, 120, 1340), "ISLAMICCENTEROFNEWTON"),
              ("caption2", L, (985, 1055, 120, 1340), "MASSACHUSETTS·ICONMA.ORG")]
TEXT = {}; report = {}
for name, M, (a0, a1, b0, b1), text in lines_spec:
    lp = contours(M[a0:a1, b0:b1], 0.5, b0, a0); bbs = [(l[:, 0].min(), l[:, 1].min(), l[:, 0].max(), l[:, 1].max(), abs(area(l))) for l in lp]
    outer = [b for i, b in enumerate(bbs) if b[4] > 3 and not any(j != i and bbs[j][0] <= b[0] and bbs[j][1] <= b[1] and bbs[j][2] >= b[2] and bbs[j][3] >= b[3] and bbs[j][4] > b[4] for j in range(len(bbs)))]
    outer.sort(key=lambda b: b[0]); assert len(outer) == len(text), (name, len(outer), len(text))
    gb = [gbounds(ch) for ch in text]
    s = float(np.median([(b[3] - b[1]) / (g[3] - g[1]) for b, g in zip(outer, gb)]))
    dpx = float(np.median([((b[2] - b[0]) - s * (g[2] - g[0])) / 2 for b, g in zip(outer, gb) if g[2] - g[0] > 150]))
    df = dpx / s; paths = []; errs = []
    for ch, b in zip(text, outer):
        cs = [embolden(c, df) for c in gcontours(ch)]; xm, ym, xM, yM = tight(cs)
        X = (b[0] + b[2]) / 2 - s * (xm + xM) / 2; Y = (b[1] + b[3]) / 2 + s * (ym + yM) / 2
        tf = lambda u, v, X=X, Y=Y: (X + s * u, Y - s * v)
        paths.append("".join(contour_path(c, tf) for c in cs))
        errs.append(max(abs(X + s * xm - b[0]), abs(X + s * xM - b[2]), abs(Y - s * yM - b[1]), abs(Y - s * ym - b[3])))
    TEXT[name] = "".join(paths); report[name] = dict(scale=s, em_px=s * 2048, embolden_px=dpx, max_bbox_err=max(errs))
print("lettering", json.dumps(report, indent=1))
# ---- 6. emit SVG ----
f2 = lambda v: ("%.2f" % v).rstrip("0").rstrip(".")
ocx, ocy, orr, ow = P["outer"]; icx, icy, irr, iw = P["inner"]
def on_circle(cx, cy, r, deg): return (cx + r * math.cos(math.radians(deg)), cy + r * math.sin(math.radians(deg)))
a0 = (ocx - orr, ocy); a1 = on_circle(ocx, ocy, orr, P["cutL"]); b0 = on_circle(ocx, ocy, orr, P["cutR"]); b1 = (ocx + orr, ocy)
# crescent arcs: choose the arc of each circle by testing a midpoint
def arc_between(c, p, q, want_inside_of, inside):
    cx_, cy_, r_ = c; ap = math.atan2(p[1] - cy_, p[0] - cx_); aq = math.atan2(q[1] - cy_, q[0] - cx_)
    for sweep in (1, 0):
        da = (aq - ap) % (2 * math.pi) if sweep else -((ap - aq) % (2 * math.pi)); am = ap + da / 2
        m = (cx_ + r_ * math.cos(am), cy_ + r_ * math.sin(am)); ok = math.hypot(m[0] - want_inside_of[0], m[1] - want_inside_of[1]) < want_inside_of[2]
        if ok == inside: return (1 if abs(da) > math.pi else 0), sweep
tA, tB = tips
lg1, sw1 = arc_between((ox, oy, cor), tA, tB, (ix, iy, cir), False)   # outer boundary: outside the inner circle
lg2, sw2 = arc_between((ix, iy, cir), tB, tA, (ox, oy, cor), True)    # inner boundary: inside the outer circle
cres_d = f"M{f2(tA[0])} {f2(tA[1])}A{f2(cor)} {f2(cor)} 0 {lg1} {sw1} {f2(tB[0])} {f2(tB[1])}A{f2(cir)} {f2(cir)} 0 {lg2} {sw2} {f2(tA[0])} {f2(tA[1])}Z"
star_d = "M" + "L".join(f"{f2(x)} {f2(y)}" for x, y in corners) + "Z"
pb = P["base_y"]; bw = P["base_w"]
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
ry = (P["rule_y0"] + P["rule_y1"]) / 2
lock = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t">
  <title id="t">ICONMA, Islamic Center of Newton, Massachusetts</title>
  {mark}
  <path id="wordmark" fill="{COL['D']}" d="{TEXT['wordmark']}"/>
  <rect id="rule" x="0" y="{f2(P['rule_y0'])}" width="{W}" height="{f2(P['rule_y1']-P['rule_y0'])}" fill="{COL['Au']}"/>
  <path id="caption-name" fill="{COL['D']}" d="{TEXT['caption1']}"/>
  <path id="caption-url" fill="{COL['L']}" d="{TEXT['caption2']}"/>
</svg>
'''
vb = (440, 21, 589, 426)
markonly = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb[0]} {vb[1]} {vb[2]} {vb[3]}" role="img" aria-labelledby="t">
  <title id="t">ICONMA mark: a dome with a crescent and star</title>
  {mark}
</svg>
'''
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, "logo-lockup.svg"), "w").write(lock); open(os.path.join(OUT, "logo-mark.svg"), "w").write(markonly)
json.dump({k: v for k, v in P.items()}, open(os.path.join(here, "params.json"), "w"), indent=1, default=float)
print("wrote", OUT, "lockup bytes", len(lock), "mark bytes", len(markonly))
print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in P.items() if not isinstance(v, (list, dict, tuple))})
print("outer", [round(v, 2) for v in P["outer"]], "inner", [round(v, 2) for v in P["inner"]])
