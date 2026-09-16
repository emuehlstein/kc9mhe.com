# KC9MHE QSL card (2026)

Standard QSL size: **5.5 × 3.5 in landscape**, 1650 × 1050 px at 300 dpi.

| File | Use |
|---|---|
| `kc9mhe-qsl-front-300dpi.png` | print, front |
| `kc9mhe-qsl-back-300dpi.png` | print, back |
| `kc9mhe-qsl-front.svg` / `kc9mhe-qsl-back.svg` | editable sources |
| `chicago-base.jpg` | 3300 × 2100 map base the SVGs reference |
| `card.py` | regenerates both SVGs |
| `mosaic.py` | refetches `chicago-base` from the tileserver |

## The map is real

Chicago is drawn from **Cook County LiDAR / DTM elevation data**, served by our own
tileserver at `tiles.chicagooffline.com`, service `cook-atak-dark-z10-16`
(zoom 10–16). `mosaic.py` stitches z14 tiles centred on `-87.695, 41.862` into a
3300 × 2100 base; `card.py` tones it toward the Chicago Offline palette and lays
the type over it. Street grid, the river, Navy Pier and the rail yards are all
actual terrain, not illustration.

Tile URL shape is `/services/<name>/tiles/{z}/{x}/{y}.png` — note the `/tiles/`
segment. Tiles are `TrueColorAlpha`; the lake is *transparent*, so flatten onto a
dark background or it composites to white.

## Rebuild

```bash
python3 mosaic.py      # only if the base needs refetching (tiles are cached)
python3 card.py
rsvg-convert -w 1650 front-v4.svg -o front-v4.png
```

Fonts are resolved by name (`Menlo`, `Helvetica Neue`). Use a **single** family per
`font-family` — rsvg-convert silently falls back to sans on a comma-separated stack.
Outline the text if the SVG is ever handed to a printer with different fonts.
