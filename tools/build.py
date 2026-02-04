#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SITE = json.loads((DATA / "site.json").read_text(encoding="utf-8"))
POSTS = json.loads((DATA / "posts.json").read_text(encoding="utf-8"))

base_url = SITE["base_url"].rstrip("/") + "/"
site_name = SITE.get("site_name", "TechNova 中文摘要索引")

# latest first
posts_sorted = sorted(POSTS, key=lambda x: (x.get("date", ""), x.get("id", "")), reverse=True)

# index.html
items_html = []
def short_label(url: str) -> str:
    if not url:
        return ""
    # Prefer a short, readable label for very long URLs.
    if "technologynova.org" in url:
        return "technologynova.org/…"
    if len(url) <= 60:
        return url
    return url[:57] + "…"

for p in posts_sorted:
    pid = p["id"]
    purl = f"p/{pid}/"
    date = p.get("date", "")
    title = p.get("title", "")
    original = p.get("original_url", "")
    landing = p.get("landing_url", "")
    tags = p.get("tags", [])
    tags_html = " ".join([f"<span class=\"badge\">{t}</span>" for t in tags[:8]])
    items_html.append(
        f"""
        <div class=\"card\">
          <div class=\"meta\">{date} · <span class=\"badge\">{pid}</span></div>
          <h2 style=\"margin:6px 0 6px\"><a href=\"{purl}\">{title}</a></h2>
          <div class=\"meta\">原文：<a href=\"{original}\" title=\"{original}\">{short_label(original)}</a></div>
          <div class=\"meta\">承接页：<a href=\"{landing}\" title=\"{landing}\">{short_label(landing)}</a></div>
          <div style=\"margin-top:10px\">{tags_html}</div>
        </div>
        """
    )

now = datetime.now().strftime("%Y-%m-%d %H:%M")
index_html = f"""<!doctype html>
<html lang=\"zh-Hans\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
  <title>{site_name}</title>
  <meta name=\"description\" content=\"TechNova 技术文章的中文摘要索引（每日更新），并回链到 TechNova 原文与产品/解决方案承接页。\" />
  <link rel=\"stylesheet\" href=\"assets/style.css\" />
</head>
<body>
  <div class=\"container\">
    <header>
      <h1 class=\"brand\">{site_name}</h1>
      <p class=\"sub\">目标：长期留存、可索引、每日新增中文摘要页，并回链到 TechNova 原文与承接页。</p>
      <p class=\"sub\">TechNova 官网：<a href=\"{SITE.get('home_url','https://technologynova.org/')}\">{SITE.get('home_url','https://technologynova.org/')}</a></p>
      <p class=\"sub\"><span class=\"badge\">Last update: {now}</span></p>
    </header>

    {''.join(items_html) if items_html else '<p>暂无内容。</p>'}

    <div class=\"footer\">
      <div>说明：本索引页为中文摘要与观点整理，非原文全文；原文版权归 TechNova 所有。</div>
      <div>如需系统建设与交付支持：<a href=\"https://technologynova.org/solution/\">https://technologynova.org/solution/</a></div>
    </div>
  </div>
</body>
</html>
"""

(ROOT / "index.html").write_text(index_html, encoding="utf-8")

# robots.txt
robots = f"""User-agent: *
Allow: /
Sitemap: {base_url}sitemap.xml
"""
(ROOT / "robots.txt").write_text(robots, encoding="utf-8")

# sitemap.xml (with lastmod)
url_rows = [(base_url, datetime.now().strftime("%Y-%m-%d"))]
for p in POSTS:
    pid = p["id"]
    lastmod = p.get("date") or datetime.now().strftime("%Y-%m-%d")
    url_rows.append((f"{base_url}p/{pid}/", lastmod))

# stable + unique
seen = set()
entries = []
for u, lm in sorted(url_rows, key=lambda x: x[0]):
    if u in seen:
        continue
    seen.add(u)
    entries.append(f"  <url><loc>{u}</loc><lastmod>{lm}</lastmod></url>")

sitemap = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">
""" + "\n".join(entries) + "\n</urlset>\n"
(ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")

# feed.xml (RSS)
items = []
for p in posts_sorted[:50]:
    pid = p["id"]
    title = p.get("title", "")
    link = f"{base_url}p/{pid}/"
    pub_date = p.get("date", "")
    # RFC 2822-ish; keep simple (00:00 GMT)
    pub_rfc = f"{pub_date} 00:00:00 GMT" if pub_date else ""
    items.append(
        f"<item><title><![CDATA[{title}]]></title><link>{link}</link><guid>{link}</guid>" +
        (f"<pubDate>{pub_rfc}</pubDate>" if pub_rfc else "") +
        f"<description><![CDATA[中文摘要页（回链 TechNova 原文）。]]></description></item>"
    )

feed = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<rss version=\"2.0\">
<channel>
  <title><![CDATA[{site_name}]]></title>
  <link>{base_url}</link>
  <description><![CDATA[TechNova 文章的中文摘要索引（每日更新）。]]></description>
  <language>zh-Hans</language>
  {''.join(items)}
</channel>
</rss>
"""
(ROOT / "feed.xml").write_text(feed, encoding="utf-8")

# touch updated_at
SITE["updated_at"] = datetime.now().strftime("%Y-%m-%d")
(DATA / "site.json").write_text(json.dumps(SITE, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(f"Built index.html + sitemap.xml (posts={len(POSTS)})")
