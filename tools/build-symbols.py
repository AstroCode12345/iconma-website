#!/usr/bin/env python3
"""
Turns images/logo-lockup.svg into three reusable SVG symbols (the mark, the crescent
alone, and the wordmark) and writes them into every page between

    <!-- symbols:start -->
    <!-- symbols:end -->

Why symbols: a symbol drawn with <use> can be recoloured from CSS variables, so each part of
a page (the dark footer, for one) colours the logo without a second copy of the artwork. Every
stroke carries pathLength="1", which is what lets the hero draw the mark in with one
stroke-dashoffset animation.

The colours come from the lockup itself, and the wordmark's box is measured from its outline, so
a new logo needs no edits here. The script also keeps each wordmark <svg> in the pages the same
shape as its symbol, and prints the aspect ratio to use in styles.css.

    python3 tools/build-symbols.py

Run it again after tools/logo/build_logo.py rewrites the lockup. It only touches the text
between the two markers, and the viewBox of the two wordmark <svg> elements.
"""
import math
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
SVG = "{http://www.w3.org/2000/svg}"
text = (ROOT / "images" / "logo-lockup.svg").read_text(encoding="utf8")
doc = ET.fromstring(text)


def by_id(i):
    el = doc.find(f".//*[@id='{i}']")
    if el is None:
        sys.exit(f"logo-lockup.svg has no element with id={i}")
    return el


arc_l, arc_r, inner = by_id("outer-arc-left"), by_id("outer-arc-right"), by_id("inner-arc")
caps = [c for c in doc.iter(SVG + "circle")]
lines = [by_id(i) for i in ("pillar", "post-left", "post-right", "base")]
crescent, star, word = by_id("crescent"), by_id("star"), by_id("wordmark")

# colours straight from the lockup
G_HEX = re.search(r'<path id="outer-arc-left"', text) and re.search(r'<g fill="none" stroke="(#[0-9A-Fa-f]{6})">', text).group(1)
AU_HEX = inner.attrib["stroke"]
WM_HEX = word.attrib["fill"]
G, AU, WM = f"var(--mk-green,{G_HEX})", f"var(--mk-gold,{AU_HEX})", f"var(--wm,{WM_HEX})"

# the wordmark's box, measured from its outline (every command in it takes x y pairs)
nums = [float(n) for n in re.findall(r"-?\d+\.?\d*", word.attrib["d"])]
xs, ys = nums[0::2], nums[1::2]
vx, vy = math.floor(min(xs)), math.floor(min(ys))
vw, vh = math.ceil(max(xs)) - vx, math.ceil(max(ys)) - vy


def line(el):
    a = el.attrib
    cap = ' stroke-linecap="round"' if a.get("stroke-linecap") == "round" else ""
    return (f'<line pathLength="1" x1="{a["x1"]}" y1="{a["y1"]}" x2="{a["x2"]}" y2="{a["y2"]}" '
            f'stroke-width="{a["stroke-width"]}"{cap}/>')


mark_body = f'''<g fill="none" style="stroke:{G}">
      <path pathLength="1" stroke-width="{arc_l.attrib['stroke-width']}" d="{arc_l.attrib['d']}"/>
      <path pathLength="1" stroke-width="{arc_r.attrib['stroke-width']}" d="{arc_r.attrib['d']}"/>
    </g>
    {"".join(f'<circle style="fill:{G}" cx="{c.attrib["cx"]}" cy="{c.attrib["cy"]}" r="{c.attrib["r"]}"/>' for c in caps)}
    <path pathLength="1" fill="none" style="stroke:{AU}" stroke-width="{inner.attrib['stroke-width']}" stroke-linecap="round" d="{inner.attrib['d']}"/>
    <g fill="none" style="stroke:{G}">
      {"".join(line(l) for l in lines)}
    </g>
    <path style="fill:{AU}" d="{crescent.attrib['d']}"/>
    <path style="fill:{AU}" d="{star.attrib['d']}"/>'''

crescent_body = f'''<path style="fill:{AU}" d="{crescent.attrib['d']}"/>
    <path style="fill:{AU}" d="{star.attrib['d']}"/>'''

block = f'''<!-- symbols:start (written by tools/build-symbols.py, do not edit by hand) -->
<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
  <symbol id="mark" viewBox="440 21 589 426">
    {mark_body}
  </symbol>
  <symbol id="crescent" viewBox="684 24 114 112">
    {crescent_body}
  </symbol>
  <symbol id="wordmark" viewBox="{vx} {vy} {vw} {vh}">
    <path style="fill:{WM}" fill-rule="evenodd" d="{word.attrib['d']}"/>
  </symbol>
</svg>
<!-- symbols:end -->'''

pages = [p for p in (ROOT / "index.html", ROOT / "about" / "index.html", ROOT / "404.html") if p.exists()]
pattern = re.compile(r"<!-- symbols:start.*?<!-- symbols:end -->", re.S)
host = re.compile(r'(<svg class="(?:brand__word|hero__word)" viewBox=")[^"]*(")')
for page in pages:
    s = page.read_text(encoding="utf8")
    if not pattern.search(s):
        print(f"skipped {page.relative_to(ROOT)} (no markers)")
        continue
    s = pattern.sub(lambda m: block, s)
    s = host.sub(lambda m: f"{m.group(1)}0 0 {vw} {vh}{m.group(2)}", s)
    page.write_text(s, encoding="utf8")
    print(f"updated {page.relative_to(ROOT)}")
print(f"symbols block: {len(block)} bytes; colours green {G_HEX}, gold {AU_HEX}, wordmark {WM_HEX}")
print(f"wordmark box {vw} x {vh}: use aspect-ratio: {vw} / {vh} for .brand__word and .hero__word in styles.css")
