#!/usr/bin/env python3
"""Audit the built static site. Standard library only.

Usage:  python audit_site.py [site_root]

Errors (exit code 1):
  - pages more than 2 clicks from home, orphan pages
  - broken internal links (pages and assets)
  - missing, duplicate or overlong titles (> 60) and meta descriptions (> 155)
  - pages without exactly one H1
  - missing canonical
  - missing JSON-LD, or JSON-LD that doesn't parse
  - sitemap coverage, both ways
  - leftover [NEEDS SOURCE] markers
  - missing Content-Security-Policy meta tag (security)
Warnings (reported, don't fail):
  - pages with fewer than 2 inbound internal links
  - canonical that doesn't match the page's own URL
  - em dashes in visible text (house style)
  - unfilled [CONTENT: ...] placeholders
  - external links that open without rel="noopener noreferrer" (security)
"""
import json
import posixpath
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict, deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urldefrag, urlparse

MAX_DEPTH = 2
TITLE_MAX = 60
DESC_MAX = 155
NEEDS_SOURCE = re.compile(r"\[NEEDS SOURCE", re.I)
PLACEHOLDER = re.compile(r"\[CONTENT:")


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = None
        self.description = None
        self.canonical = None
        self.noindex = False
        self.csp = False
        self.external = []
        self.h1 = 0
        self.links = []
        self.assets = []
        self.ids = set()
        self.jsonld = []
        self.text = []
        self._in_title = False
        self._in_jsonld = False
        self._skip = 0  # inside <script>/<style>
        self._buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "title":
            self._in_title, self._buf = True, []
        elif tag == "meta":
            name = (a.get("name") or "").lower()
            if name == "description":
                self.description = (a.get("content") or "").strip()
            elif name == "robots" and "noindex" in (a.get("content") or "").lower():
                self.noindex = True
            elif (a.get("http-equiv") or "").lower() == "content-security-policy":
                self.csp = True
        elif tag == "link":
            rel = (a.get("rel") or "").lower().split()
            if "canonical" in rel:
                self.canonical = a.get("href")
            elif a.get("href") and ({"stylesheet", "icon"} & set(rel)):
                self.assets.append(a["href"])
        elif tag == "h1":
            self.h1 += 1
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])
            if a["href"].startswith(("http://", "https://")):
                self.external.append((a["href"], (a.get("rel") or "").lower().split()))
        elif tag in ("img", "source") and a.get("src"):
            self.assets.append(a["src"])
        elif tag == "script":
            self._skip += 1
            if a.get("src"):
                self.assets.append(a["src"])
            if (a.get("type") or "").lower() == "application/ld+json":
                self._in_jsonld, self._buf = True, []
        elif tag == "style":
            self._skip += 1

    def handle_endtag(self, tag):
        if tag == "title" and self._in_title:
            self.title = "".join(self._buf).strip()
            self._in_title = False
        elif tag == "script":
            self._skip = max(0, self._skip - 1)
            if self._in_jsonld:
                self.jsonld.append("".join(self._buf))
                self._in_jsonld = False
        elif tag == "style":
            self._skip = max(0, self._skip - 1)

    def handle_data(self, data):
        if self._in_title or self._in_jsonld:
            self._buf.append(data)
        elif not self._skip:
            self.text.append(data)


SKIP_DIRS = {"admin"}  # the CMS app shell, not a site page (noindex, blocked in robots.txt)


def is_page_file(p, root):
    rel = p.relative_to(root).parts
    return (p.suffix == ".html" and not any(part.startswith((".", "_")) for part in rel)
            and rel[0] not in SKIP_DIRS)


def file_to_url(p, root):
    rel = p.relative_to(root).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def resolve(href, page_url, host):
    """Return a site-absolute path for an internal href, or None if external."""
    href, frag = urldefrag(href.strip())
    u = urlparse(href)
    if u.scheme in ("mailto", "tel", "javascript", "data"):
        return None, None
    if u.scheme or u.netloc:
        if u.netloc.lower().removeprefix("www.") != host:
            return None, None
        path = u.path or "/"
    elif not href:
        path = page_url  # pure fragment link
    else:
        base = page_url if page_url.endswith("/") else posixpath.dirname(page_url) + "/"
        path = posixpath.normpath(posixpath.join(base, u.path))
        if u.path.endswith("/") and not path.endswith("/"):
            path += "/"
    return unquote(path), frag


def target_file(path, root):
    """Map a site path to a file on disk, following GitHub Pages rules."""
    rel = path.lstrip("/")
    cand = root / rel
    if path.endswith("/"):
        cand = cand / "index.html"
    elif cand.is_dir():
        cand = cand / "index.html"
    if cand.is_file():
        return cand
    if not Path(rel).suffix and (root / (rel + ".html")).is_file():
        return root / (rel + ".html")
    return None


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent).resolve()
    cname = root / "CNAME"
    host = cname.read_text().strip().lower().removeprefix("www.") if cname.exists() else "localhost"
    origin = f"https://{host}"

    errors, warnings = [], []
    err = lambda url, msg: errors.append(f"{url}: {msg}")
    warn = lambda url, msg: warnings.append(f"{url}: {msg}")

    pages = {}  # url -> parser
    files = {}  # url -> path
    for p in sorted(root.rglob("*.html")):
        if not is_page_file(p, root):
            continue
        url = file_to_url(p, root)
        parser = PageParser()
        parser.feed(p.read_text(encoding="utf-8"))
        pages[url], files[url] = parser, p

    if "/" not in pages:
        print("ERROR: no index.html at site root")
        return 1

    indexable = {u for u, pp in pages.items() if not pp.noindex}

    # Links, broken links, link graph
    graph = defaultdict(set)
    for url, pp in pages.items():
        for href in pp.links:
            path, frag = resolve(href, url, host)
            if path is None:
                continue
            tf = target_file(path, root)
            if tf is None:
                err(url, f"broken link -> {href}")
                continue
            if tf.suffix == ".html" and is_page_file(tf, root):
                turl = file_to_url(tf, root)
                if turl != url:
                    graph[url].add(turl)
                if frag and frag not in pages[turl].ids:
                    warn(url, f"missing anchor #{frag} on {turl}")
            elif tf.suffix == ".html":
                err(url, f"links to unpublished file -> {href}")
        for src in pp.assets:
            path, _ = resolve(src, url, host)
            if path is not None and target_file(path, root) is None:
                err(url, f"missing asset -> {src}")

    # Click depth and orphans (crawl from home)
    depth = {"/": 0}
    q = deque(["/"])
    while q:
        u = q.popleft()
        for v in graph[u]:
            if v not in depth:
                depth[v] = depth[u] + 1
                q.append(v)
    inbound = defaultdict(set)
    for u, targets in graph.items():
        for v in targets:
            inbound[v].add(u)
    for url in sorted(indexable):
        if url not in depth:
            err(url, "orphan: not reachable from home")
        elif depth[url] > MAX_DEPTH:
            err(url, f"{depth[url]} clicks from home (max {MAX_DEPTH})")
        if url != "/" and len(inbound[url]) < 2:
            warn(url, f"only {len(inbound[url])} inbound internal link(s)")

    # Titles, descriptions, H1, canonical, JSON-LD, markers
    titles, descs = defaultdict(list), defaultdict(list)
    for url, pp in sorted(pages.items()):
        if not pp.title:
            err(url, "missing <title>")
        else:
            titles[pp.title].append(url)
            if len(pp.title) > TITLE_MAX:
                err(url, f"title is {len(pp.title)} chars (max {TITLE_MAX}): {pp.title!r}")
        if url in indexable:
            if not pp.description:
                err(url, "missing meta description")
            else:
                descs[pp.description].append(url)
                if len(pp.description) > DESC_MAX:
                    err(url, f"description is {len(pp.description)} chars (max {DESC_MAX})")
            if not pp.canonical:
                err(url, "missing canonical")
            elif pp.canonical != origin + url:
                warn(url, f"canonical {pp.canonical} != {origin + url}")
            if not pp.jsonld:
                err(url, "no JSON-LD")
        if not pp.csp:
            err(url, "no Content-Security-Policy meta tag")
        for href, rel in pp.external:
            if host not in href and not {"noopener", "noreferrer"} <= set(rel):
                warn(url, f"external link without rel=\"noopener noreferrer\": {href}")
        if pp.h1 != 1:
            err(url, f"{pp.h1} <h1> elements (need exactly 1)")
        for i, block in enumerate(pp.jsonld, 1):
            try:
                json.loads(block)
            except json.JSONDecodeError as e:
                err(url, f"JSON-LD block {i} doesn't parse: {e}")
        raw = files[url].read_text(encoding="utf-8")
        n = len(NEEDS_SOURCE.findall(raw))
        if n:
            err(url, f"{n} [NEEDS SOURCE] marker(s) left")
        p = len(PLACEHOLDER.findall("".join(pp.text)))
        if p:
            warn(url, f"{p} [CONTENT] placeholder(s) to fill")
        if "—" in "".join(pp.text):
            warn(url, "em dash in visible text")
    for t, urls in titles.items():
        if len(urls) > 1:
            err(", ".join(urls), f"duplicate title {t!r}")
    for d, urls in descs.items():
        if len(urls) > 1:
            err(", ".join(urls), "duplicate meta description")

    # Sitemap coverage, both ways
    sm = root / "sitemap.xml"
    if not sm.exists():
        err("/sitemap.xml", "missing")
    else:
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        try:
            locs = [e.text.strip() for e in ET.parse(sm).getroot().findall("s:url/s:loc", ns)]
        except ET.ParseError as e:
            locs = []
            err("/sitemap.xml", f"doesn't parse: {e}")
        in_map = set()
        for loc in locs:
            path, _ = resolve(loc, "/", host)
            tf = target_file(path, root) if path else None
            if tf is None:
                err("/sitemap.xml", f"lists missing page {loc}")
                continue
            turl = file_to_url(tf, root)
            if turl in pages and pages[turl].noindex:
                err("/sitemap.xml", f"lists noindex page {loc}")
            if loc != origin + turl:
                warn("/sitemap.xml", f"{loc} is not the canonical form {origin + turl}")
            in_map.add(turl)
        for url in sorted(indexable - in_map):
            err(url, "not in sitemap.xml")
    if not (root / "robots.txt").exists():
        err("/robots.txt", "missing")

    print(f"Audited {len(pages)} pages ({len(indexable)} indexable) under {root}\n")
    if warnings:
        print(f"WARNINGS ({len(warnings)})")
        for w in warnings:
            print("  - " + w)
        print()
    if errors:
        print(f"ERRORS ({len(errors)})")
        for e in errors:
            print("  - " + e)
        print("\nFAIL")
        return 1
    print("PASS: 0 errors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
