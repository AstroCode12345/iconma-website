# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
Everyone who might look up a new masjid in Newton, Massachusetts: Muslims in Newton and nearby towns first, then neighbours, interfaith visitors and city contacts. Most will arrive from a link in an email or WhatsApp message on a phone. (Confirmed: Taymour, 2026-11-16, "All".)

## Product Purpose
A functioning starter website for the Islamic Center of Newton (ICONMA, founded 2024) so the center can set up info@iconma.org and start writing to its community. Nothing else exists yet: no events, no prayer times, no photos, no old site. Success is a calm, correct, honest page that says who they are and how to reach them, and says "check back soon" about the rest.

## Positioning
A new masjid's first page that looks cared for without pretending to be bigger than it is. It must not read as another page of icbwayland.org, whose colours the president's logo happens to resemble.

## Operating Context
Two pages, Home and About. Content comes only from the president's doc (kept in `_source/`). The president chose the logo and its colours. Taymour builds and reviews on his iPhone over Wi-Fi before anything goes live. The masjid will own the hosting accounts.

## Capabilities and Constraints
- Contact is a mailing address and an email only. People cannot visit yet, so never "Visit us", no map.
- No named events, programs, prayer times or donation sections. Generic "More details coming soon" and "Check back soon for updates" tags only.
- No admin portal, no signup form, no photos in v1.
- Text is verbatim from the president's doc. The EIN sentence in that doc names the Islamic Center of Boston by mistake; the site says Newton, flagged in `PLAN.md` for the president to confirm (EIN and the 1446 AH year are unverified).
- The info@iconma.org mailbox must exist before the site goes live.
- Undecided: the final look (three directions are built for review), hosting and domain DNS, whether the president has a vector original of the logo.

## Brand Commitments
The president's logo is binding: green dome arcs, gold inner arch and crescent, ICONMA in DejaVu Sans, redrawn as SVG in `images/`. Measured colours: green #0E5C1F, gold #C69B35, dark green #12371C, light green #58924D, ground #F6F8FC. Lowkey tone. Taymour never wants copy that claims he hand-coded anything, and no em dashes.

## Evidence on Hand
The president's doc (ayah Surah Al-Ma'idah 5:2, four-point mission, address, email, EIN line) and the logo image, both in `_source/`. No photos, testimonials, events, board names or numbers exist. Do not invent any.

## Product Principles
1. Say only what is true today, and say "check back soon" about the rest.
2. The logo's own geometry is the only ornament. No stock mosque imagery, no arabesque wallpaper.
3. Plain, warm, short wording that a first-time visitor and a long-time congregant both read comfortably on a phone.
4. Show the ayah with the care Arabic text deserves: correct letters and marks, a font made for it, never altered.

## Accessibility & Inclusion
Body text 4.5:1 or better, 17px or larger base, tap targets 44px or larger, keyboard focus visible, reduced motion respected, Arabic text marked with `lang="ar"` and `dir="rtl"`.
