# Logo redraw tools

Rebuilds `images/logo-lockup.svg` and `images/logo-mark.svg` from the president's raster.

- `build_logo.py` measures the raster (circles, lines and polygons for the mark, DejaVu Sans outlines placed glyph by glyph for the lettering) and writes the SVGs. `params.json` is what it measured.
- `lib.py`, `classes.py`, `geom.py` are its helpers (colour coverage, sub-pixel contours, circle and line fits).
- Check the result with `_source/compare.html` (open it through `python3 serve.py`).

```bash
sips -s format bmp _source/logo-original.webp --out /tmp/iconma-logo.bmp
uv run --with numpy --with fonttools --with matplotlib python tools/logo/build_logo.py /tmp/iconma-logo.bmp images
```

matplotlib is only used to find the DejaVu Sans font file it ships with. DejaVu Sans is free to use and embed.
