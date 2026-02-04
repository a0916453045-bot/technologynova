export const onRequest: PagesFunction = async ({ request, next }) => {
  const url = new URL(request.url);

  // Redirect Cloudflare Pages default domain to the canonical custom domain.
  // This avoids duplicate-content across domains while keeping Pages.dev as a working fallback.
  if (url.hostname.endsWith('.pages.dev')) {
    url.hostname = 'insights.technologynova.org';
    return Response.redirect(url.toString(), 301);
  }

  return next();
};
