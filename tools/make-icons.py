#!/usr/bin/env python3
"""
Makes the small images a browser or a chat app asks for, all from the redrawn logo:

    images/favicon.svg          the crescent and star on a deep green tile (the full dome is too fine at 16px)
    images/favicon-32.png       the same, 32 x 32
    images/apple-touch-icon.png the same, 180 x 180, for an iPhone home screen
    images/og.png               1200 x 630 link preview: the full lockup on the logo's own ground

    python3 tools/make-icons.py

Needs macOS (it draws the SVGs with Quick Look's renderer, `qlmanage`) and reads images/logo-lockup.svg,
so run tools/logo/build_logo.py first if the logo changed. Nothing here is fetched or uploaded.
"""
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "images"
GROUND, DEEP, GOLD = "#F6F8FC", "#12371C", "#E0B650"

lockup = (IMG / "logo-lockup.svg").read_text(encoding="utf8")
crescent = re.search(r'<path id="crescent"[^>]* d="([^"]+)"', lockup).group(1)
star = re.search(r'<path id="star"[^>]* d="([^"]+)"', lockup).group(1)
inner = re.search(r"<svg[^>]*>(.*)</svg>", lockup, re.S).group(1)
inner = re.sub(r"<title[^>]*>.*?</title>", "", inner, flags=re.S)

# crescent and star share a box of about 114 x 112 centred on (741, 80) in the lockup's coordinates
favicon = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <title>ICONMA</title>
  <rect width="64" height="64" rx="14" fill="{DEEP}"/>
  <g transform="translate(32 33) scale(.36) translate(-741 -80)" fill="{GOLD}">
    <path d="{crescent}"/>
    <path d="{star}"/>
  </g>
</svg>
'''
(IMG / "favicon.svg").write_text(favicon, encoding="utf8")

# the lockup is 1468 x 1071; fit it in 560 px of the 630 px height
s = 560 / 1071
og = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="{GROUND}"/>
  <g transform="translate({(1200 - 1468 * s) / 2:.2f} 35) scale({s:.5f})">{inner}</g>
</svg>
'''

if not shutil.which("qlmanage"):
    sys.exit("qlmanage not found: the SVGs were written, but the PNGs need macOS (or draw them another way)")

with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp)
    (tmp / "og.svg").write_text(og, encoding="utf8")
    (tmp / "favicon.svg").write_text(favicon, encoding="utf8")
    for name, size, out in (("og", 1200, "og.png"), ("favicon", 180, "apple-touch-icon.png"), ("favicon", 32, "favicon-32.png")):
        (tmp / f"out{size}").mkdir()  # qlmanage will not create its output folder
        subprocess.run(["qlmanage", "-t", "-s", str(size), "-o", str(tmp / f"out{size}"), str(tmp / f"{name}.svg")],
                       check=True, capture_output=True)
        made = next((tmp / f"out{size}").glob("*.png"))
        shutil.copy(made, IMG / out)
        if out == "og.png":
            # Quick Look draws a non-square image into a square; keep the middle 1200 x 630
            subprocess.run(["sips", "-c", "630", "1200", str(IMG / out)], check=True, capture_output=True)
        for f in (tmp / f"out{size}").glob("*"):
            f.unlink()
        print("wrote", out)
