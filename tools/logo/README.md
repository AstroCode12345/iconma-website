# Logo redraw tools

Rebuilds `images/logo-lockup.svg` and `images/logo-mark.svg` from the president's image.

- `build_logo.py` measures the image. The mark (dome, crescent, star) becomes circles, lines and a polygon fitted to it. The lettering is **traced**: each letter's outline is found at the 50 percent edge, split at its corners, and fitted with smooth cubic curves. (The first logo was set in DejaVu Sans, so its letters could come from the font; the second uses a typeface we do not have.) `params.json` is what it measured.
- `lib.py` and `geom.py` are its helpers (colour coverage, sub-pixel contours, circle and line fits).
- Check the result with `_source/compare.html` (open it through `python3 serve.py`). It draws the original and the SVG at the same size and reports how far apart their edges are.

```bash
sips -s format bmp _source/logo-original.webp --out /tmp/iconma-logo.bmp
uv run --with numpy python tools/logo/build_logo.py /tmp/iconma-logo.bmp images
python3 tools/build-symbols.py
python3 tools/make-icons.py
```

If the president sends a vector file, use it instead of all of this.
