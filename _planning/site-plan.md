# Content Authority Lab: page inventory and linking matrix

Step 1 of the rebuild. Nothing in the site has been written yet. Sources read: `index.html` (byte-identical to the live homepage on 5 Oct 2026), `blog/`, the 7 PDFs in `work/`, and the ISA Bullion and iGaming PNGs.

## 1. Page inventory (25 pages)

| # | URL | Role | Primary query | Evidence it rests on |
|---|---|---|---|---|
| H | `/` | Hub | content authority lab; bilingual SEO content agency | All of the below |
| S0 | `/services/` | Hub | content services | Needed for breadcrumbs and the dropdown's "All services" link |
| S1 | `/services/seo-content-writing/` | Service | SEO content writing services | Vervo, Khan El Kaser, ISA Bullion. Folds in **on-page optimization** (Hayaty naming and slugs, Khan El Kaser H-structure, Beesline meta descriptions) |
| S2 | `/services/aeo-geo/` | Service | AEO and GEO services; AI search optimization | Khan El Kaser: 9.7% AI Overviews share, 14 AI mentions, 6 cited pages. Vervo: snippet and H2 sitelinks |
| S3 | `/services/content-audits/` | Service | content audit services | Folds in **performance tracking** (ISA's 44 months of daily reporting, the Vervo LinkedIn export analysis, Vervo's volume cut). **Weakest proof: see N4** |
| S4 | `/services/technical-content-writing/` | Service | technical content writing | Vervo reefer guide (2 laws, 13-row landed cost table), ISA bullion, Hayaty and Beesline INCI work |
| S5 | `/services/website-copywriting/` | Service | website copywriting; product page copy | Beesline (139 pages, EN+AR), Hayaty (9 pages), Vervo's commercial pages on page one |
| S6 | `/services/social-media-content/` | Service | social media content services | Vervo LinkedIn, Hayaty social, social portfolio |
| I0 | `/industries/` | Hub | — | Breadcrumbs and dropdown |
| I1 | `/industries/logistics-content/` | Industry | logistics content writing | Vervo SEO, Vervo LinkedIn |
| I2 | `/industries/igaming-content/` | Industry | iGaming content writing | Casino review; Revbay 2022-2026 (homepage text only, no figures) |
| I3 | `/industries/b2b-content/` | Industry | B2B content writing | Vervo LinkedIn (B2B audience data), Vervo SEO, ISA Bullion (see Q4) |
| I4 | `/industries/ecommerce-content/` | Industry | ecommerce content writing | Khan El Kaser, Beesline, Hayaty, social portfolio |
| W0 | `/work/` | Hub | content writing case studies | Grid filterable by service and industry |
| W1 | `/work/vervo-middle-east-seo/` | Work | — | `vervo-logistics-seo.pdf` |
| W2 | `/work/khan-el-kaser-seo/` | Work | — | `khan-el-kaser-seo.pdf` |
| W3 | `/work/isa-bullion-seo/` | Work | — | `isa-bullion-seo.png` + homepage card (no PDF) |
| W4 | `/work/igaming-content-case-study/` | Work | — | `igaming-casino-review.png` + homepage card (no PDF) |
| W5 | `/work/beesline-product-copy/` | Work | — | `beesline-product-content.pdf` |
| W6 | `/work/hayaty-natural-seo/` | Work | — | `hayaty-natural-web-content.pdf` + `hayaty-natural-social.pdf` (social is its own section; both PDFs offered as downloads) |
| W7 | `/work/vervo-linkedin/` | Work | — | `vervo-linkedin.pdf`. **Kept as its own page:** 21,985 impressions, 5.42% engagement against a 5.20% benchmark, 1,081 new followers, 2.18% CTR, audience demographics and a theme analysis. Enough for a full page |
| W8 | `/work/social-media-portfolio/` | Work | — | `social-operations.pdf` |
| A | `/about/` | Entity | — | Homepage About section + PDFs' method and AI statements |
| B0 | `/blog/` | Hub | — | Existing |
| B1 | `/blog/seo-aeo-geo-explained.html` | Blog | SEO vs AEO vs GEO | Existing article. **URL kept as is:** it's live and indexed, and GitHub Pages can't do 301 redirects |
| C | `/contact/` | Entity | contact | Existing form + email |
| — | `/404.html` | Utility | — | noindex, not in sitemap |

Case studies have no primary query of their own. Their job is to prove the service and industry pages, and to be cited.

### Not yet (parked, with the evidence that unlocks each one)

| Parked page | Unlocks when |
|---|---|
| `/services/on-page-optimization/`, `/services/performance-tracking/` | Never as separate pages unless Search Console shows impressions that S1 and S3 can't satisfy |
| Arabic, English, or city/country service variants | Search Console impressions for the variant query (e.g. "seo content writing dubai") with S1 ranking poorly for it |
| `/industries/skincare-content/` | Ecommerce page ranks for skincare queries it can't hold. Three skincare clients already exist, so this is the likeliest first split |
| `/industries/finance-content/` (precious metals, regulated) | A second finance client, or ISA Bullion data with sources and dates |
| `/industries/education-content/` | More than one education client (only Al-Hayat School today) |
| Revbay (iGaming SEO, Malta, 2022-2026) case study | Any figures or a PDF for that work |

## 2. URL map and navigation

```
/                                    home
├── services/                        hub
│   ├── seo-content-writing/  aeo-geo/  content-audits/
│   └── technical-content-writing/  website-copywriting/  social-media-content/
├── industries/                      hub
│   └── logistics-content/  igaming-content/  b2b-content/  ecommerce-content/
├── work/                            hub (filters: service, industry)
│   └── 8 case studies; PDFs stay in /work/*.pdf as downloads
├── about/   blog/   contact/
```

Header on every page: **Services** (dropdown: 6 + "All services") · **Work** · **Industries** (dropdown: 4 + "All industries") · **About** · **Blog** · **[Start a project]** → `/contact/`.
Footer: all 6 services, all 4 industries, Work, About, Blog, Contact, email, LinkedIn, service area (UAE, KSA, Egypt, Lebanon, UK), "Based in Cairo".

Click depth: every service and industry page is 1 click from home (via the header). Every case study is 1 click (featured on home) or 2 (home → `/work/` → case study). The article is 2 clicks (home → `/blog/` → article, plus 1 click from the home insights section).

## 3. Internal linking matrix

The header and footer links above appear on every page and aren't repeated below. This table is the **in-content** links only. Each target URL has its own anchor text: no anchor is reused for two URLs.

### Home

| Target | Anchor | Placement |
|---|---|---|
| S1-S6 | "Explore SEO content writing →", "Explore AEO & GEO →", "Explore content audits →", "Explore technical writing →", "Explore website copywriting →", "Explore social media content →" | Service cards |
| I1-I4 | "Logistics & freight", "iGaming", "B2B", "Ecommerce & skincare" | Industries strip |
| W1, W2, W3, W5 | Client name + one headline result | Selected work (4 cards) |
| W0 | "See all case studies" | Under selected work |
| B1 | Article title | Insights |
| A | "How we work" | Why CAL |
| C | "Start a project" | Hero + final CTA |

### Services → industries, case studies, blog

| Source | Industries (section: "Industries we do this for") | Case studies (in the proof section, next to the claim they back) | Blog |
|---|---|---|---|
| S1 SEO content writing | I1, I2, I3, I4 | W1 "5 #1 positions in UAE Google", W2 "#1 for a hair-care pillar in eight weeks", W3 "four queries on page one, in two languages", W6 "naming and slug decisions" (on-page section) | B1 |
| S2 AEO & GEO | I4, I1, I3 | W2 "9.7% of search presence in AI Overviews", W1 "snippet lifted from our copy" | B1 (primary) |
| S3 Content audits | I1, I3, I4 | W1 "cut volume 86%, raised depth fivefold", W7 "127 posts re-weighted by result", W3 "44 months of daily reporting" | — |
| S4 Technical writing | I1, I3, I4, I2 | W1 "a 6,000-word cold chain guide citing two UAE laws", W3 "bullion in a regulated niche", W6 "INCI-level botanical reference", W5 "INCI carried into Arabic" | — |
| S5 Website copywriting | I4, I1, I2 | W5 "139 product pages at full EN/AR parity", W6 "a nine-page trust layer", W1 "four commercial pages on page one", W4 "a review that publishes findings against the product" | — |
| S6 Social media content | I1, I3, I4 | W7 "5.42% engagement, zero paid", W8 "five accounts, 415K audience", W6 "two accounts from zero" (social section) | — |

### Industries → services and case studies

| Source | Services (2-4, in "What we do for X") | Case studies |
|---|---|---|
| I1 Logistics | S1, S4, S6, S2 | W1, W7 |
| I2 iGaming | S1, S5, S4 | W4 |
| I3 B2B | S1, S4, S6, S3 | W7, W1, W3 |
| I4 Ecommerce | S5, S1, S2, S6 | W2, W5, W6, W8 |

### Case studies → services, industry, next case study

| Source | "Services used" box | Industry | Related / next |
|---|---|---|---|
| W1 Vervo SEO | S1, S2, S4, S5 | I1, I3 | W7 (same client, LinkedIn side) |
| W2 Khan El Kaser | S1, S2 | I4 | W8 (same brand's social) |
| W3 ISA Bullion | S1, S4 | I3 (see Q4) | W1 |
| W4 iGaming review | S1, S5 | I2 | W3 |
| W5 Beesline | S5, S4 | I4 | W8 (same brand's social) |
| W6 Hayaty | S5, S4, S6, S1 | I4 | W2 |
| W7 Vervo LinkedIn | S6, S3 | I1, I3 | W1 |
| W8 Social portfolio | S6 | I4 | W2, W5 |

### Hubs, blog, entity pages

| Source | Links |
|---|---|
| S0 `/services/` | S1-S6, plus one proof link each |
| I0 `/industries/` | I1-I4 |
| W0 `/work/` | W1-W8 |
| B0 `/blog/` | B1 |
| B1 article | S2 (primary, in the "do you need all three" section), W2 (case study) |
| A About | S0, W0, C |
| C Contact | — (header and footer only) |

Inbound check: every service, industry and case study page gets at least 3 in-content links on top of the header and footer.

## 4. Missing sources (will show as visible `[NEEDS SOURCE: …]` markers until resolved)

| # | Where | What's missing |
|---|---|---|
| N1 | Home proof strip, About, W1 | **"17K+ monthly users at Vervo"** and "from a few hundred users a month". The Vervo PDF has no traffic figure at all. Needs a GA4 or Search Console screenshot with a date |
| N2 | W3 ISA Bullion | Data source and date for 3.2K visits / 77% UAE / 87% on price pages / 533 linking sites (DR 27 suggests Ahrefs). The 4 target queries and their positions (only "best #3" is given). Which 4 banks are outranked. Engagement dates and scope. What the 44 months of daily reporting covered |
| N3 | W4 iGaming | No performance data, which is by design (the PNG says the domain recently migrated). What the 8 tests, 7 criteria and 6 findings were, beyond the counts. Revbay: any figure at all |
| N4 | S3 Content audits | No audit deliverable is documented in any PDF. The page can rest on the documented decisions (Vervo's volume cut, the LinkedIn theme re-weighting, ISA reporting), but a real audit sample or a before/after would make it much stronger |
| N5 | Home proof strip | **"10+ industries served"**: only about 6 can be evidenced (logistics, skincare/ecommerce, precious metals, iGaming, education, B2B). I suggest dropping it rather than marking it |
| N6 | W1, W7 | **Vervo's CMS contradicts itself:** the SEO PDF says Joomla, the LinkedIn PDF says "the WordPress front end". Which is it? |
| N7 | Contact | The Web3Forms access key is still the placeholder, so the current form doesn't send. Not a copy marker, but the form is broken until it's set |

Figures I'll use as-is because they're on the current site: "6+ years in content", Revbay 2022-2026, the MA from the University of Hamburg, Cairo base, languages, and the service area.

## 5. Questions before I write copy

- **Q1. Front-end evidence per case study.** The PDFs document front-end or build work only for Vervo ("pages I wrote and built", "maintain the front end"). For Khan El Kaser (locale and sitemap structure), Hayaty (slugs, taxonomy) and Beesline (meta), they show on-page structure decisions, not builds. ISA, iGaming and the social pages have nothing. Should I limit each case study's front-end section to what's documented and mark the rest `[NEEDS SOURCE]`? Or did you build more than the PDFs say?
- **Q2. Voice and name.** The PDFs are first person and signed "Selwan Omar". The site speaks as a nameless team. Should the HTML case studies use "we" while the PDF downloads stay as they are, with your name? And should About name you as the lead (good for E-E-A-T and Person schema) or stay nameless?
- **Q3. Naming the iGaming site.** The review was ghostwritten, and the PNG shows the live URLs on ar.online-casinos.net. Should I link to the live review, name the domain without linking, or keep it anonymous ("an Arabic-English casino affiliate")?
- **Q4. ISA Bullion's industry home.** It's a DMCC-licensed bullion dealer, not obviously B2B. Should I link it from B2B as a "regulated sector" proof, or leave it attached only to the services until a finance page exists?

## 6. Build notes

- Fonts change from Manrope to Montserrat with an Arial fallback.
- Add a `_config.yml` that excludes `README.md`, `audit_site.py`, `build.py` and `_planning/` from publishing. Without it, GitHub Pages' Jekyll renders `README.md` as a public page. No `.nojekyll`, so underscore folders stay private.
- Templates live in `_src/`. `build.py` stamps the shared header, footer and JSON-LD into each page and writes the published HTML.
- Homepage meta description is 183 chars and the article title is 65 chars today. Both get fixed. Baseline audit of the current site: 3 errors.
