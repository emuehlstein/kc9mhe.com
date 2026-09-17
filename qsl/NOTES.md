# QSL card — KC9MHE (2026 rebuild)

## Spec held constant across variants
- Canvas **1650 × 1050 px** = 5.5 × 3.5 in @ 300 dpi (standard QSL card, landscape)
- Safe margin 90px
- Palette (Chicago Offline system):
  - bg `#05080a`, land `#0b1216`, lake `#06202b`
  - grid `#13303a`
  - Signal Cyan `#00E5FF`, Beacon Amber `#FFB300`, Mesh Green `#39FF14`
  - text `#e8eef2`, dim `#7d8c96`
- Callsign in **mono** to echo the site hero (site uses ui-monospace for `<h1>`)
- Geography: Lake Michigan right ~30%, shoreline running NNE, street grid on land

## Shoreline path (shared, do not drift)
```
M 0 0 L 1120 0
C 1135 160 1105 300 1150 420
C 1185 540 1165 700 1210 860
C 1225 950 1215 1000 1230 1050
```

## Variant axis: map/mesh detail density
- **v1 minimal** — shoreline as a single cyan rule, no grid, no lake fill, nodes only
- **v2 mid** — street grid, subtle lake fill, mesh nodes + links
- **v3 dense** — v2 + Chicago diagonals + stronger lake + range rings on the home node

## Gotchas
- `view_image` rejects `/tmp` — author inside the workspace (this dir).
- `rsvg-convert` has no webfonts; Menlo/Helvetica resolve locally so preview ≈ final.
- Outline the text before shipping if the card is ever handed off as a standalone file.

## Outcome
(filled in after review)

## REAL-MAP DIRECTION (v4) — replaces hand-drawn v1-v3
v1-v3 rejected: hand-drawn shoreline unrecognizable, land/lake contrast too weak,
generic. Font stack `"Menlo, 'Courier New', monospace"` FELL BACK to sans in
rsvg-convert — **specify a single family** (`font-family="Menlo"`), fontconfig
resolves Menlo/Courier New/Andale Mono/Helvetica Neue fine.

### Chicago Offline tileserver (tiles.chicagooffline.com)
- Service list: `GET /services` (47 services, JSON)
- Tile URL: `/services/<name>/tiles/{z}/{x}/{y}.png`  ← note the `/tiles/` segment
- Metadata: `GET /services/<name>` (tilejson: bounds, minzoom, maxzoom)
- **USE `cook-atak-dark-z10-16`** — Cook County DTM/LiDAR hillshade, z10-16,
  bounds [-88.5938,41.2448,-87.1875,42.2936]. Deep navy, shows street grid,
  Chicago River, rail yards, building masses. Reads unmistakably as Chicago.
- `cook-3dep-dark-v2` also good (more texture). **`cook-lidar-dark-v2` is DEAD** (116b responses).
- No tileserver-gl static API; `/styles/...` and `/data/v3.json` are 404.

### Build
`mosaic.py` fetches z13 tiles (center -87.72, 41.86), assembles 3300x2100
`chicago-base.png` (2x the 1650x1050 card). Tiles cached in `tiles/`.

### Mosaic run result (2026-09-16)
- z13, tiles x[2093..2106] y[3041..3049] = 14x9 = 126; **117/126 fetched**
  (9 misses are lake/out-of-bounds tiles -> filled `xc:#0e1a2b`). Cached in `tiles/`.
- `chicago-base.png` = 3300x2100, ~7.6MB. Re-running is cheap (cache hits).

### NEXT STEPS (resume here)
1. Review `base-preview.png` — confirm lakefront + grid read well; adjust CLON/CLAT
   or Z in `mosaic.py` if framing is off.
2. Build `front-v4.svg`: `chicago-base.png` as `<image>` base, duotone/darken toward
   `#05080a`, bottom fade for legibility, then typography:
   - eyebrow `AMATEUR RADIO STATION` cyan #00E5FF, mono, ls 11, at (90,150)
   - `KC9MHE` mono bold ~215px at (86,855), fill #e8eef2  <-- single font-family only
   - cyan rule y=900, `Eric Muehlstein` sans 40 at (92,955)
   - `CHICAGO, ILLINOIS · GRID EN61DT` mono 28 dim #7d8c96 at (92,1002)
     (historical note — draft used the wrong grid square; corrected to
     EN61DX for 2101 W Summerdale, see kc9mhe/STATE.md 2026-09-16)
   - `CHICAGOOFFLINE.COM` amber #FFB300 mono 26, right-aligned at (1560,1002)
   - optional amber home-node dot + range rings over the real map
3. Also build a **back** (QSO fields): TO RADIO / DATE / UTC / FREQ / MODE / RST /
   2-WAY / PWR / ANT / REMARKS, "CONFIRMING QSO WITH ___", PSE/TNX QSL.
4. Render 1650x1050 PNG (5.5x3.5in @300dpi), review, then ship to
   `~/src/kc9mhe.com/assets/` and swap the Contact `<figure>` in index.html
   (currently `assets/qsl-card-original.jpg`, caption "The QSL card, unchanged
   since 2010. Some things hold up." -> needs new caption), commit + push.

### Site state (already deployed, HEAD 2e85d83)
kc9mhe.com live on GH Pages + Route53, TLS on, https_enforced. Eric's 4 tweaks
(MeshCore link-only, "Reverse Engineering & CPS", GMRS 550/DPL023 repeater,
"Packet, APRS & AREDN", projects reordered w/ ssrf-lite +
chioff-codeplugger-profiles-shared, meshcore-health-check dropped) ALL DONE+PUSHED.
Email stays QRZ-only per Eric.

### base-preview.png REVIEW (2026-09-16) — framing needs a fix before v4
GOOD: lakefront/shoreline is crisp and unmistakable; street grid, Chicago River,
the Stevenson/rail diagonal, O'Hare-ish rail yards top-left all read beautifully.
Deep navy #1e2a44-ish with pale blue relief. This direction is RIGHT.

PROBLEMS with the current crop (fix in mosaic.py, do not re-hand-draw):
1. **Right ~10% is dead flat lake** + there is a WHITE vertical band near the right
   edge (approx x 990-1070 of the 1100px preview) = missing/failed tiles rendered
   white, NOT the #0e1a2b fill. Fix: make the miss-fill actually apply (check the
   `xc:#0e1a2b[256x256]` arg form works in this ImageMagick build) or post-fill
   white with dark navy.
2. **Top-left has a hard rectangular notch** of flat dark (missing tile block around
   x0-110, y60-700 in preview coords) — out-of-bounds NW corner. Crop it out.
3. Too much empty lake on the right for a card; shift framing WEST/SOUTH slightly
   and/or reduce width so the shoreline sits around 70-75% across.

SUGGESTED next framing: CLON ~= -87.76, CLAT ~= 41.845, Z=13 (keep), and after
mosaic, crop insetting ~120px from left and right to drop the notch + white band.
Verify no white pixels remain: `magick chicago-base.png -format "%[fx:maxima]" info:`
or histogram check for near-white.

Everything else in NOTES.md (tile API, service name, typography spec, back-of-card
fields, ship steps, site state) is still current.
