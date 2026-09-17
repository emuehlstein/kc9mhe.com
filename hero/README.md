# kc9mhe.com hero image

`build-hero.py` regenerates `assets/hero-chicago.{webp,jpg}` + `@2x.webp`.

## Source: a purpose-built high-res service

Use tileserver service **`summerdale-lidar-dark-9x`**
(`Summerdale LiDAR Hillshade Dark 9x`), z15-20, bounds
`-87.71,41.95 -> -87.65,42.00`, 9x vertical exaggeration. It covers Eric's blocks
at building-level detail. There is also a `-light-9x` twin, plus
`avenues-*-9x-z17-18` and `summit-park-*-9x-z17-18` for other areas.

Discover with `GET https://tiles.chicagooffline.com/services` then
`GET /services/<id>` for TileJSON (bounds, minzoom/maxzoom).

**There is NO satellite/ortho imagery on the tileserver** - all 47 services are
hillshade/elevation. Don't go looking for one.

## Why z17 oversampled

The county DTM `cook-atak-dark-z10-16` tops out ~z16 and the north side is
topographically FLAT, so it renders as dull murk. Fetch z17 from the Summerdale
service at the full 2.743:1 hero aspect, then Lanczos-downscale to 1920x700
(~2.4x oversample) for sharp, real structure.

## Framing constraints, learned the hard way

- A 2.743:1 hero **cannot** hold both Summerdale (41.9785) and the Loop
  (41.8827). Capping latitude to fit both forces a ~0.97 deg / 80 km longitude
  span, which drags in the whole metro and the Cook County coverage edge.
  Chicago runs north-south along the lake, so a wide hero gets a BAND.
- Ground resolution, not zoom, is the real constraint: 0.096 deg of latitude in
  700 px is ~15 m/px regardless of source zoom.
- At this latitude the lake renders **lighter** than land and its coverage
  polygon is a blatant rectangular staircase. Push it out of frame.
- Marker sits at `QTH_FRAC_Y = 0.36` and horizontally **centred**: `.hero-bg`
  uses `object-fit: cover`, which crops width hard on narrow viewports, and
  centre survives that crop. The text block occupies the bottom ~40%.
- Size marker elements in FINAL pixels and multiply by `S = SRC_W/WF`. Sizing in
  source px makes the marker a tiny speck after downscale.
- `rsvg-convert` renders colour emoji as a BLACK blob - the house is a
  hand-authored SVG path, not an emoji glyph.
- Services are TileJSON `"type": "overlay"` = transparent. Flatten onto ink
  (`-background '#050a10' -alpha remove -alpha off`) or it composites to white.

## Verifying against the real page

Browser navigation to localhost is blocked by policy. Instead composite the
actual CSS scrim + text in PIL and inspect that (see session log 2026-09-17).
`.hero-scrim` was retuned for this image: the old `.6` top / `.35` mid stops were
sized for a bright satellite photo and crushed the hillshade flat.
