#!/usr/bin/env python3
"""Build 13 JVZoo 2026 review pages from the ai-flip-domains.html template."""
import html as H
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
PRODUCTS = []
_ns = {"PRODUCTS": PRODUCTS}
for _f in ["products_data.py", "products_data2.py", "products_data3.py", "products_data4.py",
         "products_data5.py", "products_data6.py", "products_data7.py"]:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), _f)) as _fh:
        exec(_fh.read(), _ns)
PRODUCTS = _ns["PRODUCTS"]
BASE = os.path.expanduser("~/workspace/djw-site")
STYLES = open(os.path.join(BASE, "build", "lp_styles.css")).read()
SITE = "https://davidjwoodbury.com"
GTAG = "G-Z44B6SEPWT"


def esc(s):
    return H.escape(s, quote=True)


def cta_link(p):
    """Affiliate link if verified, else sales URL with TODO comment."""
    if p.get("affiliate_url"):
        return p["affiliate_url"], ""
    todo = (f"<!-- TODO: replace with {p['affiliate_url'] or 'https://jvz7.com/c/298459/{PRODUCT_ID}/'} "
            f"— look up \"{p['name']}\" in JVZoo dashboard (Find Products) -->")
    return p["sales_url"], todo


def faq_schema(p, url):
    items = []
    for q, a in p["faqs"]:
        # strip tags for schema text
        a_text = re.sub(r"<[^>]+>", "", a)
        q_text = re.sub(r"<[^>]+>", "", q)
        q_esc = json_str(q_text)
        a_esc = json_str(a_text)
        items.append(
            '    {\n      "@type": "Question",\n'
            '      "name": ' + q_esc + ',\n'
            '      "acceptedAnswer": {\n        "@type": "Answer",\n'
            '        "text": ' + a_esc + '\n      }\n    }'
        )
    return (
        '  <script type="application/ld+json">\n  {\n'
        '    "@context": "https://schema.org",\n'
        '    "@type": "FAQPage",\n'
        f'    "mainEntityOfPage": "{url}",\n'
        '    "mainEntity": [\n' + ",\n".join(items) + "\n    ]\n  }\n  </script>"
    )


def json_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ") + '"'


def build_page(p):
    url = f"{SITE}/{p['slug']}.html"
    link, todo_comment = cta_link(p)
    slug_safe = esc(p["slug"])

    vendor_bit = f" by {esc(p['vendor'])}" if p.get("vendor") and p["vendor"] != "Unknown" else ""
    if p.get("price") == "Unknown":
        price_bit = ""
        pricing_lede = "Pricing isn't listed on the sales page — check the link below for current pricing."
        price_main = '<p class="price-main">See sales page</p>'
    else:
        price_bit = f" at {esc(p['price'])} {esc(p['price_note'])}"
        pricing_lede = f"{esc(p['name'])} is {esc(p['price'])} {esc(p['price_note'])} for the front end."
        price_main = f"<p class=\"price-main\">{esc(p['price'])}<span style=\"font-size:1.2rem;font-weight:400\"> {esc(p['price_note'])}</span></p>"

    features_html = "\n".join(
        f'''        <div class="feature-card">
          <span class="feature-icon">{icon}</span>
          <h3>{esc(title)}</h3>
          <p>{desc}</p>
        </div>'''
        for icon, title, desc in p["features"]
    )
    who_html = "\n".join(
        f'''        <li>
          <span class="check">✓</span>
          <span>{item}</span>
        </li>'''
        for item in p["who_for"]
    )
    intro_html = "\n".join(f"      <p>{para}</p>" for para in p["intro_paras"])
    context_html = "\n".join(f"      <p>{para}</p>" for para in p["context_paras"])
    pricing_features = "\n".join(f"          <li>{esc(f)}</li>" for f in p["pricing_features"])
    faqs_html = "\n".join(
        f'''        <details class="faq-item"{' open' if i == 0 else ''}>
          <summary><h3>{q}</h3></summary>
          <p>{a}</p>
        </details>'''
        for i, (q, a) in enumerate(p["faqs"])
    )
    summary_meta = (
        f"David J Woodbury reviews {p['name']} ({p['vendor']}), launched {p['launch_date']} on JVZoo. "
        f"{p['price']} {p['price_note']}, {p['commission']} affiliate commission. {p['tagline']}"
    )

    # Structured data: item type is SoftwareApplication for software, Product for
    # training/info products. Offers only when price is a clean numeric value.
    item_type = p.get("item_type", "SoftwareApplication")
    if item_type == "SoftwareApplication":
        item_block = (
            '"@type": "SoftwareApplication",\n'
            f'      "name": {json_str(p["name"])},\n'
            '      "applicationCategory": "BusinessApplication",\n'
            f'      "description": {json_str(re.sub(r"<[^>]+>", "", p["highlight"]))}'
        )
    else:
        item_block = (
            f'"@type": {json_str(item_type)},\n'
            f'      "name": {json_str(p["name"])},\n'
            f'      "description": {json_str(re.sub(r"<[^>]+>", "", p["highlight"]))}'
        )
    price_m = re.match(r"^\$([\d,]+(?:\.\d{1,2})?)$", (p.get("price") or "").strip())
    offers_block = (
        f',\n      "offers": {{"@type": "Offer", "price": '
        f'"{price_m.group(1).replace(",", "")}", "priceCurrency": "USD"}}\n'
        if price_m else "\n"
    )
    review_json = (
        '  <script type="application/ld+json">\n'
        "  {\n"
        '    "@context": "https://schema.org",\n'
        '    "@type": "Review",\n'
        f'    "headline": "{esc(p["meta_title"])}",\n'
        f'    "description": "{esc(p["meta_desc"])}",\n'
        f'    "author": {{"@type": "Person", "name": "David J Woodbury", "url": "{SITE}"}},\n'
        f'    "publisher": {{"@type": "Person", "name": "David J Woodbury", "url": "{SITE}"}},\n'
        '    "itemReviewed": {\n'
        f"      {item_block}{offers_block}"
        '    },\n'
        f'    "mainEntityOfPage": {{"@type": "WebPage", "@id": "{url}"}}\n'
        "  }\n"
        "  </script>"
    )

    todo_html = f"\n  {todo_comment}" if todo_comment else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={GTAG}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{GTAG}');
  </script>

  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(p['meta_title'])}</title>
  <meta name="description" content="{esc(p['meta_desc'])}">
  <meta name="author" content="David J Woodbury">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <meta name="summary" content="{esc(summary_meta)}">
  <link rel="canonical" href="{url}">

  <!-- Open Graph -->
  <meta property="og:type" content="article">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{esc(p['meta_title'])}">
  <meta property="og:description" content="{esc(p['meta_desc'])}">
  <meta property="og:image" content="{SITE}/assets/profile.jpg">
  <meta property="og:site_name" content="David J Woodbury">
  <meta property="og:locale" content="en_US">
  <meta property="article:published_time" content="2026-10-03">
  <meta property="article:author" content="David J Woodbury">

  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:creator" content="@davidjustin84">
  <meta name="twitter:site" content="@davidjustin84">
  <meta name="twitter:title" content="{esc(p['meta_title'])}">
  <meta name="twitter:description" content="{esc(p['meta_desc'])}">
  <meta name="twitter:image" content="{SITE}/assets/profile.jpg">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css">
  <link rel="icon" href="assets/favicon.svg" type="image/svg+xml">

{review_json}
{faq_schema(p, url)}

  <style>{STYLES}
  </style>
</head>
<body>

  <header>
    <nav aria-label="Main navigation">
      <div class="logo">
        <a href="/" style="display:flex;align-items:center;gap:1rem;text-decoration:none;">
          <img src="assets/profile.jpg" alt="David J Woodbury" class="logo-img" width="44" height="44">
          <span>David J Woodbury</span>
        </a>
      </div>
      <ul class="nav-links">
        <li><a href="/#tools">AI Tools</a></li>
        <li><a href="/#about">About</a></li>
        <li><a href="/#contact">Contact</a></li>
      </ul>
    </nav>
  </header>

  <main>

    <!-- Hero -->
    <div class="lp-hero">
      <div class="lp-badge">{esc(p['badge'])}</div>
      <h1>{esc(p['tagline'])}</h1>
      <p class="subhead">{esc(p['name'])}{vendor_bit} — launched {esc(p['launch_date'])} on JVZoo{price_bit}. Here's my honest take.</p>
      {todo_html}
      <a href="{esc(link)}" target="_blank" rel="nofollow sponsored" class="lp-cta-primary">
        Check Out {esc(p['name'])} →
      </a>
    </div>

    <hr class="divider">

    <!-- Personal Intro -->
    <section class="lp-section">
      <h2>{esc(p['intro_title'])}</h2>
{intro_html}

      <div class="highlight-box">
        <p>{p['highlight']}</p>
      </div>
    </section>

    <hr class="divider">

    <!-- What It Does -->
    <section class="lp-section">
      <h2>What {esc(p['name'])} Actually Does</h2>

      <div class="features-grid">
{features_html}
      </div>
    </section>

    <hr class="divider">

    <!-- Who It's For -->
    <section class="lp-section">
      <h2>Is This For You?</h2>
      <p>Let me be straight about who gets the most out of this:</p>

      <ul class="for-who-list">
{who_html}
      </ul>

      <p>{p['not_for']}</p>
    </section>

    <hr class="divider">

    <!-- Context -->
    <section class="lp-section">
      <h2>{esc(p['context_title'])}</h2>
{context_html}
    </section>

    <hr class="divider">

    <!-- Pricing -->
    <section class="lp-section">
      <h2>What's the Investment?</h2>
      <p>{pricing_lede}</p>

      <div class="pricing-box">
        {price_main}
        <p class="price-period">{esc(p['vendor']) if p.get('vendor') != 'Unknown' else 'JVZoo'} · Launched {esc(p['launch_date'])} · JVZoo</p>
        <ul class="pricing-features">
{pricing_features}
        </ul>
        <a href="{esc(link)}" target="_blank" rel="nofollow sponsored" class="lp-cta-primary" style="font-size:1rem;">
          Get {esc(p['name'])} →
        </a>
        <p class="guarantee">✓ {esc(p['guarantee'])}</p>
      </div>
    </section>

    <hr class="divider">

    <!-- FAQ -->
    <section class="lp-faq">
      <h2>Quick FAQ</h2>
      <div class="faq-container">
{faqs_html}
      </div>

      <!-- Author note -->
      <div class="author-note">
        <img src="assets/profile.jpg" alt="David J Woodbury">
        <div class="author-note-text">
          <strong>David J Woodbury</strong>
          10-year digital marketing veteran. Top ClickBank affiliate. #1 affiliate partner. I review and recommend AI tools that create real leverage for online entrepreneurs — not hype, not fluff.
          <br><a href="/" style="color:var(--accent-primary);text-decoration:none;">← Back to all my tool recommendations</a>
        </div>
      </div>

      <div style="text-align:center;margin-top:3rem;">
        <a href="{esc(link)}" target="_blank" rel="nofollow sponsored" class="lp-cta-primary">
          Get {esc(p['name'])} →
        </a>
      </div>
    </section>

    <p class="affiliate-disclaimer">
      <strong>Disclosure:</strong> This page contains affiliate links. If you purchase {esc(p['disclosure_product'])} through my link, I may earn a commission at no extra cost to you. I only recommend tools I genuinely believe in. Results vary — this is not a guaranteed income source.
    </p>

  </main>

  <footer>
    <p>&copy; 2026 David J Woodbury. All rights reserved.</p>
    <p><a href="/privacy.html">Privacy Policy</a> | <a href="/terms.html">Terms of Service</a></p>
    <p class="footer-note">David J Woodbury is a digital marketing consultant and AI tools expert based in the United States.</p>
  </footer>

  <script src="script.js"></script>
</body>
</html>
"""


def main():
    out = []
    for p in PRODUCTS:
        page = build_page(p)
        path = os.path.join(BASE, p["slug"] + ".html")
        with open(path, "w") as f:
            f.write(page)
        out.append((p["slug"], len(page)))
        print(f"built {p['slug']}.html ({len(page)} bytes)")
    print(f"\n{len(out)} pages built")


if __name__ == "__main__":
    main()
