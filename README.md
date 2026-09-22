# Content Authority Lab

Live site: **https://contentauthoritylab.com**

This is the portfolio and blog of Content Authority Lab, a bilingual SEO, AEO and GEO content team. It's hosted free on GitHub Pages.
You can do everything below in your browser on github.com, with nothing to install.

**The golden rule:** every change you save ("commit") on GitHub goes live automatically within 1–2 minutes.
If you don't see a change, press **Ctrl+F5** on the site to skip your browser's cache.

```
index.html                 Home page (hero, services, work, about, blog preview, contact form)
blog/index.html            Blog list page
blog/<post>.html           One file per blog post
blog/_post-template.html   Blank post template (not published)
work/                      Case-study PDFs and cover images
assets/style.css           Design and colours
sitemap.xml                List of pages for Google
```

---

## ✏️ Edit an existing blog post
1. Open https://github.com/sellwanomar-sudo/sellwanomar-sudo.github.io/tree/main/blog
2. Click the post file, e.g. `seo-aeo-geo-explained.html`.
3. Click the **pencil icon ✏️** (top right of the file).
4. Change the text. Article text sits between `<article class="article">` and `</article>`.
5. Click **Commit changes…** and then **Commit changes** again.
6. If you changed the title or summary, update the matching card in `blog/index.html` (and in `index.html` if it's shown on the home page).

## ➕ Add (publish) a new blog post
**1. Create the post file**
1. Open the template: https://github.com/sellwanomar-sudo/sellwanomar-sudo.github.io/blob/main/blog/_post-template.html
2. Click the **Copy raw file** icon (two overlapping squares, top right of the file).
3. Go to the `blog` folder and click **Add file → Create new file**.
4. Name it with a short, keyword-rich slug ending in `.html`, e.g. `arabic-seo-tips.html` (lowercase, with hyphens and no spaces).
5. Paste with Ctrl+V, then replace every CAPITALISED placeholder:

   | Placeholder | Replace with |
   |---|---|
   | `POST TITLE` (4 places) | Your headline |
   | `ONE-SENTENCE SUMMARY` (2 places) | Your meta description (140–160 characters) |
   | `POST-SLUG` (2 places) | Your file name without `.html`, e.g. `arabic-seo-tips` |
   | `YYYY-MM-DD` (2 places) | Today's date, e.g. `2026-10-05` |
   | `CATEGORY · CATEGORY` | e.g. `SEO · Localization` |
   | `DD Month YYYY · X min read` | e.g. `5 October 2026 · 7 min read` |

6. Write your article inside `<article class="article">`. Use this formatting cheat sheet:

   | You want | Type |
   |---|---|
   | Paragraph | `<p>Text</p>` |
   | Section heading | `<h2>Heading</h2>` |
   | Sub-heading | `<h3>Heading</h3>` |
   | **Bold** | `<strong>text</strong>` |
   | Link | `<a href="https://…">link text</a>` |
   | Bullet list | `<ul><li>One</li><li>Two</li></ul>` |
   | Numbered list | `<ol><li>One</li><li>Two</li></ol>` |
   | Quote | `<blockquote>Quote</blockquote>` |
   | Image | `<img src="../work/image-name.png" alt="Describe the image">` |

   **Shortcut:** write the post in Word or Google Docs, then paste it into Claude and ask:
   *"Convert this into my Content Authority Lab blog template, with slug X."*
   Claude will return the whole file ready to paste in.

7. Click **Commit changes**.

**2. Add it to the blog list**
1. Open `blog/index.html` and click ✏️.
2. Find the comment `NEW POSTS GO HERE`. Directly below it, paste this (newest post at the top):
   ```html
   <a class="post-card" href="arabic-seo-tips.html">
     <span class="meta">5 Oct 2026 · 7 min read</span>
     <h3>Your post title</h3>
     <p>One-sentence summary.</p>
     <span class="more">Read article →</span>
   </a>
   ```
3. Commit.

**3. (Optional) Feature it on the home page**
In `index.html`, find `From the blog`. Paste the same card there, with the link changed to `blog/arabic-seo-tips.html`.
Keep 2–3 cards and delete the oldest, or the `More articles coming soon` box.

**4. Tell Google**
In `sitemap.xml`, add this line above `</urlset>` and commit:
```xml
<url><loc>https://contentauthoritylab.com/blog/arabic-seo-tips.html</loc><lastmod>2026-10-05</lastmod></url>
```
Then in Google Search Console, use **URL Inspection → Request indexing** for the new URL.

## 🗑️ Remove a blog post
1. Open the post file in `blog/`, click the **⋯** menu (top right), choose **Delete file**, then commit.
2. Remove its card from `blog/index.html`, and from `index.html` if it's featured there.
3. Remove its line from `sitemap.xml`.

To hide a post without deleting it, rename the file so it starts with `_` (e.g. `_arabic-seo-tips.html`) and remove its cards.

---

## Other everyday changes
- **Connect the contact form:** get a free key at https://web3forms.com using `team@contentauthoritylab.com`, then open `index.html`, find `YOUR_WEB3FORMS_ACCESS_KEY` and replace it with your key.
- **Add a work sample:** in `work/`, use **Add file → Upload files** to add the PDF and a cover image. Then in `index.html`, copy one `<article class="work">` block and edit it. Set `data-cat` to `seo`, `web` or `social` so the filters work.
- **Remove a work sample:** delete its `<article class="work">…</article>` block in `index.html`.
- **Change text on the home page:** edit `index.html` with ✏️. Use **Ctrl+F** in the editor to find the sentence.
- **Change colours:** edit the values at the top of `assets/style.css`.
- **Undo a mistake:** open the file, click **History**, open the previous version, copy it, and paste it back in.

## Get found on Google
1. In Google Search Console, add the URL-prefix property `https://contentauthoritylab.com/`.
   Choose **HTML tag** verification and paste the tag just below `<head>` in `index.html`.
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

## Adding your name later
The site currently speaks as a team and shows no personal name. When you want to add yourself and your colleagues,
edit the About section of `index.html`, and change the author box and byline in the blog posts.
