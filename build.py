#!/usr/bin/env python3
"""Build the published site from _src/. Standard library only.

Usage:  python build.py

Every file in _src/pages/ is a page body with a JSON block at the top:

    <!--
    {"url": "/services/aeo-geo/", "title": "...", "description": "...",
     "type": "service", "name": "AEO & GEO", "crumbs": [["Services", "/services/"]]}
    -->
    <section>...page body, starting with the H1...</section>

build.py wraps each body in the shared <head>, header and footer, adds the
breadcrumb trail and the JSON-LD for the page type, writes the HTML to the
page's URL, then rewrites sitemap.xml. Files whose name starts with "_" are
skipped (use them for drafts and templates).

Page types: home, hub, service, industry, work, about, contact, blog, post, 404.
Optional keys: "image" (social preview, site path), "published" and
"modified" (posts, YYYY-MM-DD), "client" (work pages), "audience" (industry
pages), "noindex" (true to keep a page out of search and the sitemap).
Any <details><summary>Q</summary>A</details> blocks on a service, industry
or post page are also published as FAQPage structured data.
"""
import datetime
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "_src"
ORIGIN = "https://" + (ROOT / "CNAME").read_text().strip()
TODAY = datetime.date.today().isoformat()
SITE = "Content Authority Lab"
ORG_ID = ORIGIN + "/#org"
PERSON_ID = ORIGIN + "/about/#selwan-omar"
DEFAULT_IMAGE = "/work/vervo-logistics-seo.png"

META = re.compile(r"^\s*<!--\s*(\{.*?\})\s*-->\s*", re.S)
FAQ = re.compile(r"<details[^>]*>\s*<summary>(.*?)</summary>(.*?)</details>", re.S)
TAGS = re.compile(r"<[^>]+>")


def text(fragment):
    return " ".join(html.unescape(TAGS.sub(" ", fragment)).split())


def esc(s):
    return html.escape(s, quote=True)


def org():
    return {
        "@type": "ProfessionalService",
        "@id": ORG_ID,
        "name": SITE,
        "url": ORIGIN + "/",
        "description": "Bilingual Arabic and English content team for SEO, answer engine optimization and generative engine optimization.",
        "email": "team@contentauthoritylab.com",
        "founder": {"@type": "Person", "@id": PERSON_ID, "name": "Selwan Omar"},
        "address": {"@type": "PostalAddress", "addressLocality": "Cairo", "addressCountry": "EG"},
        "areaServed": ["AE", "SA", "EG", "LB", "GB"],
        "knowsAbout": [
            "Search engine optimization", "Answer engine optimization",
            "Generative engine optimization", "Content strategy",
            "Arabic and English localization", "Technical writing",
        ],
    }


def person():
    return {
        "@type": "Person",
        "@id": PERSON_ID,
        "name": "Selwan Omar",
        "jobTitle": "Founder and Lead Strategist",
        "worksFor": {"@id": ORG_ID},
        "alumniOf": {"@type": "CollegeOrUniversity", "name": "University of Hamburg"},
        "knowsLanguage": ["ar", "en"],
        "sameAs": ["https://www.linkedin.com/in/selwanomar/", "https://clippings.me/selwan-omar"],
    }


def breadcrumb(meta):
    trail = [["Home", "/"]] + meta.get("crumbs", []) + [[meta.get("name", meta["title"]), meta["url"]]]
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": n, "item": ORIGIN + u}
            for i, (n, u) in enumerate(trail, 1)
        ],
    }


def jsonld(meta, body):
    t, url = meta["type"], ORIGIN + meta["url"]
    image = ORIGIN + meta.get("image", DEFAULT_IMAGE)
    graph = []
    if t == "home":
        graph += [org(), {"@type": "WebSite", "@id": ORIGIN + "/#site", "url": ORIGIN + "/",
                          "name": SITE, "publisher": {"@id": ORG_ID}, "inLanguage": "en"}]
    elif t in ("service", "industry"):
        svc = {"@type": "Service", "name": meta["name"], "serviceType": meta["name"],
               "description": meta["description"], "url": url, "provider": {"@id": ORG_ID},
               "areaServed": ["AE", "SA", "EG", "LB", "GB"]}
        if meta.get("audience"):
            svc["audience"] = {"@type": "BusinessAudience", "name": meta["audience"]}
        graph += [svc, breadcrumb(meta)]
    elif t == "work":
        graph += [{"@type": "Article", "headline": meta["h1"] if "h1" in meta else meta["title"],
                   "description": meta["description"], "image": image, "url": url,
                   "mainEntityOfPage": url, "dateModified": meta.get("modified", TODAY),
                   "author": {"@id": ORG_ID}, "publisher": {"@id": ORG_ID},
                   "about": {"@type": "Organization", "name": meta["client"]}},
                  breadcrumb(meta)]
    elif t == "post":
        graph += [{"@type": "BlogPosting", "headline": meta["h1"], "description": meta["description"],
                   "image": image, "url": url, "mainEntityOfPage": url,
                   "datePublished": meta["published"], "dateModified": meta.get("modified", meta["published"]),
                   "author": {"@id": ORG_ID}, "publisher": {"@id": ORG_ID}},
                  breadcrumb(meta)]
    elif t in ("hub", "blog", "about", "contact"):
        page_type = {"hub": "CollectionPage", "blog": "Blog", "about": "AboutPage", "contact": "ContactPage"}[t]
        graph += [{"@type": page_type, "name": meta.get("name", meta["title"]), "url": url,
                   "description": meta["description"], "publisher": {"@id": ORG_ID}},
                  breadcrumb(meta)]
        if t in ("about", "contact"):
            graph.append(org())
        if t == "about":
            graph.append(person())
    else:
        return ""
    if t in ("service", "industry", "post"):
        qa = [{"@type": "Question", "name": text(q),
               "acceptedAnswer": {"@type": "Answer", "text": text(a)}} for q, a in FAQ.findall(body)]
        if qa:
            graph.append({"@type": "FAQPage", "mainEntity": qa})
    data = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)
    return f'<script type="application/ld+json">\n{data}\n</script>'


def head(meta, body):
    noindex = meta.get("noindex") or meta["type"] == "404"
    image = ORIGIN + meta.get("image", DEFAULT_IMAGE)
    og_type = "article" if meta["type"] in ("work", "post") else "website"
    lines = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{esc(meta['title'])}</title>",
        f'<meta name="description" content="{esc(meta["description"])}">',
    ]
    if noindex:
        lines.append('<meta name="robots" content="noindex">')
    else:
        lines += [
            f'<link rel="canonical" href="{ORIGIN + meta["url"]}">',
            f'<meta property="og:type" content="{og_type}">',
            f'<meta property="og:site_name" content="{SITE}">',
            f'<meta property="og:title" content="{esc(meta.get("og_title", meta["title"]))}">',
            f'<meta property="og:description" content="{esc(meta["description"])}">',
            f'<meta property="og:url" content="{ORIGIN + meta["url"]}">',
            f'<meta property="og:image" content="{image}">',
            '<meta name="twitter:card" content="summary_large_image">',
        ]
    lines += [
        '<meta name="theme-color" content="#16231f">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        '<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap" rel="stylesheet">',
        '<link rel="stylesheet" href="/assets/style.css">',
        "<link rel=\"icon\" href=\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='22' fill='%2316231f'/><text x='50' y='68' font-size='54' font-family='Arial' font-weight='700' text-anchor='middle' fill='%23b7d5a5'>C</text></svg>\">",
    ]
    ld = "" if noindex else jsonld(meta, body)
    if ld:
        lines.append(ld)
    lines.append("</head>")
    return "\n".join(lines)


def crumbs_html(meta):
    if meta["type"] in ("home", "404"):
        return ""
    items = [["Home", "/"]] + meta.get("crumbs", [])
    links = "".join(f'<li><a href="{u}">{esc(n)}</a></li>' for n, u in items)
    here = f'<li aria-current="page">{esc(meta.get("name", meta["title"]))}</li>'
    return f'<nav class="crumbs wrap" aria-label="Breadcrumb"><ol>{links}{here}</ol></nav>\n'


def mark_current(fragment, url):
    """Flag the nav link for this page (and its section) as current."""
    def sub(m):
        href = m.group(1)
        if href == url:
            return m.group(0).replace("<a ", '<a aria-current="page" ', 1)
        return m.group(0)
    return re.sub(r'<a href="([^"]+)"', sub, fragment)


def render(meta, body, partials):
    header = mark_current(partials["header"], meta["url"])
    return "\n".join([
        head(meta, body),
        "<body>",
        '<a class="skip" href="#main">Skip to content</a>',
        header,
        '<main id="main">',
        crumbs_html(meta) + body.strip(),
        "</main>",
        partials["footer"],
        '<script src="/assets/site.js" defer></script>',
        "</body>",
        "</html>",
        "",
    ])


def out_path(url):
    rel = url.lstrip("/")
    if rel == "" or rel.endswith("/"):
        rel += "index.html"
    return ROOT / rel


def main():
    partials = {n: (SRC / f"{n}.html").read_text(encoding="utf-8").strip() for n in ("header", "footer")}
    built, problems = [], []
    for src in sorted((SRC / "pages").rglob("*.html")):
        if src.name.startswith("_"):
            continue
        raw = src.read_text(encoding="utf-8")
        m = META.match(raw)
        if not m:
            sys.exit(f"{src}: missing the JSON block at the top")
        meta, body = json.loads(m.group(1)), raw[m.end():]
        if len(meta["title"]) > 60:
            problems.append(f"{meta['url']}: title is {len(meta['title'])} chars")
        if len(meta["description"]) > 155:
            problems.append(f"{meta['url']}: description is {len(meta['description'])} chars")
        dest = out_path(meta["url"])
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(render(meta, body, partials), encoding="utf-8")
        built.append(meta)

    urls = [m["url"] for m in built if not (m.get("noindex") or m["type"] == "404")]
    order = lambda u: (u != "/", u.count("/"), u)
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    lines += [f"  <url><loc>{ORIGIN + u}</loc><lastmod>{TODAY}</lastmod></url>" for u in sorted(urls, key=order)]
    lines.append("</urlset>\n")
    (ROOT / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8")

    print(f"Built {len(built)} pages, {len(urls)} in sitemap.xml")
    for p in problems:
        print("  WARNING " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
