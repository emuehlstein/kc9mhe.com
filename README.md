# kc9mhe.com

Personal amateur radio station page for **KC9MHE** (Eric Muehlstein), Chicago IL.

Static site, no build step. Served by GitHub Pages from `main`.

## Layout
- `index.html` — the whole site
- `style.css` — Chicago Offline palette (Signal Cyan / Beacon Amber / Mesh Green)
- `assets/qsl-chicago.jpg` — satellite QSL card image, carried over from the 2010 site
- `CNAME` — custom domain binding

## DNS
Route 53 hosted zone `Z0465455229IDAWWW1JXE`. Apex A records point at GitHub
Pages; `www` CNAMEs to `emuehlstein.github.io`. Mail (`MX` → `mail89.csoft.net`),
SPF and DMARC were carried over verbatim from the legacy csoft.net zone.

The pre-2026 site (last modified 2010-12-03) is archived in `legacy/`.
