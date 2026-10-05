/**
 * GitHub login helper for Decap CMS, as a Cloudflare Worker (free plan is enough).
 *
 * Decap opens  https://cms-auth.contentauthoritylab.com/auth  in a popup.
 * This sends the user to GitHub to approve, GitHub sends them back to /callback,
 * and the Worker hands the access token to the CMS window and closes the popup.
 *
 * Secrets to set in Cloudflare (Workers > this worker > Settings > Variables):
 *   GITHUB_CLIENT_ID      from your GitHub OAuth App
 *   GITHUB_CLIENT_SECRET  from your GitHub OAuth App (add as an encrypted secret)
 * Setup steps: README.md > "Set up the CMS login".
 */
const SITE_ORIGIN = "https://contentauthoritylab.com"; // the only page allowed to receive the token
const SCOPE = "public_repo"; // enough for a public repo; use "repo" if it ever goes private

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/auth") {
      const state = crypto.randomUUID();
      const authorize = new URL("https://github.com/login/oauth/authorize");
      authorize.searchParams.set("client_id", env.GITHUB_CLIENT_ID);
      authorize.searchParams.set("redirect_uri", `${url.origin}/callback`);
      authorize.searchParams.set("scope", SCOPE);
      authorize.searchParams.set("state", state);
      return new Response(null, {
        status: 302,
        headers: {
          Location: authorize.toString(),
          "Set-Cookie": `decap_state=${state}; Path=/; Max-Age=600; HttpOnly; Secure; SameSite=Lax`,
        },
      });
    }

    if (url.pathname === "/callback") {
      const cookie = request.headers.get("Cookie") || "";
      const expected = (cookie.match(/(?:^|;\s*)decap_state=([^;]+)/) || [])[1];
      const state = url.searchParams.get("state");
      const code = url.searchParams.get("code");
      if (!code || !state || state !== expected) {
        return page("error", { message: "Login check failed. Close this window and try again." });
      }
      const res = await fetch("https://github.com/login/oauth/access_token", {
        method: "POST",
        headers: { Accept: "application/json", "Content-Type": "application/json", "User-Agent": "decap-cms-auth" },
        body: JSON.stringify({
          client_id: env.GITHUB_CLIENT_ID,
          client_secret: env.GITHUB_CLIENT_SECRET,
          code,
          redirect_uri: `${url.origin}/callback`,
        }),
      });
      const data = await res.json();
      if (!data.access_token) {
        return page("error", { message: data.error_description || "GitHub did not return a token." });
      }
      return page("success", { token: data.access_token, provider: "github" });
    }

    return new Response("Not found", { status: 404 });
  },
};

// Decap's popup handshake: say "authorizing", wait for the CMS window to answer,
// then send the result only to the site's own origin.
function page(status, content) {
  const message = `authorization:github:${status}:${JSON.stringify(content)}`;
  const html = `<!doctype html><html><body><p>Finishing login...</p><script>
  (function () {
    var origin = ${JSON.stringify(SITE_ORIGIN)};
    function receive(e) {
      if (e.origin !== origin) return;
      window.opener.postMessage(${JSON.stringify(message)}, origin);
      window.removeEventListener("message", receive);
      setTimeout(function () { window.close(); }, 300);
    }
    window.addEventListener("message", receive);
    window.opener.postMessage("authorizing:github", origin);
  })();
  </script></body></html>`;
  return new Response(html, {
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "no-store",
      "Referrer-Policy": "no-referrer",
      "Set-Cookie": "decap_state=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax",
    },
  });
}
