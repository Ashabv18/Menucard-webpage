#!/usr/bin/env python3
"""
page-parts.py — the shared parts of every Kaala Mithra sales page.

The theme, the logo, the footer, the floating Call/WhatsApp buttons, the desktop
click-rescue and the contact CONFIG are approved once, on index.html. Every page
the sales team shows should carry the SAME ones, so both generators pull them from
here instead of each keeping a copy that can rot.

  from page_parts import parts
  P = parts()                      # dict of strings, all sliced out of index.html
  P["style"], P["LOGO"], P["footer"], P["floating"], P["script_head"], ...

If index.html changes shape, the asserts here fail loudly — that is the point.
"""
import base64
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "index.html"


def data_uri(rel, mime="image/jpeg"):
    p = ROOT / rel
    assert p.exists(), f"missing image {rel}"
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def patch_once(text, pairs, label):
    """Replace each `old` exactly once; a silent no-op would ship a half-patched page."""
    for old, new in pairs:
        n = text.count(old)
        assert n == 1, f"{label}: expected 1 occurrence, found {n}: {old[:70]!r}"
        text = text.replace(old, new)
    return text


def parts():
    s = SRC.read_text(encoding="utf-8")

    def find(pat):
        m = re.search(pat, s)
        assert m, f"anchor not found in index.html: {pat[:60]}"
        return m

    def between(start, end, include_end=False):
        i = s.index(start)
        j = s.index(end, i + 1)
        return s[i:j + len(end)] if include_end else s[i:j]

    # the theme, copied verbatim so the two pages can be proven byte-identical
    style = s[s.index("<style>") + len("<style>"):s.index("</style>")]

    # the head pieces
    favicon = find(r'(<link rel="icon"[^>]+>)').group(1)
    apple = find(r'(<link rel="apple-touch-icon"[^>]+>)').group(1)
    fonts = "\n".join(l for l in s.splitlines() if "fonts.g" in l or "fonts.googleapis" in l)
    assert len(fonts.splitlines()) == 3, fonts

    LOGO = find(r'class="brand-logo" src="(data:image/png;base64,[^"]+)"').group(1)

    floating = s[s.index("\n<!-- ============ FLOATING ="):s.index("\n<script>")]
    footer = s[s.index("<!-- ============ FOOTER ============"):s.index("</footer>") + len("</footer>")]

    # the script, in four content-anchored slices (line numbers broke once already)
    config = between("/* ============================================================\n   EDIT ONLY THIS BLOCK",
                     "/* ============================================================ */", include_end=True).rstrip()
    rewrite = between('  const tel = "tel:+" + CONFIG.phone;',
                      "  if (yr) yr.textContent = new Date().getFullYear();", include_end=True)
    rescue = between("  /* ============================================================\n     CONTACT RESCUE",
                     "  /* ---- gentle scroll reveal").rstrip()
    reveal = between("  /* ---- gentle scroll reveal", "\n})();").rstrip()
    assert "const CONFIG = {" in config and "CONTACT RESCUE" in rescue
    assert "IntersectionObserver" in reveal and "extraPhonesOut" in rewrite
    assert "window.__kmForms" not in rescue + reveal and "checkBtn" not in rewrite
    assert rescue.count("if (PANEL) {") == 1 and rescue.rstrip().endswith("}"), rescue[-90:]
    for leaked in ("sendEnquiry", "buildMailto", "wireForm", "manualFallback", "mobileIssue", "__kmForms"):
        assert leaked not in rewrite + rescue + reveal, f"{leaked} leaked out of the form block"

    script = "\n".join([config, "(function(){", rewrite, rescue, reveal, "})();"])

    return {
        "root": ROOT,
        "src_html": s,
        "style": style,
        "favicon": favicon,
        "apple": apple,
        "fonts": fonts,
        "LOGO": LOGO,
        "footer": footer,
        "floating": floating,
        "config": config,
        "rewrite": rewrite,
        "rescue": rescue,
        "reveal": reveal,
        "script": script,
        "data_uri": data_uri,
        "patch_once": patch_once,
    }


if __name__ == "__main__":
    p = parts()
    print("index.html parts extracted cleanly:")
    for k in ("style", "LOGO", "footer", "floating", "script"):
        print(f"  {k:9s} {len(p[k]):>8,} chars")
