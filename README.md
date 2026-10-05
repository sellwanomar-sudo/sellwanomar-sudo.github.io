# Content Authority Lab

Live site: **https://contentauthoritylab.com**

This is the portfolio and blog of Content Authority Lab, a bilingual SEO, AEO and GEO content team. It's hosted free on GitHub Pages.

**The golden rule:** every change you commit to the `main` branch goes live automatically within 1 to 2 minutes.
If you don't see a change, press **Ctrl+F5** on the site to skip your browser's cache.

**How the site is built:** you edit the files in `_src/`, run `python build.py`, then `python audit_site.py`, and commit.
`build.py` adds the shared header, footer, breadcrumbs, structured data (JSON-LD) and `sitemap.xml` to every page, so you never edit those by hand.
Both scripts use plain Python 3 with nothing to install.

```
_src/header.html, footer.html   Shared header and footer (edit once, every page updates)
_src/pages/                     One file per page. The folder path matches the URL
_src/pages/blog/_post-template.html   Blank post template (files starting with _ are not published)
build.py                        Builds the HTML pages and sitemap.xml from _src/
audit_site.py                   Checks links, titles, descriptions, H1s, schema and sitemap. Must say PASS before you publish
_planning/site-plan.md          Page inventory, linking matrix and parked pages
work/                           Case-study PDFs and cover images
assets/style.css, site.js       Design and behavior
```

The generated folders (`services/`, `industries/`, `work/<case>/`, `about/`, `contact/`, `blog/`) and `index.html` are build output. Don't edit them directly: your change would be overwritten on the next build.

## Edit a page
1. Open the page's file in `_src/pages/` (for example `_src/pages/services/aeo-geo.html`).
2. The JSON block at the top holds the title (max 60 characters), meta description (max 155) and page type. The HTML below it is the page body.
3. Replace each yellow `[CONTENT: ...]` box with your copy. The audit lists the ones still left.
4. FAQ: write each question as `<details><summary>Question?</summary><p>Answer.</p></details>` inside the `<div class="faq">`. It's published as FAQ structured data automatically.
5. Run `python build.py` and `python audit_site.py`, then commit.

## Add a blog post
1. Copy `_src/pages/blog/_post-template.html` to `_src/pages/blog/your-slug.html` and fill in every CAPITALIZED placeholder.
2. Add a card for it in `_src/pages/blog/index.html` (and optionally in `_src/pages/index.html`).
3. Run `python build.py` (it adds the post to `sitemap.xml`) and `python audit_site.py`, then commit.
4. In Google Search Console, use **URL Inspection → Request indexing**.

## Other everyday changes
- **Connect the contact form:** get a free key at https://web3forms.com using `team@contentauthoritylab.com`, then in `_src/pages/contact.html` replace `YOUR_WEB3FORMS_ACCESS_KEY` with it and rebuild.
- **Add a case study:** add the PDF and cover PNG to `work/`, copy a file in `_src/pages/work/`, then add its card to `_src/pages/work/index.html` and link it from the relevant service and industry pages.
- **Change colors:** edit the values at the top of `assets/style.css`.
- **Undo a mistake:** open the file, click **History**, open the previous version, copy it, and paste it back in.

## Get found on Google
1. In Google Search Console, add the URL-prefix property `https://contentauthoritylab.com/`.
   Choose **DNS** verification in Cloudflare (the HTML tag would need adding to `build.py`).
2. Submit `sitemap.xml`.
3. Add the site link to LinkedIn (Contact info and Featured), clippings.me and your CV.

## Your domain
`contentauthoritylab.com` is registered at Cloudflare and connected to this repository.
DNS (Cloudflare → DNS → Records) must stay as: four A records on `@` pointing to 185.199.108–111.153,
and a CNAME on `www` pointing to `sellwanomar-sudo.github.io`. All of them set to **DNS only**, never "Proxied".
The `CNAME` file in this repository holds the domain name: don't delete it.
The old `sellwanomar-sudo.github.io` address now redirects here automatically.

## Your email
`team@contentauthoritylab.com` is set up through Cloudflare Email Routing (free) and forwards to sellwan.omar@gmail.com.
Manage it in Cloudflare → Email Routing → Routing rules, where you can add more addresses such as `hello@` or `billing@`.
To send mail *from* that address, add it in Gmail under Settings → Accounts → "Send mail as", using an SMTP service such as Brevo.

## Voice and names
The HTML pages speak as "we". The About page names Selwan Omar as Founder and Lead Strategist, with Person structured data linked to the Organization (set in `build.py`). The PDFs in `work/` are unchanged.
