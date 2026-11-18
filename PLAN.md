# ICONMA website: plan

Two-page starter site (Home, About) for the Islamic Center of Newton, so the center can set up email and start writing to its community. Built in steps with a check-in after each. Started 2026-11-16.

## Confirmed facts
- Name: Islamic Center of Newton. Short name ICONMA. Domain iconma.org. (president's doc)
- Founded in 2024. (president's doc)
- Mailing address: 229 Woodcliff Rd, Newton, MA 02461. People cannot visit there yet, so the site says "Contact", never "Visit us". (doc, and Taymour 2026-11-16)
- Email: info@iconma.org. The doc says "will be", so the mailbox may not exist yet. (doc)
- Ayah for the home page: Surah Al-Ma'idah 5:2, "And cooperate in righteousness and piety." Arabic copied exactly from the doc. (doc)
- Mission statement, four points, for the About page. (doc)
- 501(c)(3) nonprofit, EIN 33-1418409, for the footer. Not verified. (doc)
- Logo supplied as a soft raster, 1468 x 1071. Original kept in `_source/logo-original.webp`. Lettering is DejaVu Sans, a free font. Colours measured from the raster: green #0E5C1F, gold #C69B35, dark green #12371C, light green #58924D, background #F6F8FC.

## Decisions
| Area | Decision | Why |
|---|---|---|
| Pages | Home and About. Home carries the four mission lead phrases as cards, About carries the full statement | Avoids two pages saying the same thing |
| Look | **Line & Light**, chosen by Taymour on 2026-11-17 from three (Dome at Dusk and Arch & Garden and the Tweaks panel were deleted) | He asked to flip between looks like Claude Design's tweaks, then picked one and asked for more hierarchy |
| Distance from ICB | Cool white, sans type, line art; no cream, serif or mono | The president's colours sit close to icbwayland.org, and he wants this site to feel distinct |
| Contact | Mailing address and email only. No map, no signup form | No one can visit yet; email only for now |
| Empty areas | Generic "More details coming soon" and "Check back soon for updates". No named sections | Nothing exists yet and nothing is invented |
| Admin portal | Skipped for v1. `content.json` holds contact details and a switched-off announcement | Nothing changes often yet |
| Photos | None | None available |
| Logo | Redrawn as SVG, precisely | His request |
| Hosting | The masjid's own GitHub repository and Vercel project deploy the site. Taymour keeps his own repo as a mirror and pushes to both, the way ICB Wayland works (`origin` with two push addresses, `mine` for his copy alone) | The masjid stays in control; his copy never goes stale. He has access to their Vercel and GitHub |

## Open questions for the masjid
1. **EIN sentence.** The doc reads "Islamic Center of Newton is The Islamic Center of Boston (ICB) was established in 2024 (1446 AH) ...". We write it as Newton. Please confirm the EIN is Newton's own, and that 1446 AH is right (1446 began in July 2024, so it only fits a founding in the second half of 2024).
2. **Mailbox.** info@iconma.org must exist before the site goes live, or the contact link bounces.
3. **Logo file.** If the president has the original vector (SVG, AI or PDF), send it. Until then we use the redraw.
4. **Logo rule.** The gold line under ICONMA runs edge to edge in the supplied image. The redrawn lockup copies that. Confirm it is meant to.
5. **Wording.** "Mailing address" instead of "Address".

## Log
### 2026-11-16
- Step 1 done: logo redrawn as SVG. `images/logo-lockup.svg` (17 KB) and `images/logo-mark.svg` (1.5 KB). The mark is fitted circles, lines and polygons; the lettering is DejaVu Sans outlines placed glyph by glyph, with the wordmark's vertical stems thickened 0.76 px per side because the raster's stems are heavier than the font's.
- Checked against the original with `_source/compare.html`: mean edge error 0.08 to 0.24 px per region, nothing more than 1 px from the original's edge (8 border pixels of the full-width rule excepted, where the source image is cropped). The source itself wobbles about 0.5 px, so this is as exact as it can be.
- `tools/logo/` regenerates it. `serve.py` on port 8230 and an `iconma` launch.json entry added.
- Step 2 written, not yet verified: `index.html`, `about/index.html`, `styles.css` (shared part plus one block per look), `app.js`, `content.js`, `content.json`, `tweaks.js`, `tools/build-symbols.py` (writes the logo symbols into the pages), `PRODUCT.md`. Bug found and fixed: host `<svg>` boxes that use a `<symbol>` must start at `0 0`, not at the symbol's own offset.
- Verified (same day): all three looks on Home and About at 1280 wide, and at 360, 393 and 430 wide: no sideways scroll, no tap target under 44px, every text colour meets its contrast bar, no console errors. The Arabic matches the doc exactly (42 of 42 code points) and the mission text is verbatim. `detect.mjs` run once: clean after squaring Dusk's mission panels (a thick gold top border clashed with rounded corners).
- Fixed after looking at screenshots: the Arabic's lower marks touched the English line (more gap); Arch's mission cards left a big empty arch with text at the bottom (text now centred inside the arch); email and "Read the full mission statement" links were under 44px tall.
- Not checked: 375px width (between two widths that pass), a real iPhone over Wi-Fi, keyboard walk-through by hand, reduced-motion by eye (rules are in the CSS). Hero draw-in and Dusk lamp were seen only as stills.
- Next: Taymour picks a look. Then step 3: prune the other two looks and `tweaks.js`, write `DESIGN.md` from the chosen look, favicon and og image, `vercel.json`, `robots.txt`, `sitemap.xml`, `404.html`, README.

### 2026-11-17
- Taymour likes **Line & Light** (not yet confirmed as the final pick, so Dusk, Arch and `tweaks.js` are still in) and said it looked flat and needed visual hierarchy. Reworked only its block in `styles.css`, plus three markup hooks (dome lines and crescent in the Home ayah section, `contact__row--email` on the email row).
- What changed, and why: body weight 400 with light 300 kept for large type only (thin small text read faint); the mark is the largest thing on Home and its base line runs across the page as a horizon with "Founded in 2024" and "Newton, Massachusetts" sitting on it at each end; the ayah sits on a tinted band with the logo's two arcs drawn large behind it and the crescent at the top of the dome; the mission statement is the biggest type below the hero with a gold arch before each line and the label held in place on desktop; the "coming soon" note is a slim strip, not a section; About's title is very large and stands on a rule; the email is the large item in Contact; the footer is one deep green block so the page ends on something solid. The repeated arc ornament above every section was dropped as decoration.
- Checked: desktop 1280 and phone 360, 393, 430 on Home and About. No sideways scroll, no contrast failures, detector clean. The email link was 43px tall and was raised to the 44px target. Draw-in and hover not re-checked by eye.
- Impeccable's full interview and direction roll were skipped on purpose: Taymour had already pinned all three directions. PRODUCT.md was written from his confirmed answers, so it is his approval round at the next check-in.
- Step 3, finished the site (same day): deleted Dusk, Arch and `tweaks.js`, and rewrote `styles.css` as one flat file with Line & Light's final values. Checked by measuring every element (size, position, colour, type) before and after, on Home and About at 1280 and 393 wide: zero differences. Only the empty "soon" wrapper element was removed on purpose.
- Added: `404.html`, `robots.txt`, `sitemap.xml` (`tools/build-sitemap.py`), `vercel.json` (cache headers, three redirects, three security headers), `.vercelignore` (allow-list so only the website uploads; `PLAN.md` and `PRODUCT.md` hold unconfirmed facts), `favicon.svg`, `favicon-32.png`, `apple-touch-icon.png`, `og.png` (1200x630) from `tools/make-icons.py`, share and icon tags on every page, `README.md`, `DESIGN.md`. A title descender collision on the 404 ("g" in "Page") was fixed for every page title.
- Design choice to confirm: the favicon and home-screen icon are the crescent and star on a deep green tile, because the full dome is too fine at 16px. That tile is not in the president's logo.
- Not tested: `vercel.json` and `.vercelignore` against a real deploy (the same allow-list pattern works for Flick); a real iPhone; the link preview in WhatsApp; the hero draw-in and hover underlines by eye. Fonts load from Google Fonts.
- Still needs the masjid: the president confirming the EIN sentence and "1446 AH"; the info@iconma.org mailbox; the GitHub organization and Vercel project in the masjid's own accounts; DNS at the registrar. Nothing is committed to git.
