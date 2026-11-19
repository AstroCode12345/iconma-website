# Design

The look of the ICONMA site as built, written from the shipped CSS. It was chosen by Taymour on 2026-11-17 ("Line & Light") from three directions; the other two (Dome at Dusk, Arch & Garden) were deleted. Product facts are in [PRODUCT.md](PRODUCT.md).

## Idea

Cool white and thin line. The logo's own geometry (two dome arcs, crescent, star, a base line) is the only ornament. The hierarchy comes from scale and weight, one tinted band, and one deep green block at the foot, not from decoration. It had to sit close to the president's green and gold yet look nothing like icbwayland.org, so there is no cream, no serif and no monospace.

## Colour

| Token | Value | Role |
|---|---|---|
| `--bg` | `#F6F8FC` | The page. A touch cooler than the logo's plain white ground. |
| `--tint` | `#E9EFF6` | The one tinted band, behind the ayah. |
| `--ink` | `#063909` | Text. The logo's caption green. 12.4:1 on `--bg`. |
| `--ink-soft` | `#2F5E36` | Secondary text. 7:1 on `--bg`. |
| `--green` | `#025107` | Links on hover, focus ring, the logo's arcs. |
| `--gold` | `#CA9703` | Decoration only on light: arches, underlines, the inner dome line. 2.5:1, so never text. |
| `--deep` | `#014405` | The footer block, and the wordmark's green. |
| `--pale-soft` | `#C9DCCB` | Text on the footer. |
| `--gold-lit` | `#E3B72C` | The only gold allowed to carry colour on the deep block. |
| `--hair`, `--hair-strong` | green at 22% and 40% | Rules. |

Gold is rationed: it appears as a line or a shape, never as body text on a light ground.

## Type

Jost for everything Latin, Amiri Quran for the Arabic (a font made for Quranic text, so every mark is drawn). Weight carries the hierarchy: 300 for large type, 400 for reading, 500 for small labels, 600 only for the current nav link.

| Use | Size | Weight |
|---|---|---|
| Page title (About) | up to 9rem | 300, tight |
| Section title | 2.2 to 3.75rem | 300 |
| Mission lines, email | 1.55 to 3.5rem | 300 |
| Arabic ayah | 2.4 to 4.75rem | 400 |
| Body | 1.125rem, line 1.6 | 400 |
| Labels, facts | 0.95 to 1.05rem | 500 |
| Full name in the hero | 0.82 to 1.05rem, tracked caps | 400 |

The tracked caps are used once, for the full name, because the logo itself sets it that way. Body text is never below 17px. Lines stay under about 38rem.

## Layout

One column width (`--wrap`, 70rem) with a fluid gutter. Sections that hold a label and content use a two-column grid, label left (1fr) and content right (2fr), from 56rem up, and stack below that. The label in the mission section stays in view while you read.

## The parts

- **Nav:** the mark and the ICON wordmark, then Home, About, Contact. Hairline underneath. No menu button: three links fit at 360px.
- **Hero (Home):** the mark is the largest thing on the page. Its base line runs on across the whole width as a horizon. "Founded in 2024" and "Newton, Massachusetts" sit on that line, one at each end. The wordmark and full name sit below it.
- **Ayah band (Home):** a tinted full-width stage. The dome's two arcs are drawn large behind the verse (outer in green, inner in gold) and the crescent sits at the top of the dome. The band's bottom edge is a base line.
- **Mission:** a gold arch before each line, hairlines between lines. On Home the four lead phrases link to About. On About the four sentences are in full.
- **Placeholder strip:** "More details coming soon." in a slim ruled strip. Quiet on purpose.
- **About title:** a very large title standing on a rule, with the crescent above it.
- **Contact:** the email is the large item with a gold underline. The mailing address is smaller beneath it.
- **Footer:** one deep green block with the mark recoloured light, and the 501(c)(3) line.

## Motion

One moment: the hero mark draws itself (stroke by stroke), then its solid parts fill in. Hover on the mission lines and the email draws a gold underline. Lower sections fade in once. Everything is off under `prefers-reduced-motion`, and nothing is hidden unless JavaScript runs.

## The logo in code

`images/logo-lockup.svg` is the full lockup, redrawn from the president's image. This is his second logo (2026-11-18): the first said ICONMA in DejaVu Sans. The mark is fitted circles and lines, and the lettering is traced from the image, because the new typeface is not a font we have. The pages carry three symbols (`#mark`, `#crescent`, `#wordmark`), written in by `tools/build-symbols.py`, which read `--mk-green`, `--mk-gold` and `--wm`. That is how the footer shows the mark light on green without a second copy of the art. Every stroke has `pathLength="1"`, which is what lets one `stroke-dashoffset` animation draw the whole mark.

## Keep

- Cool white ground, Jost, thin line. No cream, serif, monospace, purple gradient or stock mosque imagery.
- Gold never as text on a light ground.
- One tinted band and one deep block. A second of either flattens the hierarchy again.
- No numbered sections, no tracked caps above headings, no decoration repeated above every section (an early version had arcs above every section and it read as templated).
- All wording from the president's doc. Placeholders stay generic. Nothing invented.
