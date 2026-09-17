#!/usr/bin/env python3
"""
Hero v4 — use the purpose-built high-res Summerdale service.

Why this beats v1-v3: the county DTM (cook-atak-dark-z10-16) tops out around z16
and the north side is topographically FLAT, so it renders as dull murk. The
tileserver already carries `summerdale-lidar-dark-9x` (z15-20, 9x vertical
exaggeration, bounds -87.71,41.95 -> -87.65,42.00) which covers Eric's blocks at
building-level detail. Fetch z17 and downscale -> sharp, real structure.
"""
import math, pathlib, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
import urllib.request

SVC  = "summerdale-lidar-dark-9x"
BASE = f"https://tiles.chicagooffline.com/services/{SVC}/tiles"
Z, TS = 17, 256
BOUNDS = (-87.71, 41.95, -87.65, 42.00)   # w, s, e, n  (from TileJSON)

INK, CYAN, AMBER, MONO = "#050a10", "#00E5FF", "#FFB300", "Menlo"
WF, HF = 1920, 700
ASPECT = WF / HF

QTH_LAT, QTH_LON = 41.9785215, -87.6821048    # 2101 W Summerdale

LON_SPAN = 0.0500                              # ~4.1 km wide
LAT_SPAN = LON_SPAN / ASPECT                   # keep hero aspect exactly
# .hero-inner puts the text block across the bottom ~40%, so lift the marker to
# 36% height. Keep it horizontally CENTRED: .hero-bg uses object-fit:cover, which
# crops width hard on narrow viewports, and centre survives that crop.
QTH_FRAC_Y = 0.36

d = pathlib.Path(__file__).parent
cache = d / "tiles_summerdale"; cache.mkdir(exist_ok=True)

n = 2 ** Z
def lon2px(lon): return (lon + 180.0) / 360.0 * n * TS
def lat2px(lat):
    s = math.sin(math.radians(lat))
    return (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n * TS

# centre on the QTH, then clamp inside the service bounds
clon = min(max(QTH_LON, BOUNDS[0] + LON_SPAN/2), BOUNDS[2] - LON_SPAN/2)
_north_target = QTH_LAT + QTH_FRAC_Y * LAT_SPAN
clat = min(max(_north_target - LAT_SPAN/2,
               BOUNDS[1] + LAT_SPAN/2), BOUNDS[3] - LAT_SPAN/2)
print(f"window centre {clon:.5f},{clat:.5f}  span {LON_SPAN}x{LAT_SPAN:.5f} deg")

west, east = clon - LON_SPAN/2, clon + LON_SPAN/2
north, south = clat + LAT_SPAN/2, clat - LAT_SPAN/2
for nm, v, lo, hi in (("west", west, BOUNDS[0], BOUNDS[2]),
                      ("east", east, BOUNDS[0], BOUNDS[2]),
                      ("south", south, BOUNDS[1], BOUNDS[3]),
                      ("north", north, BOUNDS[1], BOUNDS[3])):
    if not (lo <= v <= hi):
        sys.exit(f"{nm} edge {v} outside service bounds {BOUNDS}")

x0, y0 = lon2px(west), lat2px(north)
SRC_W = round(lon2px(east) - x0)
SRC_H = round(lat2px(south) - y0)
print(f"z{Z} source {SRC_W}x{SRC_H}  ({SRC_W/WF:.2f}x oversample)")

qx, qy = round(lon2px(QTH_LON) - x0), round(lat2px(QTH_LAT) - y0)
print(f"QTH src ({qx},{qy}) -> final ({round(qx*WF/SRC_W)},{round(qy*HF/SRC_H)})")

tx0, ty0 = int(x0 // TS), int(y0 // TS)
tx1, ty1 = int((x0 + SRC_W) // TS), int((y0 + SRC_H) // TS)
cols, rws = tx1-tx0+1, ty1-ty0+1
print(f"tiles x[{tx0}..{tx1}] y[{ty0}..{ty1}] = {cols}x{rws} = {cols*rws}")

def fetch(a):
    tx, ty = a
    p = cache / f"{Z}_{tx}_{ty}.png"
    if p.exists() and p.stat().st_size > 500:
        return True
    try:
        req = urllib.request.Request(f"{BASE}/{Z}/{tx}/{ty}.png",
                                     headers={"User-Agent": "kc9mhe-hero/4.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            b = r.read()
        if len(b) > 500:
            p.write_bytes(b); return True
    except Exception as e:
        print(f"  miss {tx},{ty}: {e}", file=sys.stderr)
    return False

jobs = [(tx, ty) for ty in range(ty0, ty1+1) for tx in range(tx0, tx1+1)]
with ThreadPoolExecutor(max_workers=8) as ex:
    ok = sum(ex.map(fetch, jobs))
print(f"tiles {ok}/{len(jobs)}" + ("  complete" if ok == len(jobs) else "  <-- gaps"))
if ok == 0:
    sys.exit("no tiles fetched")

fill = d / "_f4.png"
subprocess.run(["magick", "-size", f"{TS}x{TS}", f"xc:{INK}", str(fill)], check=True)
rowfiles = []
for ty in range(ty0, ty1+1):
    rf = d / f"_r4_{ty}.png"
    parts = []
    for tx in range(tx0, tx1+1):
        p = cache / f"{Z}_{tx}_{ty}.png"
        parts.append(str(p) if p.exists() and p.stat().st_size > 500 else str(fill))
    subprocess.run(["magick"] + parts + ["+append", str(rf)], check=True)
    rowfiles.append(str(rf))
full = d / "_full4.png"
subprocess.run(["magick"] + rowfiles + ["-append", str(full)], check=True)

ox, oy = int(x0 - tx0*TS), int(y0 - ty0*TS)
base = d / "hero4-base.png"
# service type is "overlay" -> flatten the alpha onto ink or it goes white
subprocess.run(["magick", str(full), "-crop", f"{SRC_W}x{SRC_H}+{ox}+{oy}", "+repage",
                "-background", INK, "-alpha", "remove", "-alpha", "off",
                "-modulate", "128,118", str(base)], check=True)
for f in rowfiles + [str(fill), str(full)]:
    pathlib.Path(f).unlink(missing_ok=True)
print("wrote hero4-base.png")

# The source is downscaled by S, so size every marker element in FINAL pixels and
# multiply up. Sizing in source px (v4 first pass) made the marker a tiny speck.
S = SRC_W / WF
r_glow, r_ring, r_dot = 44*S, 26*S, 7*S
stem_a, stem_b = 23*S, 46*S
house_scale = (46*S) / 34.0        # house path is 34 units wide -> ~46 final px
house_dy = 64*S
print(f"marker scaled x{S:.2f}: ring r={r_ring:.0f}src ({r_ring/S:.0f} final px)")

HOUSE = f'''
  <g transform="translate({qx},{qy-house_dy}) scale({house_scale:.3f})">
    <path d="M -17 2 L 0 -14 L 17 2 L 17 3 L 12 3 L 12 17 L -12 17 L -12 3 L -17 3 Z"
          fill="{AMBER}" stroke="{INK}" stroke-width="1.8" stroke-linejoin="round"
          vector-effect="non-scaling-stroke"/>
    <rect x="-4.5" y="6" width="9" height="11" fill="{INK}" opacity="0.75"/>
    <rect x="6" y="-9" width="5" height="8.5" fill="{AMBER}" stroke="{INK}"
          stroke-width="1.4" vector-effect="non-scaling-stroke"/>
  </g>'''

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{SRC_W}" height="{SRC_H}" viewBox="0 0 {SRC_W} {SRC_H}">
<defs>
  <filter id="tone" x="0" y="0" width="100%" height="100%">
    <feColorMatrix type="matrix" values="
        0.62 0    0    0 0
        0    0.88 0.12 0 0
        0.10 0.26 0.98 0 0
        0    0    0    1 0"/>
    <feComponentTransfer>
      <feFuncR type="gamma" amplitude="1" exponent="0.92" offset="0"/>
      <feFuncG type="gamma" amplitude="1" exponent="0.90" offset="0"/>
      <feFuncB type="gamma" amplitude="1" exponent="0.86" offset="0"/>
    </feComponentTransfer>
  </filter>
  <linearGradient id="bot" x1="0" y1="1" x2="0" y2="0">
    <stop offset="0%"  stop-color="{INK}" stop-opacity="0.45"/>
    <stop offset="18%" stop-color="{INK}" stop-opacity="0.18"/>
    <stop offset="40%" stop-color="{INK}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="top" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%"  stop-color="{INK}" stop-opacity="0.22"/>
    <stop offset="16%" stop-color="{INK}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="side" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%"  stop-color="{INK}" stop-opacity="0.32"/>
    <stop offset="14%" stop-color="{INK}" stop-opacity="0"/>
    <stop offset="88%" stop-color="{INK}" stop-opacity="0"/>
    <stop offset="100%" stop-color="{INK}" stop-opacity="0.32"/>
  </linearGradient>
  <filter id="glow" x="-70%" y="-70%" width="240%" height="240%">
    <feGaussianBlur stdDeviation="{14*S:.0f}" result="b"/>
    <feComposite in="SourceGraphic" in2="b" operator="over"/>
  </filter>
</defs>

<rect width="{SRC_W}" height="{SRC_H}" fill="{INK}"/>
<image xlink:href="hero4-base.png" x="0" y="0" width="{SRC_W}" height="{SRC_H}"
       preserveAspectRatio="xMidYMid slice" filter="url(#tone)"/>
<rect width="{SRC_W}" height="{SRC_H}" fill="url(#top)"/>
<rect width="{SRC_W}" height="{SRC_H}" fill="url(#bot)"/>
<rect width="{SRC_W}" height="{SRC_H}" fill="url(#side)"/>

<circle cx="{qx}" cy="{qy}" r="{r_glow:.1f}" fill="none" stroke="{CYAN}"
        stroke-width="{3.5*S:.1f}" opacity="0.26" filter="url(#glow)"/>
<circle cx="{qx}" cy="{qy}" r="{r_ring:.1f}" fill="none" stroke="{CYAN}"
        stroke-width="{4*S:.1f}" opacity="0.9"/>
<circle cx="{qx}" cy="{qy}" r="{r_dot:.1f}" fill="{CYAN}"/>
<line x1="{qx}" y1="{qy-stem_a:.1f}" x2="{qx}" y2="{qy-stem_b:.1f}" stroke="{CYAN}"
      stroke-width="{4*S:.1f}" opacity="0.8"/>
{HOUSE}
</svg>'''

(d / "hero4.svg").write_text(svg)
subprocess.run(["rsvg-convert", "-w", str(SRC_W), str(d/"hero4.svg"),
                "-o", str(d/"hero4-2x.png")], check=True)
subprocess.run(["magick", str(d/"hero4-2x.png"), "-filter", "Lanczos",
                "-resize", f"{WF}x{HF}!", "-quality", "90", str(d/"hero-v4.jpg")], check=True)
subprocess.run(["magick", str(d/"hero4-2x.png"), "-filter", "Lanczos",
                "-resize", f"{WF*2}x{HF*2}!", "-quality", "84", str(d/"hero-v4@2x.jpg")], check=True)
print(f"wrote hero-v4.jpg {WF}x{HF} + hero-v4@2x.jpg")
