# ICONMA website

The site for the Islamic Center of Newton (ICONMA, iconma.org): two pages, Home and About. Plain HTML, CSS and JavaScript. There is no build step and no database. Facts, decisions and open questions are in [PLAN.md](PLAN.md); the look is recorded in [DESIGN.md](DESIGN.md).

## Run it

```bash
python3 serve.py
```

Then open http://localhost:8230. Use `serve.py`, not `python3 -m http.server`: it turns browser caching off, so an edit always shows, and it serves `404.html` for missing addresses the way Vercel will.

To see it on an iPhone, join the same Wi-Fi and open `http://<this Mac's address>:8230`.

## What is where

| File | What it is |
|---|---|
| `index.html`, `about/index.html`, `404.html` | The pages. The text is written in them directly. |
| `styles.css` | All the styling. One flat file, one section per part of the page. |
| `content.json`, `content.js` | The few things that may change: the email, the mailing address, and a switched-off announcement banner. `content.js` fills them into the pages. |
| `app.js` | Marks the current page in the nav and fades in the lower sections. |
| `images/` | The redrawn logo (`logo-lockup.svg`, `logo-mark.svg`), the favicon, the home-screen icon and the link preview (`og.png`). |
| `robots.txt`, `sitemap.xml`, `vercel.json`, `.vercelignore` | Search engines and hosting. |
| `_source/` | The president's original logo and doc, and `compare.html`. Never uploaded. |
| `tools/` | Scripts that regenerate things (see below). Never uploaded. |

## Changing things

**The words.** Edit the HTML. All text comes from the president's doc, so check any change with him.

**The email or the mailing address.** Edit `content.json`. The same values are also written in the HTML as a fallback, so for now change both places.

**An announcement.** In `content.json` set `"show": true` and write the `"text"`. A thin green bar appears at the top of every page. Set `"show": false` to hide it.

**After editing `styles.css`, `content.js` or `app.js`,** change the `?v=` stamp at the end of their addresses in all three pages, or visitors keep running the old file. Use the next letter on today's date:

```bash
perl -pi -e 's/(styles\.css|content\.js|app\.js)\?v=[0-9a-z]+/$1?v=20261201a/g' index.html about/index.html 404.html
```

## The logo and the small images

The president sent the logo as a soft image. It was redrawn as clean SVG (the mark as fitted circles and lines, the lettering traced from the image) and checked against his image, within about 1 pixel everywhere. The current logo is his second version; the first is kept in `_source/`.

```bash
sips -s format bmp _source/logo-original.webp --out /tmp/iconma-logo.bmp
uv run --with numpy python tools/logo/build_logo.py /tmp/iconma-logo.bmp images
python3 tools/build-symbols.py      # puts the logo into every page, so it can be recoloured
python3 tools/make-icons.py         # favicon, home-screen icon and link preview (macOS only)
```

Open `http://localhost:8230/_source/compare.html` after any logo change to see the original against the redraw. `tools/logo/README.md` has the details. If the president sends a vector file, use it instead.

## The sitemap

```bash
python3 tools/build-sitemap.py
```

Run it after adding a page.

## Before it goes live (not done yet)

1. **The mailbox.** `info@iconma.org` must exist before the site is public, or the contact link bounces.
2. **The president confirms** the EIN, and that "1446 AH" fits the month they were founded. His doc named the Islamic Center of Boston in that sentence by mistake; the site says Newton.
3. **Accounts.** The GitHub repository and the Vercel project belong to the masjid, with at least two trusted owners. See Hosting and pushing below.
4. **The domain.** Point iconma.org at Vercel from the registrar. Email uses separate records at the same registrar, so the two do not conflict.
5. **Check the preview.** After deploying, paste the address into WhatsApp or iMessage to see the link preview. If it looks stale, the app has cached the old one.
6. `.vercelignore` is an allow-list: only the website uploads. Leave it that way, because `PLAN.md` and `PRODUCT.md` hold facts that are not confirmed yet.

## Hosting and pushing

This is managed the same way as the ICB Wayland site: the masjid owns the GitHub repository and the Vercel project, and the developer keeps his own copy as a working mirror.

- **The masjid's repository** is what Vercel deploys. A push to its `main` branch publishes the site within a minute or two.
- **The developer's own repository** is the mirror, so his copy never goes stale.
- `origin` has two push addresses, so one `git push origin main` reaches both. `mine` points at his copy alone. `git remote -v` showing two push lines for `origin` is deliberate; do not "fix" it.

```bash
git remote add mine https://github.com/<your-account>/iconma-website.git
git remote add origin https://github.com/<masjid-account>/<repo>.git
git remote set-url --add --push origin https://github.com/<masjid-account>/<repo>.git
git remote set-url --add --push origin https://github.com/<your-account>/iconma-website.git
git remote -v
```

The first `--add --push` has to name the masjid's repository again, because adding a push address replaces the default one.

In Vercel, from the masjid's account: Add New, Project, import the masjid's repository, framework preset **Other**, no build command, no output directory. Then under Settings, Domains, add `iconma.org` and create the records Vercel shows at the registrar. `vercel.json` and `.vercelignore` are already in the repository.

The routine: `git pull`, edit, bump the `?v=` stamp if styles or scripts changed, check it on a phone, commit, `git pull` again, `git push origin main`. If the two copies ever diverge, merge them. Never force-push.

The fonts (Jost and Amiri Quran) load from Google Fonts. Self-hosting them is possible later if the masjid prefers no requests to Google.
