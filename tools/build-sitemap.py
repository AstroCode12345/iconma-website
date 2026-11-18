#!/usr/bin/env python3
"""
Writes sitemap.xml from the site's pages, so nobody has to remember to edit it by hand.

    python3 tools/build-sitemap.py

A page is any index.html at the top level or one folder down (about/index.html), except the
folders that are not part of the site (_source, tools, images). 404.html is left out on purpose.
lastmod is the file's own modification date. Run it again after adding a page, and add the
page's priority below if it should rank above the default.
"""
import datetime
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://iconma.org"
NOT_SITE = {"_source", "tools", "images"}
PRIORITY = {"/": "1.0", "/about/": "0.8"}
DEFAULT_PRIORITY = "0.6"

pages = []
for index in sorted([ROOT / "index.html", *ROOT.glob("*/index.html")]):
    rel = index.relative_to(ROOT).parent
    if rel.parts and rel.parts[0] in NOT_SITE:
        continue
    path = "/" if not rel.parts else "/" + rel.as_posix() + "/"
    day = datetime.date.fromtimestamp(index.stat().st_mtime).isoformat()
    pages.append((path, day))

pages.sort(key=lambda p: (p[0] != "/", p[0]))  # home first
lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for path, day in pages:
    lines += ["  <url>", f"    <loc>{BASE}{path}</loc>", f"    <lastmod>{day}</lastmod>",
              f"    <priority>{PRIORITY.get(path, DEFAULT_PRIORITY)}</priority>", "  </url>"]
lines.append("</urlset>")
(ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf8")
print(f"sitemap.xml: {len(pages)} pages")
for path, day in pages:
    print("  ", path, day)
