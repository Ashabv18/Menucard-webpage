# Menu card design — the client-facing page

**`menu-card.html` is the deliverable.** One file, everything inside it (theme, logo, photographs,
footer) is inlined, so it opens from a laptop, a phone, an e-mail attachment or an offline
screen-share. 273,865 bytes, no internet needed for its own content.

| What you want to do | How |
|---|---|
| Open it | double-click `menu-card.html` |
| Show it on a call | scroll top to bottom, then leave it on the **CTA band** (*Send a photo. Get two designs back.*) |
| Send a printed hand-out | open in a browser → `Ctrl/Cmd + P` → Save as PDF. Print styles drop the buttons and keep each block whole |
| Send the file | attach `menu-card.html` — it is self-contained, nothing else is needed |
| Verify it before sending | `node test-menu-design.js` → **84 passed, 0 failed** |

## What the page is, and what it deliberately is not

It sells **menu card design** for restaurants, cafés, cloud kitchens and events: hero offer →
before/after (five problems, five fixes) → what the design covers, print and phone → seven formats
→ four steps → small print → one CTA band.

Three things were removed on request and **must stay out**:

1. the four sample menu cards with the format switcher,
2. the phone mock-up and the QR demo card,
3. the `#desk` order-desk contact list.

So the page shows **no sample menus, no mock-ups and no prices** — `₹`, `Rs.` and `INR` appear
nowhere on it. Nothing is labelled "demo" because nothing is invented any more; instead the hero
and the small print state the policy: no client's card is published, and the design fee is quoted
after we see their menu, never printed. Contact routes that remain: Call + WhatsApp in the hero and
the CTA band, the floating bubbles, and **the footer**, which already carries all three numbers,
both inboxes (`kaalamithra.sales@gmail.com`, `tech@kaalamithra-ai.com`) and "India · Remote
Friendly" — that is why removing the desk section lost nothing. There is **no form** on the page,
so nothing can fail silently.

If a client insists on seeing a card before hiring us: photograph *their* menu, lay it out, send
that as a proposal. Do not rebuild a gallery of stock samples.

## Editing it — do not hand-edit the HTML

`menu-card.html` is **generated**. Open `build-menu-design.py` and edit the data lists at the top:

| List | What it drives |
|---|---|
| `STRIP` | the seven format chips |
| `STEPS` | the four-step "how it works" |
| `HANDLING` | the four cards in the digital-half band |
| `NOTES` | the small print |
| `VS_BAD` / `VS_GOOD` | the before/after bullets |
| `HERO_HTML` / `COMPARE` / `CTA` blocks | the wording |

Then:

```bash
python3 build-menu-design.py          # rewrites menu-card.html
python3 build-menu-design.py --check  # prints a preview copy and says whether it matches the file on disk
node test-menu-design.js              # 84 checks (first time only: npm install jsdom)
```

`index.html` **must stay in this folder** — the theme, logo, footer, floating buttons and the
desktop click-rescue are copied out of it by `page_parts.py`, text anchor by text anchor, so the
trademark page and this one can never drift apart. The one image the page adds of its own is
`assets/menu-hero.jpg`.

Changing the phone number means two places: the numbers written into this page's own markup
(search `6361842299` in `build-menu-design.py` — 7 occurrences in the header, hero and CTA), and
the `CONFIG` block near line 1297 of `index.html`, which drives the floating buttons, the desktop
number panel and the label fill-ins. Then re-run the generator.

## What the test suite will not let you do

`build-menu-design.py` refuses to write the file, and `test-menu-design.js` fails, if any of these
reappear: a price symbol of any kind, the words `Rs.` or `INR`, a testimonial, a "success rate", a
client story, an invented years-in-business claim, a `[EDIT]` placeholder outside the copied footer
note, an `href="#x"` pointing at a section that does not exist, any markup from the three removed
blocks, an image inlined by this page other than the hero, or copy advertising a feature the page
no longer has (e.g. "tap a format"). It also checks the WhatsApp anchors stay bare
(`https://wa.me/916361842299`, `target="_blank" rel="noopener noreferrer"`, exactly as on
kaalamithra-branding.vercel.app), the theme block is byte-identical to `index.html`, and the contact
list is never placed on the dark CTA band.

## Files in this folder

```
menu-card.html         the page you send                        273,865 B
build-menu-design.py   the generator - edit this, not the HTML       24,612 B
page_parts.py          copies theme/logo/footer/JS out of index.html 
index.html             the source those blocks come from                452,514 B
assets/menu-hero.jpg   the hero photograph, inlined at build             42,636 B
test-menu-design.js    84 checks, needs jsdom                            21,399 B
README.md              this file                                    5,060 B

Folder total on disk: 824,418 B.
```
