// Cloudflare Workers entrypoint for the Static Assets site.
//
// The assets binding (with html_handling="none") serves .html files
// directly at their declared paths but does NOT auto-resolve directory
// URLs like "/" or "/elements/" to their index.html. This Worker fills
// that gap by handling the asset-miss fallback path: when a request
// ends in "/", rewrite to "<path>index.html" and re-fetch from the
// asset binding. Everything else is a real 404.

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname.endsWith("/")) {
      url.pathname += "index.html";
      return env.ASSETS.fetch(new Request(url.toString(), request));
    }
    return new Response("Not Found", { status: 404 });
  },
};
