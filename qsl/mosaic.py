#!/usr/bin/env python3
"""Mosaic real Chicago LiDAR tiles from the Chicago Offline tileserver."""
import math, pathlib, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
import urllib.request

SVC = "cook-atak-dark-z10-16"
BASE = f"https://tiles.chicagooffline.com/services/{SVC}/tiles"
Z = 14
TS = 256

# landscape framing: city + lakefront
CLON, CLAT = -87.695, 41.862
OUT_W, OUT_H = 3300, 2100          # 2x the 1650x1050 card

d = pathlib.Path(__file__).parent
cache = d / "tiles"; cache.mkdir(exist_ok=True)

n = 2 ** Z
def lon2px(lon): return (lon + 180.0) / 360.0 * n * TS
def lat2px(lat):
    s = math.sin(math.radians(lat))
    return (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n * TS

cx, cy = lon2px(CLON), lat2px(CLAT)
x0, y0 = cx - OUT_W / 2, cy - OUT_H / 2
tx0, ty0 = int(x0 // TS), int(y0 // TS)
tx1, ty1 = int((x0 + OUT_W) // TS), int((y0 + OUT_H) // TS)
cols, rows = tx1 - tx0 + 1, ty1 - ty0 + 1
print(f"z{Z}  tiles x[{tx0}..{tx1}] y[{ty0}..{ty1}]  = {cols}x{rows} = {cols*rows}")

def fetch(args):
    tx, ty = args
    p = cache / f"{Z}_{tx}_{ty}.png"
    if p.exists() and p.stat().st_size > 500:
        return p, True
    url = f"{BASE}/{Z}/{tx}/{ty}.png"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "kc9mhe-qsl/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            b = r.read()
        if len(b) > 500:
            p.write_bytes(b); return p, True
    except Exception as e:
        print("  miss", tx, ty, e, file=sys.stderr)
    return p, False

jobs = [(tx, ty) for ty in range(ty0, ty1 + 1) for tx in range(tx0, tx1 + 1)]
ok = 0
with ThreadPoolExecutor(max_workers=4) as ex:
    for p, good in ex.map(fetch, jobs):
        ok += good
print(f"fetched/cached {ok}/{len(jobs)}")

# assemble with ImageMagick
fill = d / "_fill.png"
subprocess.run(["magick", "-size", f"{TS}x{TS}", "xc:#0e1a2b", str(fill)], check=True)

rowfiles = []
for ty in range(ty0, ty1 + 1):
    rf = d / f"_row{ty}.png"
    parts = []
    for tx in range(tx0, tx1 + 1):
        p = cache / f"{Z}_{tx}_{ty}.png"
        parts.append(str(p) if p.exists() and p.stat().st_size > 500 else str(fill))
    subprocess.run(["magick"] + parts + ["+append", str(rf)], check=True)
    rowfiles.append(str(rf))

full = d / "_full.png"
subprocess.run(["magick"] + rowfiles + ["-append", str(full)], check=True)

# crop to the exact requested window
ox, oy = int(x0 - tx0 * TS), int(y0 - ty0 * TS)
subprocess.run(["magick", str(full), "-crop", f"{OUT_W}x{OUT_H}+{ox}+{oy}", "+repage",
                "-background", "#071019", "-alpha", "remove", "-alpha", "off",
                str(d / "chicago-base.png")], check=True)
for f in rowfiles: pathlib.Path(f).unlink(missing_ok=True)
fill.unlink(missing_ok=True)
full.unlink(missing_ok=True)
print("wrote chicago-base.png")
