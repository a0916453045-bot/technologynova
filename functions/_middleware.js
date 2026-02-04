/**
 * Cloudflare Pages Functions middleware.
 * Redirect the Pages default domain (*.pages.dev) to the canonical custom domain.
 */
export async function onRequest({ request, next }) {
  const url = new URL(request.url);

  if (url.hostname.endsWith('.pages.dev')) {
    url.hostname = 'insights.technologynova.org';
    return Response.redirect(url.toString(), 301);
  }

  return next();
}
