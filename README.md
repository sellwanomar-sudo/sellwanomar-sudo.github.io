# Content Authority Lab

Live site: **https://contentauthoritylab.com**, hosted free on GitHub Pages.

## How it works

```
content/          All page text, as JSON. Edited through the CMS (or by hand)
admin/            The CMS (Decap) at /admin/, and its settings in config.yml
cms-auth/         GitHub login helper for the CMS (a Cloudflare Worker)
build.py          Turns content/ into the website in _site/: menus, links, schema, sitemap
audit_site.py     Checks links, titles, descriptions, H1s, schema, sitemap and security tags
.github/workflows Builds, audits and publishes on every change to main
assets/, work/    Design files, case-study PDFs and images
_planning/        Site plan and design directions (not published)
```

1. You edit a page in the CMS and click **Save**. That creates a draft (a pull request).
2. GitHub builds and audits the draft automatically. A red X means the audit found a problem.
3. You click **Publish** in the CMS. GitHub builds again and the site updates in 1 to 2 minutes.

Nothing in `_site/` is stored in the repo. It's rebuilt from `content/` every time.

## Using the CMS
Go to **https://contentauthoritylab.com/admin/** and click **Login with GitHub**.

- **Services, Industries, Case studies, Blog posts:** one entry per page. Adding a service or industry adds it to the header and footer menus automatically.
- **Pages:** the homepage, About, Contact, and the intro text of the four hub pages.
- **Site settings:** email, links, the bottom call to action, the contact form key.
- Empty fields show on the site as yellow `[CONTENT: ...]` boxes until you fill them.
- Title tags are limited to 60 characters and descriptions to 155. The CMS won't let you save longer ones.
- Files you upload go into `work/`.

## Set up the CMS login (one time, about 15 minutes)
GitHub requires a small login helper for Decap. It runs free on your Cloudflare account.

**1. Create a GitHub OAuth App**
1. GitHub → your profile picture → **Settings → Developer settings → OAuth Apps → New OAuth App**.
2. Application name: `Content Authority Lab CMS`
3. Homepage URL: `https://contentauthoritylab.com`
4. Authorization callback URL: `https://cms-auth.contentauthoritylab.com/callback`
5. Click **Register application**, then **Generate a new client secret**. Keep the Client ID and the secret open in this tab.

**2. Create the Cloudflare Worker**
1. Cloudflare dashboard → **Workers & Pages → Create → Create Worker**. Name it `cms-auth`, then click **Deploy**.
2. Click **Edit code**, delete what's there, paste everything from `cms-auth/worker.js`, and click **Deploy**.
3. Go to **Settings → Variables and Secrets** and add:
   - `GITHUB_CLIENT_ID`: the Client ID (type: Text)
   - `GITHUB_CLIENT_SECRET`: the client secret (type: **Secret**)
4. **Settings → Domains & Routes → Add → Custom domain:** `cms-auth.contentauthoritylab.com`

**3. Test:** open `/admin/`, click **Login with GitHub**, and approve. You're in.

## Launch checklist (one time, when the content is ready)
1. Merge the `rebuild/flat-architecture` branch into `main`.
2. Repository → **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. Watch the **Actions** tab: the "Build, audit and deploy" run should go green.
4. In Google Search Console, submit `https://contentauthoritylab.com/sitemap.xml`.

## Working without the CMS
```
pip install -r requirements.txt
python build.py
python audit_site.py _site
python -m http.server -d _site 8000     # preview at http://localhost:8000
```
The CMS screen at `/admin/` only works on the live site (the CMS itself is added during deploy).

## Security in place
- A Content-Security-Policy on every page: scripts only from this site, the form posts only to Web3Forms, and no plugins or embedding of other sites' code.
- A strict referrer policy, and `noopener noreferrer` on external links.
- `/.well-known/security.txt` with a contact for security reports.
- The CMS is hidden from search engines (`noindex` and blocked in `robots.txt`). Only people with write access to this GitHub repo can log in.
- Every CMS change is a reviewed pull request, and nothing deploys unless the audit passes.
- The build workflow runs with read-only permissions. Only the deploy step can publish, and the CMS version is pinned.
- The login helper checks a one-time state value against forged logins and only hands the GitHub token to contentauthoritylab.com.

Not done yet (needs your decision): HTTPS enforcement, main-branch protection and Dependabot on GitHub, plus HSTS and anti-clickjacking headers through Cloudflare.

## Your domain
`contentauthoritylab.com` is registered at Cloudflare and connected to this repository.
DNS (Cloudflare → DNS → Records) must stay as: four A records on `@` pointing to 185.199.108–111.153,
a CNAME on `www` pointing to `sellwanomar-sudo.github.io`, all set to **DNS only**. Add the `cms-auth` Worker domain in step 2 above.
The `CNAME` file in this repository holds the domain name: don't delete it.

## Your email
`team@contentauthoritylab.com` is set up through Cloudflare Email Routing (free) and forwards to sellwan.omar@gmail.com.
To send mail *from* that address, add it in Gmail under Settings → Accounts → "Send mail as", using an SMTP service such as Brevo.
