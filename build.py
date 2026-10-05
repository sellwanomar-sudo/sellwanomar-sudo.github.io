#!/usr/bin/env python3
"""Build the site from content/ into _site/.

Usage:  pip install -r requirements.txt
        python build.py              # writes _site/
        python audit_site.py _site   # checks it

Content lives in content/ as JSON, one file per page. Edit it through the CMS
at /admin/ or by hand. This script owns everything structural: URLs, the
header and footer menus (generated from the service and industry lists),
breadcrumbs, internal links, JSON-LD, canonical and social tags, the
Content-Security-Policy, sitemap.xml and the copied static files.

An empty content field renders as a visible [CONTENT: ...] box, and the
audit lists every one that's left.
"""
import datetime
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
OUT = ROOT / "_site"
DOMAIN = (ROOT / "CNAME").read_text().strip()
ORIGIN = "https://" + DOMAIN
ORG_ID = ORIGIN + "/#org"
PERSON_ID = ORIGIN + "/about/#selwan-omar"
TODAY = datetime.date.today().isoformat()
STATIC = ["assets", "work", "admin", ".well-known", "CNAME", "robots.txt"]

# Same policy on every public page. GitHub Pages can't send headers, so it ships as a meta tag.
CSP = ("default-src 'self'; script-src 'self'; style-src 'self' https://fonts.googleapis.com; "
       "font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src https://api.web3forms.com; "
       "form-action 'self' https://api.web3forms.com; base-uri 'self'; object-src 'none'; upgrade-insecure-requests")

TAGS = re.compile(r"<[^>]+>")
esc = lambda s: html.escape(s or "", quote=True)


# ---------------------------------------------------------------- content helpers

def load(rel):
    return json.loads((CONTENT / rel).read_text(encoding="utf-8"))


def load_dir(name):
    items = {}
    for p in sorted((CONTENT / name).glob("*.json")):
        d = load(f"{name}/{p.name}")
        d["slug"], d["_src"] = p.stem, p
        items[p.stem] = d
    return dict(sorted(items.items(), key=lambda kv: (kv[1].get("order", 99), kv[0])))


def md(text):
    return markdown.markdown(text or "", extensions=["tables", "sane_lists"])


def md_inline(text):
    out = md(text)
    return out[3:-4] if out.startswith("<p>") and out.endswith("</p>") and out.count("<p>") == 1 else out


def todo(hint):
    return f'<p class="todo">[CONTENT: {esc(hint)}]</p>'


def block(text, hint):
    return md(text) if (text or "").strip() else todo(hint)


def lines(text):
    return "<br>".join(esc(x) for x in (text or "").split("\n"))


def plain(fragment):
    return " ".join(html.unescape(TAGS.sub(" ", fragment)).split())


def short_date(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%b %Y')}"


def lastmod(path):
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(path)], cwd=ROOT,
                             capture_output=True, text=True, timeout=10).stdout.strip()
        return out or TODAY
    except (OSError, subprocess.SubprocessError):
        return TODAY


# ---------------------------------------------------------------- site data

SITE = load("site.json")
SERVICES = load_dir("services")
INDUSTRIES = load_dir("industries")
WORK = load_dir("work")
POSTS = dict(sorted(load_dir("posts").items(), key=lambda kv: kv[1]["date"], reverse=True))
PAGES = {p.stem: load(f"pages/{p.name}") for p in (CONTENT / "pages").glob("*.json")}

S_URL = lambda s: f"/services/{s}/"
I_URL = lambda s: f"/industries/{s}/"
W_URL = lambda s: f"/work/{s}/"
P_URL = lambda s: POSTS[s].get("url") or f"/blog/{s}/"


def check_refs():
    """Fail fast on links to pages that don't exist (for example a renamed case study)."""
    bad = []
    for s in SERVICES.values():
        bad += [f"services/{s['slug']}: proof case {p['case']}" for p in s.get("proof", []) if p["case"] not in WORK]
        bad += [f"services/{s['slug']}: industry {i}" for i in s.get("industries", []) if i not in INDUSTRIES]
        bad += [f"services/{s['slug']}: reading {r}" for r in s.get("reading", []) if r not in POSTS]
        if s.get("hub_proof") and s["hub_proof"] not in WORK:
            bad.append(f"services/{s['slug']}: hub_proof {s['hub_proof']}")
    for d in INDUSTRIES.values():
        bad += [f"industries/{d['slug']}: service {x['service']}" for x in d.get("services", []) if x["service"] not in SERVICES]
        bad += [f"industries/{d['slug']}: case {c}" for c in d.get("cases", []) if c not in WORK]
    for w in WORK.values():
        bad += [f"work/{w['slug']}: service {x}" for x in w.get("services", []) if x not in SERVICES]
        bad += [f"work/{w['slug']}: industry {x}" for x in w.get("industries", []) if x not in INDUSTRIES]
        bad += [f"work/{w['slug']}: next {x}" for x in w.get("next", []) if x not in WORK]
    home = PAGES["home"]
    bad += [f"home: featured {x}" for x in home["work_section"]["featured"] if x not in WORK]
    bad += [f"home: service card {c['service']}" for c in home["service_cards"] if c["service"] not in SERVICES]
    if bad:
        sys.exit("Broken references in content/:\n  " + "\n  ".join(bad))


# ---------------------------------------------------------------- structured data

def org():
    return {
        "@type": "ProfessionalService", "@id": ORG_ID, "name": SITE["name"], "url": ORIGIN + "/",
        "description": "Bilingual Arabic and English content team for SEO, answer engine optimization and generative engine optimization.",
        "email": SITE["email"],
        "founder": {"@type": "Person", "@id": PERSON_ID, "name": PAGES["about"]["founder"]["name"]},
        "address": {"@type": "PostalAddress", "addressLocality": "Cairo", "addressCountry": "EG"},
        "areaServed": ["AE", "SA", "EG", "LB", "GB"],
        "knowsAbout": ["Search engine optimization", "Answer engine optimization", "Generative engine optimization",
                       "Content strategy", "Arabic and English localization", "Technical writing"],
    }


def person():
    f = PAGES["about"]["founder"]
    return {"@type": "Person", "@id": PERSON_ID, "name": f["name"], "jobTitle": f["role"],
            "worksFor": {"@id": ORG_ID},
            "alumniOf": {"@type": "CollegeOrUniversity", "name": "University of Hamburg"},
            "knowsLanguage": ["ar", "en"], "sameAs": [SITE["linkedin"], SITE["clippings"]]}


def breadcrumb(page):
    trail = [["Home", "/"]] + page.get("crumbs", []) + [[page["name"], page["url"]]]
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": n, "item": ORIGIN + u} for i, (n, u) in enumerate(trail, 1)]}


def faq_schema(faqs):
    qa = [{"@type": "Question", "name": f["question"],
           "acceptedAnswer": {"@type": "Answer", "text": plain(md(f["answer"]))}}
          for f in faqs if f.get("question") and f.get("answer")]
    return [{"@type": "FAQPage", "mainEntity": qa}] if qa else []


def jsonld(page):
    t, url = page["type"], ORIGIN + page["url"]
    image = ORIGIN + page.get("image", SITE["default_image"])
    if t == "home":
        g = [org(), {"@type": "WebSite", "@id": ORIGIN + "/#site", "url": ORIGIN + "/", "name": SITE["name"],
                     "publisher": {"@id": ORG_ID}, "inLanguage": "en"}]
    elif t in ("service", "industry"):
        svc = {"@type": "Service", "name": page["name"], "serviceType": page["name"], "description": page["description"],
               "url": url, "provider": {"@id": ORG_ID}, "areaServed": ["AE", "SA", "EG", "LB", "GB"]}
        if page.get("audience"):
            svc["audience"] = {"@type": "BusinessAudience", "name": page["audience"]}
        g = [svc, breadcrumb(page)] + faq_schema(page.get("faqs", []))
    elif t == "work":
        g = [{"@type": "Article", "headline": page["h1"], "description": page["description"], "image": image,
              "url": url, "mainEntityOfPage": url, "dateModified": page["modified"],
              "author": {"@id": ORG_ID}, "publisher": {"@id": ORG_ID},
              "about": {"@type": "Organization", "name": page["client"]}}, breadcrumb(page)]
    elif t == "post":
        g = [{"@type": "BlogPosting", "headline": page["h1"], "description": page["description"], "image": image,
              "url": url, "mainEntityOfPage": url, "datePublished": page["published"],
              "dateModified": page["modified"], "author": {"@id": ORG_ID}, "publisher": {"@id": ORG_ID}},
             breadcrumb(page)] + faq_schema(page.get("faqs", []))
    else:
        kind = {"hub": "CollectionPage", "blog": "Blog", "about": "AboutPage", "contact": "ContactPage"}[t]
        g = [{"@type": kind, "name": page["name"], "url": url, "description": page["description"],
              "publisher": {"@id": ORG_ID}}, breadcrumb(page)]
        if t in ("about", "contact"):
            g.append(org())
        if t == "about":
            g.append(person())
    data = json.dumps({"@context": "https://schema.org", "@graph": g}, ensure_ascii=False, indent=1)
    data = data.replace("</", "<\\/")  # a "</script>" inside a string can't end the block early
    return f'<script type="application/ld+json">\n{data}\n</script>'


# ---------------------------------------------------------------- shell

def head(page):
    noindex = page["type"] == "404"
    image = ORIGIN + page.get("image", SITE["default_image"])
    og_type = "article" if page["type"] in ("work", "post") else "website"
    out = ["<!doctype html>", '<html lang="en">', "<head>", '<meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width, initial-scale=1">',
           f'<meta http-equiv="Content-Security-Policy" content="{CSP}">',
           '<meta name="referrer" content="strict-origin-when-cross-origin">',
           f"<title>{esc(page['title'])}</title>",
           f'<meta name="description" content="{esc(page["description"])}">']
    if noindex:
        out.append('<meta name="robots" content="noindex">')
    else:
        out += [f'<link rel="canonical" href="{ORIGIN + page["url"]}">',
                f'<meta property="og:type" content="{og_type}">',
                f'<meta property="og:site_name" content="{esc(SITE["name"])}">',
                f'<meta property="og:title" content="{esc(page.get("og_title", page["title"]))}">',
                f'<meta property="og:description" content="{esc(page["description"])}">',
                f'<meta property="og:url" content="{ORIGIN + page["url"]}">',
                f'<meta property="og:image" content="{image}">',
                '<meta name="twitter:card" content="summary_large_image">']
    out += ['<meta name="theme-color" content="#16231f">',
            '<link rel="preconnect" href="https://fonts.googleapis.com">',
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
            '<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&amp;display=swap" rel="stylesheet">',
            '<link rel="stylesheet" href="/assets/style.css">',
            '<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">']
    if not noindex:
        out.append(jsonld(page))
    out.append("</head>")
    return "\n".join(out)


def header(url):
    def link(href, label, cls=""):
        cur = ' aria-current="page"' if href == url else ""
        c = f' class="{cls}"' if cls else ""
        return f'<a href="{href}"{c}{cur}>{esc(label)}</a>'

    svc = "".join(f"<li>{link(S_URL(k), s['name'])}</li>" for k, s in SERVICES.items())
    ind = "".join(f"<li>{link(I_URL(k), d['label'])}</li>" for k, d in INDUSTRIES.items())
    return f'''<header class="site-header">
  <nav class="wrap nav" aria-label="Main">
    <a href="/" class="logo">{esc(SITE["name"])}<span>.</span></a>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="nav-links">Menu</button>
    <ul class="links" id="nav-links">
      <li class="has-menu"><button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu-services">Services</button>
        <ul class="submenu" id="menu-services">{svc}<li class="all">{link("/services/", "All services")}</li></ul></li>
      <li>{link("/work/", "Work")}</li>
      <li class="has-menu"><button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu-industries">Industries</button>
        <ul class="submenu" id="menu-industries">{ind}<li class="all">{link("/industries/", "All industries")}</li></ul></li>
      <li>{link("/about/", "About")}</li>
      <li>{link("/blog/", "Blog")}</li>
      <li>{link("/contact/", "Start a project", "btn dark")}</li>
    </ul>
  </nav>
</header>'''


def footer():
    svc = "".join(f'<li><a href="{S_URL(k)}">{esc(s["name"])}</a></li>' for k, s in SERVICES.items())
    ind = "".join(f'<li><a href="{I_URL(k)}">{esc(d["label"])}</a></li>' for k, d in INDUSTRIES.items())
    return f'''<footer class="site-footer">
  <div class="wrap foot-grid">
    <div class="foot-brand">
      <a href="/" class="logo">{esc(SITE["name"])}<span>.</span></a>
      <p>{esc(SITE["footer_text"])}</p>
      <p><a href="mailto:{esc(SITE["email"])}">{esc(SITE["email"])}</a><br><a href="{esc(SITE["linkedin"])}" rel="noopener noreferrer">LinkedIn</a></p>
    </div>
    <div><p class="foot-head">Services</p><ul>{svc}</ul></div>
    <div><p class="foot-head">Industries</p><ul>{ind}</ul></div>
    <div><p class="foot-head">Company</p><ul><li><a href="/work/">Work</a></li><li><a href="/about/">About</a></li><li><a href="/blog/">Blog</a></li><li><a href="/contact/">Contact</a></li></ul></div>
  </div>
  <div class="wrap foot-base">
    <span>&copy; <span data-year>{TODAY[:4]}</span> {esc(SITE["name"])}</span>
    <span>Service area: {" · ".join(esc(a) for a in SITE["service_area"])}</span>
  </div>
</footer>'''


def crumbs(page):
    if page["type"] in ("home", "404"):
        return ""
    items = "".join(f'<li><a href="{u}">{esc(n)}</a></li>' for n, u in [["Home", "/"]] + page.get("crumbs", []))
    return f'<nav class="crumbs wrap" aria-label="Breadcrumb"><ol>{items}<li aria-current="page">{esc(page["name"])}</li></ol></nav>\n'


def render(page, body):
    return "\n".join([head(page), "<body>", '<a class="skip" href="#main">Skip to content</a>', header(page["url"]),
                      '<main id="main">', crumbs(page) + body.strip(), "</main>", footer(),
                      '<script src="/assets/site.js" defer></script>', "</body>", "</html>", ""])


# ---------------------------------------------------------------- shared components

def kpis(items, cls="kpis", item="div"):
    if not items:
        return ""
    if cls == "kpis":
        return '<div class="kpis">' + "".join(f"<div><b>{esc(k['value'])}</b>{esc(k['label'])}</div>" for k in items) + "</div>"
    return '<div class="metrics">' + "".join(
        f'<div class="metric"><b>{esc(k["value"])}</b><span>{esc(k["label"])}</span></div>' for k in items) + "</div>"


def work_card(slug):
    w = WORK[slug]
    if w.get("cover"):
        thumb = f'<a class="thumb" href="{W_URL(slug)}" tabindex="-1" aria-hidden="true"><img src="{esc(w["cover"])}" alt="" loading="lazy"></a>'
    else:
        thumb = f'<div class="thumb blank" aria-hidden="true">{esc(w["tag"])}</div>'
    return f'''<article class="work" data-service="{" ".join(w["services"])}" data-industry="{" ".join(w["industries"]) or "none"}">
  {thumb}
  <div class="body">
    <span class="tag">{esc(w["tag"])}</span>
    <h3><a href="{W_URL(slug)}">{esc(w["h1"])}</a></h3>
    <p>{esc(w["summary"])}</p>
    {kpis(w["kpis"])}
    <a class="textlink" href="{W_URL(slug)}">Read the case study →</a>
  </div>
</article>'''


def cta():
    c = SITE["cta"]
    return f'''<section>
  <div class="wrap cta">
    <div>
      <p class="eyebrow">{esc(c["eyebrow"])}</p>
      <h2>{esc(c["heading"])}</h2>
      <p>{esc(c["text"])}</p>
    </div>
    <div class="actions"><a class="btn light" href="/contact/">{esc(c["button"])}</a></div>
  </div>
</section>'''


def start_box():
    b = SITE["start_box"]
    return (f'<div class="box dark"><p class="eyebrow">{esc(b["heading"])}</p><p>{esc(b["text"])}</p>'
            f'<a class="btn light" href="/contact/">{esc(b["button"])}</a></div>')


def faq_block(faqs, hint):
    items = [f for f in faqs if f.get("question")]
    if not items:
        return f'<div class="faq">{todo(hint)}</div>'
    return '<div class="faq">' + "".join(
        f"<details><summary>{esc(f['question'])}</summary>{block(f.get('answer'), 'answer')}</details>" for f in items) + "</div>"


def hero(eyebrow, h1, lead_html, actions=""):
    return f'''<div class="wrap page-hero">
  <p class="eyebrow">{esc(eyebrow)}</p>
  <h1>{esc(h1)}</h1>
  {lead_html}
  {actions}
</div>'''


def lead(text, hint):
    return f'<div class="lead">{md(text)}</div>' if (text or "").strip() else todo(hint)


# ---------------------------------------------------------------- page builders

def page_meta(data, **kw):
    m = {"title": data["title"], "description": data["description"]}
    m.update(kw)
    return m


def build_service(s):
    k = s["slug"]
    proof = "\n".join(
        f'<li><a href="{W_URL(p["case"])}{"#" + p["section"] if p.get("section") else ""}">{esc(p["anchor"])}</a>: '
        f'{esc(WORK[p["case"]]["name"])}. {md_inline(p["note"]) if p.get("note") else todo("one or two sentences on what this proves")}</li>'
        for p in s["proof"])
    inds = "".join(f'<a href="{I_URL(i)}">{esc(INDUSTRIES[i]["label"])}</a>' for i in s["industries"])
    reading = "".join(f'<p><a href="{P_URL(r)}">{esc(POSTS[r]["h1"])}</a></p>' for r in s.get("reading", []))
    others = "".join(f'<li><a href="{S_URL(o)}">{esc(x["name"])}</a></li>' for o, x in SERVICES.items() if o != k)
    body = f'''{hero("Service", s["h1"], lead(s["lead"], "lead paragraph: what this service is, who it is for, and the answer-first summary"),
                '<div class="actions"><a class="btn dark" href="/contact/">Start a project</a><a class="btn" href="#proof">See the proof ↓</a></div>')}
<div class="wrap layout">
<div class="prose">
<h2>What's included</h2>
{block(s["included"], "deliverables, as a short list")}
<h2>How we work</h2>
{block(s["how"], "process, step by step")}
<h2 id="proof">Proof</h2>
<ul>
{proof}
</ul>
<h2>Industries we do this for</h2>
<div class="strip">{inds}</div>
{"<h2>Further reading</h2>" + reading if reading else ""}
<h2>Frequently asked questions</h2>
{faq_block(s["faqs"], "3 to 5 questions and answers")}
</div>
<aside class="aside">
{start_box()}
<div class="box"><p class="eyebrow">Other services</p><ul>{others}</ul></div>
</aside>
</div>
{cta()}'''
    return page_meta(s, url=S_URL(k), type="service", name=s["name"], faqs=s["faqs"],
                     crumbs=[["Services", "/services/"]]), body


def build_industry(d):
    k = d["slug"]
    svcs = "\n".join(f'<li><a href="{S_URL(x["service"])}">{esc(SERVICES[x["service"]]["name"])}</a>: '
                     f'{md_inline(x["note"]) if x.get("note") else todo("what this service looks like for this industry")}</li>'
                     for x in d["services"])
    cases = "\n".join(work_card(c) for c in d["cases"])
    body = f'''{hero("Industry", d["h1"], lead(d["lead"], "lead paragraph: who this is for and the problem we solve in this industry"),
                '<div class="actions"><a class="btn dark" href="/contact/">Start a project</a></div>')}
<div class="wrap layout">
<div class="prose">
<h2>What makes content work in this industry</h2>
{block(d["context"], "the specific search, buyer and compliance realities of this industry")}
<h2>What we do for {esc(d["label"])} brands</h2>
<ul>
{svcs}
</ul>
<h2>Frequently asked questions</h2>
{faq_block(d["faqs"], "3 to 5 questions and answers")}
</div>
<aside class="aside">
{start_box()}
</aside>
</div>
<section>
  <div class="wrap">
    <div class="section-head"><div><p class="eyebrow">Proof</p><h2>Case studies</h2></div></div>
    <div class="workgrid">
{cases}
    </div>
  </div>
</section>
{cta()}'''
    return page_meta(d, url=I_URL(k), type="industry", name=d["name"], audience=d.get("audience"),
                     faqs=d["faqs"], crumbs=[["Industries", "/industries/"]]), body


def build_work(w):
    k = w["slug"]
    secs = []
    for s in w["sections"]:
        sid = f' id="{esc(s["id"])}"' if s.get("id") else ""
        eyebrow = f'<p class="eyebrow">{esc(s["eyebrow"])}</p>' if s.get("eyebrow") else ""
        secs.append(f'<h2{sid}>{esc(s["heading"])}</h2>\n{eyebrow}\n{block(s.get("body"), s["heading"].lower())}\n{kpis(s.get("kpis"), "metrics")}')
    dl = "".join(f'<li><a href="{esc(d["file"])}">{esc(d["label"])}</a></li>' for d in w["downloads"]) \
        or f'<li>{esc(w.get("downloads_note", ""))}</li>'
    used = "".join(f'<li><a href="{S_URL(x)}">{esc(SERVICES[x]["name"])}</a></li>' for x in w["services"])
    inds = "".join(f'<li><a href="{I_URL(x)}">{esc(INDUSTRIES[x]["name"])}</a></li>' for x in w["industries"]) \
        or f'<li>{esc(w.get("industry_note", ""))}</li>'
    nxt = "".join(f'<li><a href="{W_URL(x)}">{esc(WORK[x]["h1"])}</a></li>' for x in w["next"])
    cover = ""
    if w.get("cover"):
        target = w["downloads"][0]["file"] if w["downloads"] else w["cover"]
        cover = f'<figure class="wrap cover"><a href="{esc(target)}"><img src="{esc(w["cover"])}" alt="{esc(w["name"])} case study cover" loading="lazy"></a></figure>'
    body = f'''{hero("Case study · " + w["tag"], w["h1"], f'<p class="lead">{esc(w["summary"])}</p>')}
<div class="wrap">{kpis(w["kpis"], "metrics")}</div>
<div class="wrap layout">
<div class="prose">
{chr(10).join(secs)}
</div>
<aside class="aside">
<div class="box"><p class="eyebrow">Case file</p><ul>{dl}</ul></div>
<div class="box"><p class="eyebrow">Services used</p><ul>{used}</ul></div>
<div class="box"><p class="eyebrow">Industry</p><ul>{inds}</ul></div>
<div class="box"><p class="eyebrow">Next case study</p><ul>{nxt}</ul></div>
</aside>
</div>
{cover}
{cta()}'''
    meta = page_meta(w, url=W_URL(k), type="work", name=w["name"], h1=w["h1"], client=w["client"],
                     modified=lastmod(w["_src"]), crumbs=[["Work", "/work/"]])
    if w.get("cover"):
        meta["image"] = w["cover"]
    return meta, body


def build_post(p):
    date = datetime.date.fromisoformat(p["date"])
    body = f'''<div class="wrap page-hero">
  <p class="eyebrow">{esc(p["eyebrow"])}</p>
  <h1>{esc(p["h1"])}</h1>
  <p class="post-meta">By {esc(SITE["name"])} · {date.day} {date.strftime("%B %Y")} · {esc(p["reading_time"])}</p>
</div>
<div class="wrap pad-bottom">
<article class="prose">
{md(p["body"])}
{"<h2>Frequently asked questions</h2>" + faq_block(p["faqs"], "") if p.get("faqs") else ""}
<div class="author-box">
  <div class="avatar" aria-hidden="true">CAL</div>
  <p>{md_inline(p.get("author_note", ""))} <a href="/contact/">Work with us →</a></p>
</div>
</article>
</div>'''
    return page_meta(p, url=P_URL(p["slug"]), type="post", name=p["breadcrumb"], h1=p["h1"], og_title=p["h1"],
                     published=p["date"], modified=p.get("modified") or p["date"], faqs=p.get("faqs", []),
                     crumbs=[["Blog", "/blog/"]]), body


def post_card(slug, meta_line):
    p = POSTS[slug]
    return f'''<a class="post-card" href="{P_URL(slug)}">
  <span class="meta">{esc(meta_line)}</span>
  <h3>{esc(p["h1"])}</h3>
  <p>{esc(p["summary"])}</p>
  <span class="more">Read article →</span>
</a>'''


def build_home():
    h = PAGES["home"]
    stats = "".join(f'<div class="stat"><b>{esc(s["value"])}</b><span>{esc(s["label"])}</span></div>' for s in h["stats"])
    cards = "\n".join(
        f'<article class="card"><span class="num">{i:02d}</span><h3>{esc(c["heading"])}</h3><p>{esc(c["text"])}</p>'
        f'<a class="textlink" href="{S_URL(c["service"])}">{esc(c["link_text"])}</a></article>'
        for i, c in enumerate(h["service_cards"], 1))
    strip = "".join(f'<a href="{I_URL(k)}">{esc(d["label"])}</a>' for k, d in INDUSTRIES.items())
    ws, ss, ab, bs, p = h["work_section"], h["services_section"], h["about_section"], h["blog_section"], h["panel"]
    featured = "\n".join(work_card(x) for x in ws["featured"])
    posts = "\n".join(post_card(s, f'{x["eyebrow"]} · {x["reading_time"]}') for s, x in list(POSTS.items())[:2])
    empty = f'<div class="post-card empty"><p>{esc(bs["empty_card"])}</p></div>' if len(POSTS) < 3 else ""
    body = f'''<div class="wrap" id="top">
  <div class="hero">
    <div>
      <p class="eyebrow">{esc(h["eyebrow"])}</p>
      <h1>{esc(h["h1"])} <em>{esc(h["h1_highlight"])}</em></h1>
      <p class="lead">{esc(h["lead"])}</p>
      <div class="actions"><a class="btn dark" href="#work">{esc(h["primary_button"])}</a><a class="btn" href="/contact/">{esc(h["secondary_button"])}</a></div>
    </div>
    <aside class="hero-panel" aria-label="At a glance">
      <span class="tiny">{esc(p["label"])}</span>
      <p class="big">{"<br>".join(esc(x) for x in p["lines"])}</p>
      <ul>{"".join(f"<li>{esc(b)}</li>" for b in p["bullets"])}</ul>
    </aside>
  </div>
  <div class="stats" aria-label="Key numbers">{stats}</div>
</div>
<section id="services">
  <div class="wrap">
    <div class="section-head"><div><p class="eyebrow">{esc(ss["eyebrow"])}</p><h2>{lines(ss["heading"])}</h2></div><p>{esc(ss["text"])}</p></div>
    <div class="cards four">
{cards}
    </div>
  </div>
</section>
<section id="industries">
  <div class="wrap">
    <div class="section-head"><div><p class="eyebrow">{esc(h["industries_section"]["eyebrow"])}</p><h2>{esc(h["industries_section"]["heading"])}</h2></div></div>
    <div class="strip">{strip}</div>
  </div>
</section>
<section id="work">
  <div class="wrap">
    <div class="section-head"><div><p class="eyebrow">{esc(ws["eyebrow"])}</p><h2>{lines(ws["heading"])}</h2></div><p>{esc(ws["text"])}</p></div>
    <div class="workgrid four">
{featured}
    </div>
    <p class="actions"><a class="btn dark" href="/work/">{esc(ws["button"])}</a></p>
  </div>
</section>
<section id="about">
  <div class="wrap section-head">
    <div><p class="eyebrow">{esc(ab["eyebrow"])}</p><h2>{esc(ab["heading"])}</h2></div>
    <p>{esc(ab["text"])} <a class="textlink" href="/about/">{esc(ab["link_text"])}</a></p>
  </div>
</section>
<section id="blog">
  <div class="wrap">
    <div class="section-head"><div><p class="eyebrow">{esc(bs["eyebrow"])}</p><h2>{lines(bs["heading"])}</h2></div><p><a class="textlink" href="/blog/">{esc(bs["link_text"])}</a></p></div>
    <div class="postgrid">
{posts}
{empty}
    </div>
  </div>
</section>
{cta()}'''
    return page_meta(h, url="/", type="home", name="Home", og_title=h["title"]), body


def build_about():
    a = PAGES["about"]
    f = a["founder"]
    facts = "".join(f'<li><b>{esc(x["label"])}</b>{esc(x["value"])}</li>' for x in a["facts"])
    tools = "".join(f"<span>{esc(t)}</span>" for t in a["tools"])
    body = f'''{hero(a["eyebrow"], a["h1"], "")}
<div class="wrap layout">
<div class="prose">
{md(a["body"])}
<h2 id="selwan-omar">{esc(f["name"])}, {esc(f["role"])}</h2>
{block(f["bio"], "short bio of the founder and lead strategist")}
<h2>{esc(a["method_heading"])}</h2>
{block(a["method"], "the method, from research to publishing to measurement, and how AI is used in the workflow")}
<h2>Where to go next</h2>
<ul>
  <li><a href="/services/">See what we offer</a></li>
  <li><a href="/work/">Browse the case studies</a></li>
  <li><a href="/contact/">Tell us about your project</a></li>
</ul>
</div>
<aside class="aside">
  <ul class="facts">{facts}</ul>
  <div class="box">
    <p class="eyebrow">Tools</p>
    <div class="chips">{tools}</div>
    <p class="box-link"><a href="{esc(SITE["clippings"])}" rel="noopener noreferrer"><strong>{esc(a["clippings_text"])}</strong></a></p>
  </div>
</aside>
</div>'''
    return page_meta(a, url="/about/", type="about", name="About"), body


def build_contact():
    c = PAGES["contact"]
    opts = "".join(f"<option>{esc(o)}</option>" for o in c["form_options"])
    body = f'''{hero(c["eyebrow"], c["h1"], "")}
<div class="wrap pad-bottom">
  <div class="contact">
    <div>
      <p>{esc(c["text"])}</p>
      <ul class="contact-links">
        <li><a href="mailto:{esc(SITE["email"])}">{esc(SITE["email"])} ↗</a></li>
        <li><a href="{esc(SITE["linkedin"])}" rel="noopener noreferrer">LinkedIn ↗</a></li>
        <li><a href="{esc(SITE["clippings"])}" rel="noopener noreferrer">Clippings.me portfolio ↗</a></li>
      </ul>
    </div>
    <form id="contact-form" action="https://api.web3forms.com/submit" method="POST" novalidate>
      <input type="hidden" name="access_key" value="{esc(SITE["web3forms_key"])}">
      <input type="hidden" name="subject" value="New enquiry from contentauthoritylab.com">
      <input type="hidden" name="from_name" value="Content Authority Lab website">
      <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
      <div class="row">
        <label>Your name<input type="text" name="name" required maxlength="120" autocomplete="name" placeholder="Jane Doe"></label>
        <label>Email<input type="email" name="email" required maxlength="200" autocomplete="email" placeholder="jane@company.com"></label>
      </div>
      <label>What do you need?<select name="service">{opts}</select></label>
      <label>Message<textarea name="message" required maxlength="5000" placeholder="A few lines about your project, website and timeline..."></textarea></label>
      <button class="btn light" type="submit">{esc(c["button"])}</button>
      <p class="form-status" role="status" aria-live="polite"></p>
    </form>
  </div>
</div>'''
    return page_meta(c, url="/contact/", type="contact", name="Contact"), body


def build_hub(kind):
    d = PAGES[kind]
    lead_html = f'<p class="lead">{esc(d["lead"])}</p>' if d.get("lead") else todo("lead paragraph")
    if kind == "services":
        cards = "\n".join(f'''<article class="card"><span class="num">{i:02d}</span>
  <h3><a href="{S_URL(k)}">{esc(s["name"])}</a></h3><p>{esc(s["card_text"])}</p>
  <a class="textlink" href="{W_URL(s["hub_proof"])}">Proof: {esc(WORK[s["hub_proof"]]["h1"])}</a></article>'''
                          for i, (k, s) in enumerate(SERVICES.items(), 1))
        inner = f'<div class="wrap"><div class="cards">\n{cards}\n</div></div>'
    elif kind == "industries":
        cards = "\n".join(f'''<article class="card"><h3><a href="{I_URL(k)}">{esc(x["name"])}</a></h3>
  {f"<p>{esc(x['card_text'])}</p>" if x.get("card_text") else todo("one-sentence summary")}
  <a class="textlink" href="{I_URL(k)}">Explore {esc(x["label"])} →</a></article>''' for k, x in INDUSTRIES.items())
        inner = f'<div class="wrap"><div class="cards two">\n{cards}\n</div></div>'
    elif kind == "work":
        def group(name, label, items):
            btns = "".join(f'<button class="filter" type="button" data-filter="{k}" aria-pressed="false">{esc(v)}</button>' for k, v in items)
            return (f'<div class="filters" role="group" aria-label="Filter by {name}" data-group="{name}"><span class="label">{label}</span>'
                    f'<button class="filter" type="button" data-filter="all" aria-pressed="true">All</button>{btns}</div>')
        cards = "\n".join(work_card(k) for k in WORK)
        inner = f'''<div class="wrap pad-bottom">
  {group("service", "Service", [(k, s["name"]) for k, s in SERVICES.items()])}
  {group("industry", "Industry", [(k, x["label"]) for k, x in INDUSTRIES.items()])}
  <p class="filter-status" role="status" aria-live="polite">Showing {len(WORK)} case studies</p>
  <div class="workgrid">
{cards}
  </div>
</div>'''
    else:  # blog
        cards = "\n".join(post_card(s, f'{short_date(p["date"])} · {p["reading_time"]}')
                          for s, p in POSTS.items())
        inner = f'<div class="wrap pad-bottom"><div class="postgrid">\n{cards}\n</div></div>'
    body = f'{hero(d["eyebrow"], d["h1"], lead_html)}\n{inner}\n{cta() if kind != "blog" else ""}'
    names = {"services": "Services", "industries": "Industries", "work": "Work", "blog": "Blog"}
    return page_meta(d, url=f"/{kind}/", type="blog" if kind == "blog" else "hub", name=names[kind]), body


def build_404():
    body = '''<div class="wrap page-hero">
  <p class="eyebrow">404</p>
  <h1>This page doesn't exist.</h1>
  <p class="lead">It may have moved. Try the homepage or the blog.</p>
  <div class="actions"><a class="btn dark" href="/">Go home</a><a class="btn" href="/work/">See our work</a><a class="btn" href="/blog/">Read the blog</a></div>
</div>'''
    return {"url": "/404.html", "title": "Page not found | " + SITE["name"], "description": "This page doesn't exist.",
            "type": "404", "name": "404"}, body


# ---------------------------------------------------------------- output

def out_path(url):
    rel = url.lstrip("/")
    if rel == "" or rel.endswith("/"):
        rel += "index.html"
    return OUT / rel


def copy_static():
    for name in STATIC:
        src = ROOT / name
        if src.is_dir():
            shutil.copytree(src, OUT / name, dirs_exist_ok=True)
        elif src.is_file():
            shutil.copy2(src, OUT / name)


def main():
    check_refs()
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    copy_static()

    pages = [(build_home(), CONTENT / "pages/home.json"), (build_about(), CONTENT / "pages/about.json"),
             (build_contact(), CONTENT / "pages/contact.json"), (build_404(), None)]
    pages += [(build_hub(k), CONTENT / f"pages/{k}.json") for k in ("services", "industries", "work", "blog")]
    pages += [(build_service(s), s["_src"]) for s in SERVICES.values()]
    pages += [(build_industry(d), d["_src"]) for d in INDUSTRIES.values()]
    pages += [(build_work(w), w["_src"]) for w in WORK.values()]
    pages += [(build_post(p), p["_src"]) for p in POSTS.values()]

    problems, entries = [], []
    for (meta, body), src in pages:
        if len(meta["title"]) > 60:
            problems.append(f"{meta['url']}: title is {len(meta['title'])} chars (max 60)")
        if len(meta["description"]) > 155:
            problems.append(f"{meta['url']}: description is {len(meta['description'])} chars (max 155)")
        dest = out_path(meta["url"])
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(render(meta, body), encoding="utf-8")
        if meta["type"] != "404":
            entries.append((meta["url"], lastmod(src) if src else TODAY))

    entries.sort(key=lambda e: (e[0] != "/", e[0].count("/"), e[0]))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{ORIGIN + u}</loc><lastmod>{d}</lastmod></url>" for u, d in entries]
    (OUT / "sitemap.xml").write_text("\n".join(sm + ["</urlset>", ""]), encoding="utf-8")

    print(f"Built {len(pages)} pages into {OUT.relative_to(ROOT)}/, {len(entries)} in sitemap.xml")
    for p in problems:
        print("  ERROR " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
