"""
build-menu-design.py — generates menu-card.html: the MENU CARD DESIGN page for clients.

For the restaurant / café / cloud-kitchen owner who asks "who will design my menu card?". It
explains what a card has to do, what we need from them, which formats exist and what they keep
afterwards — then converts, on WhatsApp and click-to-call.

The page shows **no sample menus and no mock-ups**. It used to carry four drawn menu cards, then
a phone mock-up beside a working QR code; both were removed on request, and the checks at the
bottom of this file refuse to write the page if any part of them comes back. Nothing here is
invented content, so there is nothing to label as demo — and no price anywhere on the page,
theirs or ours. Kaala Mithra's fee is quoted after the current menu is seen, never printed.

Theme, logo, footer, floating Call/WhatsApp buttons and the desktop click-rescue are copied
verbatim out of index.html through page_parts.py, so the pages can never drift apart.

  python3 build-menu-design.py            write menu-card.html
  python3 build-menu-design.py --check    build to /tmp, compare, write nothing
"""
import pathlib
import re
import sys

from page_parts import parts

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "menu-card.html"

P = parts()
style, favicon, apple, fonts = P["style"], P["favicon"], P["apple"], P["fonts"]
LOGO, FLOATING, FOOTER = P["LOGO"], P["floating"], P["footer"]
CONFIG, REWRITE, RESCUE, REVEAL = P["config"], P["rewrite"], P["rescue"], P["reveal"]
data_uri, patch_once = P["data_uri"], P["patch_once"]

HERO = data_uri("assets/menu-hero.jpg")
REVEAL_GUARD = ".reveal{opacity:1 !important; transform:none !important}"


STRIP = [
    ("Table-top tent", "Both sides printed, stands on the table"),
    ("A4 / A3 single sheet", "Laminated, counter-facing, cheapest to reprint"),
    ("Bi-fold", "Groups of items in a hand-sized card"),
    ("Tri-fold", "Takeaway hand-out, address on the flap"),
    ("Square card", "Café tables, and it looks right in a photo"),
    ("Digital menu (QR)", "One link, updated the day your prices change"),
    ("Wall menu", "Big type for a counter, read in three seconds"),
]

STEPS = [
    ("Send what you already have", "A photo of the current menu, a WhatsApp note or a spreadsheet — any of it. Nothing to prepare."),
    ("We return two directions", "Two designs for the same content, side by side, so you choose between finished looks and not adjectives."),
    ("You pick one, we refine it", "Your dishes, your prices, your colours. We keep going until you sign the layout off."),
    ("Files and a live menu", "Print-ready PDFs with bleed, the editable source, and a scannable link for the phone version."),
]

HANDLING = [
    ("Layout &amp; typography", "Hierarchy, spacing and sizes that stay readable at 90 cm on a wall and on a 6-inch screen."),
    ("Menu grouping", "Sections in the order guests actually decide, so the dishes you want to sell sit where the eye lands."),
    ("Print preparation", "Bleed, margins, colour profiles — so the printer does not email you questions at 11 PM."),
    ("The digital copy", "The same card as a phone page behind a QR, updated when your prices move."),
]

NOTES = [
    ("Why no fee is printed on this page",
     "A menu design depends on how many pages, how many languages and how soon you need it. We look at your "
     "current menu and quote the same day — usually while you are still on the call."),
    ("Your menu is not published",
     "We do not put your card in a gallery, on our socials or in an advert. The design, the print files and the "
     "menu link are handed over and stay yours — which is also why this page shows no sample menus."),
    ("Photographs of your food",
     "If your dishes need shooting we will say so, instead of dressing the card with stock photos that are not "
     "your food. The one photograph on this page is a blank card, waiting for content."),
    ("What you keep",
     "The editable source files, the print PDFs and the menu link. Change a price next month and you are not "
     "locked to us to print a new card."),
]

VS_BAD = ["Every line bold, so nothing stands out and the eye gives up",
          "Prices in three different columns, none of them lined up",
          "The dishes you want to sell buried at the bottom of a wall of text",
          "One language on the card, so half the room has to ask",
          "Reprinted from a Word file, so the print shop &ldquo;fixes&rdquo; it"]
VS_GOOD = ["Three typefaces at most, and a size step you can feel from a chair",
           "Prices in one aligned column, easy to change next month",
           "Groups in the order guests decide, with the eye landing where you want it",
           "Two or three scripts set properly, so nothing looks machine-translated",
           "Print-ready PDF with bleed, plus the same card behind a QR"]


STRIP_HTML = "\n".join(f"""      <div class="strip-item reveal"><span class="strip-ico"><svg viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/></svg></span>
        <b>{t}</b><span>{d}</span></div>""" for (t, d) in STRIP)

STEPS_HTML = "\n".join(f"""      <li class="step reveal"><span class="step-num">{i + 1:02d}</span><h3>{t}</h3><p>{d}</p></li>"""
                      for i, (t, d) in enumerate(STEPS))

HANDLING_HTML = "\n".join(f"""      <div class="why-item reveal"><span class="why-ico"><svg viewBox="0 0 24 24" fill="none"
        stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 17l6-6 4 4 6-7"/></svg></span>
        <h3>{t}</h3><p>{d}</p></div>""" for (t, d) in HANDLING)

NOTES_HTML = "\n".join(f"""      <div class="doc-col reveal"><h3>{t}</h3><p class="doc-note" style="margin-top:0">{d}</p></div>"""
                       for (t, d) in NOTES)


def vs(items, mark):
    return "".join(
        '<li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" '
        f'aria-hidden="true"><path d="{mark}"/></svg><span>{t}</span></li>' for t in items)


HEADER = f"""<header class="site">
  <div class="wrap nav">
    <a href="#top" class="brand" aria-label="Kaala Mithra — AI Tech Solution, home">
      <img class="brand-logo" src="{LOGO}" alt="Kaala Mithra — AI Tech Solution. Idea Today. Impact Tomorrow." width="642" height="270">
      <span class="brand-text" style="display:flex; flex-direction:column; gap:3px; flex:none; padding-left:14px; border-left:1px solid rgba(2,4,19,.10)">
        <b class="brand-sub" style="font-size:20px; font-weight:700; line-height:1.1; letter-spacing:.3px; text-transform:uppercase; white-space:nowrap; color:#8a3bff">Menu Card Design</b>
        <span style="font-size:11px; font-weight:600; letter-spacing:1.1px; text-transform:uppercase; line-height:1.3; white-space:nowrap; color:#5b6478">Print &middot; Digital &middot; QR &middot; Editable files</span>
      </span>
    </a>
    <nav class="links">
      <a href="#compare">Before &amp; after</a>
      <a href="#digital">Digital menu</a>
      <a href="#formats">Formats</a>
      <a href="#process">How it works</a>
    </nav>
    <div class="nav-cta">
      <a href="https://wa.me/916361842299" target="_blank" rel="noopener noreferrer" class="btn btn-gold js-wa">Send your menu</a>
    </div>
  </div>
</header>"""

HERO_HTML = f"""<section class="hero" id="top">
  <div class="wrap">
    <div class="hero-grid">
      <div>
        <span class="eyebrow">Menu card design</span>
        <h1>A menu card that does the <span class="grad-text">selling</span> for you</h1>
        <p class="lead">Menu cards laid out the way they will print — not a poster, not a Word file. <b>Send us
          the menu you have today</b>, a photo is enough, and we will show you the same content done properly.</p>
        <div class="btn-row">
          <a href="https://wa.me/916361842299" target="_blank" rel="noopener noreferrer" class="btn btn-wa js-wa">
            <svg class="ico" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.04 2C6.6 2 2.2 6.4 2.2 11.84c0 1.74.46 3.44 1.32 4.94L2 22l5.36-1.4a9.86 9.86 0 004.68 1.18h.01c5.43 0 9.84-4.4 9.84-9.84S17.47 2 12.04 2z"/></svg>
            <span class="js-fill">WhatsApp us your menu</span>
          </a>
          <a href="tel:+916361842299" class="btn btn-primary js-tel"><span class="js-fill">Call +91 63618 42299</span></a>
        </div>
        <div class="hero-badges">
          <span class="badge">Print-ready PDFs</span>
          <span class="badge">Digital menu + QR</span>
          <span class="badge">You keep the source files</span>
        </div>
        <p class="hero-note"><b>No sample menus and no stock claims.</b> Nothing on this page is somebody
          else&rsquo;s card, and we do not publish the menus we design — you see your own, built from what you
          send us. Our design fee is never printed here either; it is quoted after we see your menu.</p>
      </div>
      <figure class="vis vis-hero reveal">
        <img src="{HERO}" alt="A blank printed menu card lying on a desk, waiting for the content" width="1120" height="840">
        <figcaption><b>The blank card is the brief.</b> Tell us what you serve and we fill it.</figcaption>
      </figure>
    </div>
  </div>
</section>"""

COMPARE = f"""<section id="compare">
  <div class="wrap">
    <div class="center">
      <span class="eyebrow">Before &amp; after</span>
      <h2>What lands in your inbox today</h2>
      <p class="lead">Same dishes, same prices, same number of pages. The difference is whether it reads.</p>
    </div>
    <div class="vs">
      <div class="vs-col vs-bad">
        <div class="vs-head">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color:var(--red)"><circle cx="12" cy="12" r="9"/><path d="M15 9l-6 6M9 9l6 6"/></svg>
          <h3>The file you already have</h3>
        </div>
        <ul class="vs-list">{vs(VS_BAD, "M18 6L6 18M6 6l12 12")}</ul>
      </div>
      <div class="vs-col vs-good">
        <div class="vs-head">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color:var(--green)"><circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.5 2.5L16 9.5"/></svg>
          <h3>What we hand back</h3>
        </div>
        <ul class="vs-list">{vs(VS_GOOD, "M5 13l4 4L19 7")}</ul>
      </div>
    </div>
  </div>
</section>"""

DIGITAL = f"""<section class="why" id="digital">
  <div class="wrap">
    <div class="center">
      <span class="eyebrow eyebrow-dark">The digital half</span>
      <h2>One card — printed, and on the phone</h2>
      <p class="lead">A printed card goes out of date the week a price moves. The QR version does not: the link
        stays the same and we change what it shows. Both come off one layout, so they never disagree.</p>
    </div>
    <div class="why-grid">
{HANDLING_HTML}
    </div>
  </div>
</section>"""

FORMATS_SEC = f"""<section id="formats">
  <div class="wrap">
    <div class="center">
      <span class="eyebrow">Formats</span>
      <h2>Choose the shape, we handle the rest</h2>
      <p class="lead">One design, cut for every place a menu lives in your restaurant.</p>
    </div>
    <div class="strip">
      <div class="strip-grid">
{STRIP_HTML}
      </div>
    </div>
    <p class="strip-note">Sizes are typical for each format — the final trim is decided with your printer.</p>
  </div>
</section>"""

PROCESS = f"""<section id="process">
  <div class="wrap">
    <div class="center">
      <span class="eyebrow">How it works</span>
      <h2>Four steps, and you only do the first one</h2>
      <p class="lead">Turnaround depends on how fast your content and your price list come back to us — that is the
        part we cannot do for you.</p>
    </div>
    <ol class="steps">
{STEPS_HTML}
    </ol>
  </div>
</section>"""

NOTES_SEC = f"""<section id="notes">
  <div class="wrap">
    <div class="center">
      <span class="eyebrow">Small print, in plain words</span>
      <h2>Before you ask</h2>
    </div>
    <div class="docs">
{NOTES_HTML}
    </div>
  </div>
</section>"""

CTA = """<section class="cta" id="order">
  <div class="wrap">
    <div class="cta-split">
      <div>
        <span class="eyebrow eyebrow-dark">Show us your menu</span>
        <h2>Send a photo. Get two designs back.</h2>
        <p>The current card, the wall menu, a screenshot of your listing on a delivery app — whatever exists today.
          We will tell you what the layout is costing you and quote the same day.</p>
      </div>
      <div>
        <div class="btn-row">
          <a href="https://wa.me/916361842299" target="_blank" rel="noopener noreferrer" class="btn btn-wa js-wa">
            <svg class="ico" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.04 2C6.6 2 2.2 6.4 2.2 11.84c0 1.74.46 3.44 1.32 4.94L2 22l5.36-1.4a9.86 9.86 0 004.68 1.18h.01c5.43 0 9.84-4.4 9.84-9.84S17.47 2 12.04 2z"/></svg>
            <span class="js-fill">Send it on WhatsApp</span>
          </a>
          <a href="tel:+916361842299" class="btn btn-light js-tel"><span class="js-fill">Call +91 63618 42299</span></a>
        </div>
        <p class="cta-fine">No form on this page, on purpose &mdash; <b>a photo lands in a WhatsApp thread with
          a person</b>, and the quote comes back down the same thread.</p>
      </div>
    </div>
  </div>
</section>"""

FOOTER_FINAL = patch_once(FOOTER, [
    ('<p class="tagline">Protect your brand name, logo and tagline with a registered trademark — search, filing, objection replies, renewal and enforcement, handled end to end by Kaala Mithra.</p>',
     '<p class="tagline">Menu cards, menus on phones, brand identity and the trademark protection behind the name — '
     'designed and handled end to end by Kaala Mithra.</p>'),
    ('          <li><a href="#why">Why register a trademark</a></li>\n          <li><a href="#services">What we handle</a></li>\n          <li><a href="#process">How it works</a></li>\n          <li><a href="#documents">Documents needed</a></li>\n          <li><a href="#faq">FAQ</a></li>\n',
     '          <li><a href="#compare">Before &amp; after</a></li>\n'
     '          <li><a href="#digital">Digital menu &amp; QR</a></li>\n'
     '          <li><a href="#formats">Formats &amp; sizes</a></li>\n'
     '          <li><a href="#process">How it works</a></li>\n'
     '          <li><a href="#order">Send a photo</a></li>\n'),
    ('          <li><a href="#services">Trademark search &amp; clearance</a></li>\n          <li><a href="#services">Registration &amp; filing</a></li>\n          <li><a href="#services">Objection reply &amp; hearing</a></li>\n          <li><a href="#services">Renewal &amp; restoration</a></li>\n          <li><a href="#services">Opposition &amp; rectification</a></li>\n          <li><a href="#services">Madrid Protocol (global filing)</a></li>\n',
     '          <li><a href="#compare">Why a card stops selling</a></li>\n'
     '          <li><a href="#formats">Table tents, bi-folds, wall menus</a></li>\n'
     '          <li><a href="#notes">What you keep</a></li>\n'
     '          <li><a href="#digital">QR menu that stays current</a></li>\n'),
    ('<a href="#check" class="btn btn-primary foot-cta">Check my brand name</a>',
     '<a href="#order" class="btn btn-primary foot-cta">Send us your menu</a>'),
    ('<p class="legal">Information on this page is general guidance on Indian trademark practice and is not legal advice for a specific matter.</p>',
     '<p class="legal">No client menu appears on this page. Print sizes are typical — the final trim is '
     'confirmed with your printer.</p>'),
], "footer retarget")

CSS = """
  /* ==========================================================
     MENU CARD DESIGN PAGE — one rule of its own (.strip-note); the rest is the theme
     ------------------------------------------------------------------------
     Three blocks were removed on request and must stay out: the four sample menu cards, the phone
     mock-up with the QR demo, and the order-desk contact list. The page sells the service in words
     and hands over to one CTA band, so it owns almost no CSS of its own — the result, not
     unfinished work.
     ========================================================== */
  /* the small note the formats section carries */
  .strip-note{margin:18px 0 0; text-align:center; color:var(--muted); font-size:.82rem}

  @media print{
    /* the cards that used to print one to a page are gone, so the page itself is the hand-out:
       drop the controls and the shadows, keep every row unbroken. The dark bands (.why / .cta) are
       already forced to print with their background by the theme block copied from index.html. */
    .btn-row, .btn-more{display:none !important}
    .vs-col, .strip-item, .step, .doc-col{box-shadow:none; page-break-inside:avoid}
    .reveal{opacity:1 !important; transform:none !important}
  }
"""



page = f"""<!DOCTYPE html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{favicon}
{apple}
<!-- with scripts blocked the scroll-reveal rule would hide the whole page -->
<noscript><style>{REVEAL_GUARD}</style></noscript>

<!-- social share preview (what WhatsApp / LinkedIn show when the sales team sends the link) -->
<meta property="og:type" content="website">
<meta property="og:site_name" content="Kaala Mithra — AI Tech Solution">
<meta property="og:title" content="Menu Card Design for restaurants, cafés & cloud kitchens | Kaala Mithra — AI Tech Solution">
<meta property="og:description" content="Menu card design for restaurants, cafés and cloud kitchens: print formats cut for each place a menu lives, a digital menu behind a working QR, and the files are yours. Sample content is labelled as sample content.">
<meta property="og:image" content="assets/kaalamithra-logo.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="assets/kaalamithra-logo.png">
<!-- Poppins to match kaalamithra-branding.vercel.app. Optional: the page falls back
     to system fonts offline, so delete these 3 lines if you need a 100% offline file. -->
{fonts}

<title>Menu Card Design | Kaala Mithra — AI Tech Solution</title>
<meta name="description" content="Menu card design for restaurants, cafés, cloud kitchens and events: print formats cut for each place a menu lives, print-ready PDFs with bleed, a QR digital menu that stays current, and the editable files are yours. Our fee is quoted after we see your menu.">

<!-- ==================================================================
     THIS PAGE IS GENERATED — edit build-menu-design.py, then re-run it.
     ------------------------------------------------------------------
     * Theme, footer, contact numbers and the desktop click-rescue come
       from index.html through page_parts.py, so the pages agree.
     * Nothing on this page is invented: no sample menu, no mock-up, no
       client gallery, no prices. Three demo blocks (the four sample cards,
       the phone mock-up with its QR, the order-desk contact list) were
       removed on request and must stay out - the test suite enforces that.
       A client's real menu never appears here without their consent.
     * No Kaala Mithra fee appears anywhere. If one is ever agreed, it
       belongs in a quote, not on a hand-out that goes stale.
=================================================================== -->

<style>{style}</style>
<style>{CSS}</style>
</head>
<body>

{HEADER}

{HERO_HTML}


{COMPARE}

{DIGITAL}

{FORMATS_SEC}

{PROCESS}

{NOTES_SEC}

{CTA}

{FOOTER_FINAL}

{FLOATING}

<script>
{CONFIG}
(function(){{
{REWRITE}
{RESCUE}
{REVEAL}}})();
</script>
</body>
</html>
"""

# ------------------------------------------------------------------ self-checks
body = page[page.index("<body>"):]
# base64 image blobs are noise for text greps ("INR" hides inside them), so strip them first
bodyText = re.sub(r"data:[^'\"]+", "", body)
assert not any(m in bodyText for m in ("₹", "Rs.", "INR")), "no money on the page at all: no demo menu, and never our own fee"
for leak in ("testimonial", "success rate", "Client Stories", "years of experience", "our fees", "charges ₹"):
    assert leak.lower() not in bodyText.lower(), f"leak: {leak}"
assert "[EDIT]" not in bodyText.replace(re.sub(r"data:[^'\"]+", "", FOOTER_FINAL), ""), "placeholder outside the copied footer note"
assert 'href="https://wa.me/916361842299" target="_blank" rel="noopener noreferrer"' in bodyText
assert "wa.me/916361842299?text" not in bodyText, "WhatsApp links stay bare, like the branding site"
assert "mc-demo" not in page and "mc-fig" not in page and "stage-card" not in page and ".mc{" not in CSS, \
    "the sample-card section and its CSS must be gone entirely, not just hidden"
assert not any(w in page for w in ("Copper Cup", "Espresso", "ph-list", "phone-screen", "qr-img", "qr-card", "digital-row")), "a removed block came back"
assert "we do not publish the menus we design" in bodyText.lower(), "it must still say why there are no samples"
for t in ["div", "section", "ul", "li", "article", "figure", "span", "header", "footer", "button", "ol", "p",
          "h2", "h3", "h4", "h5", "nav", "a", "code", "em", "b", "label"]:
    o = len(re.findall(r"<%s[\s>]" % t, body))
    c = len(re.findall(r"</%s>" % t, body))
    assert o == c, f"unbalanced <{t}>: {o} open / {c} close"
assert ".strip-note{" in CSS and not any(t in CSS for t in (".phone", ".qr-", ".digital-row", ".mc", ".stage")), "the only CSS this page owns is one note under the format chips"
assert ".strip-item{" in style, "the format chips are styled by the theme block copied from index.html"
assert "--photo-" not in page, "the per-card photo variables are gone with the section"
# the hero photo is the one image this page adds; every other blob is copied in from index.html
for _mime in ("jpeg", "png"):
    _copied = sum(b.count("data:image/" + _mime) for b in (style, FOOTER, LOGO, favicon, apple))
    _extra = 1 if _mime == "jpeg" else 0
    assert page.count("data:image/" + _mime) == _copied + _extra, f"no image of our own may survive except the hero ({_mime})"
assert "#designs" not in page and "priceToggle" not in page and "setFormat" not in page and ".fmtn" not in CSS
# every in-page anchor must land somewhere: this is what catches a link to a removed section
_ids = set(re.findall(r'id="([a-zA-Z0-9_-]+)"', page))
_dead = sorted({a for a in re.findall(r'href="#([a-zA-Z0-9_-]+)"', page) if a not in _ids})
assert not _dead, f"anchors point at sections that no longer exist: {_dead}"
# scoped to the body: the theme block in <head> legitimately still styles .contact-list,
# because the trademark page uses it
# scoped to the markup, not the script: the contact script copied from index.html still names
# #extraPhonesOut / #addrOut, and that is fine - it fills them behind existence guards
_body = page[page.index("<body>"):page.index("<script>")]
assert not any(w in _body for w in ('id="desk"', "contact-list", "extraPhonesOut", "addrOut")), \
    "the order desk markup is back, in whole or in part"
assert "if (exLi &&" in page and "if (addr &&" in page, \
    "the copied contact script lost the guards that make a missing desk safe"
for _ghost in ("sample card", "tap a format", "Four layouts", "This QR actually works", "Demo content"):
    assert _ghost not in bodyText.lower(), f"the copy still advertises a removed block: {_ghost}"
assert "menu-card.html" not in bodyText  # the page never refers to its own filename

if "--check" in sys.argv:
    pathlib.Path("/tmp/menu-design.preview.html").write_text(page, encoding="utf-8")
    same = OUT.exists() and OUT.read_text(encoding="utf-8") == page
    print(f"would write {len(page.encode()):,} B · {len(STRIP)} formats · {len(STEPS)} steps · 0 prices · "
          f"{'identical to the file on disk' if same else 'CHANGES PENDING'}")
else:
    OUT.write_text(page, encoding="utf-8")
    print(f"menu-card.html written: {len(page.encode()):,} B · {len(STRIP)} formats · {len(STEPS)} steps · "
          f"{len(HANDLING)} handled · {len(NOTES)} notes · 0 prices, 0 sample menus")
