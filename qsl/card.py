#!/usr/bin/env python3
"""KC9MHE QSL card — front (real Chicago LiDAR) + back (QSO fields)."""
import pathlib

W, H = 1650, 1050
CYAN, AMBER = "#00E5FF", "#FFB300"
TEXT, DIM = "#eaf2f6", "#7d8c96"
INK = "#050a10"
MONO, SANS = "Menlo", "Helvetica Neue"

d = pathlib.Path(__file__).parent


def front() -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="16"/></clipPath>

  <!-- lift the LiDAR relief and push it cyan -->
  <filter id="tone" x="0" y="0" width="100%" height="100%">
    <feColorMatrix type="matrix" values="
        0.62 0     0     0 0
        0    0.86  0.10  0 0
        0.08 0.24  0.92  0 0
        0    0     0     1 0"/>
    <feComponentTransfer>
      <feFuncR type="gamma" amplitude="1" exponent="1.25" offset="0"/>
      <feFuncG type="gamma" amplitude="1" exponent="1.15" offset="0"/>
      <feFuncB type="gamma" amplitude="1" exponent="1.02" offset="0"/>
    </feComponentTransfer>
  </filter>

  <!-- fade the stair-stepped LiDAR coverage edge out over the lake -->
  <linearGradient id="lakeFade" x1="0.58" y1="0" x2="1" y2="0">
    <stop offset="0%"   stop-color="{INK}" stop-opacity="0"/>
    <stop offset="55%"  stop-color="{INK}" stop-opacity="0.55"/>
    <stop offset="100%" stop-color="{INK}" stop-opacity="0.96"/>
  </linearGradient>

  <linearGradient id="baseFade" x1="0" y1="1" x2="0" y2="0">
    <stop offset="0%"   stop-color="{INK}" stop-opacity="0.96"/>
    <stop offset="38%"  stop-color="{INK}" stop-opacity="0.62"/>
    <stop offset="75%"  stop-color="{INK}" stop-opacity="0.10"/>
    <stop offset="100%" stop-color="{INK}" stop-opacity="0.30"/>
  </linearGradient>

  <radialGradient id="vig" cx="0.40" cy="0.62" r="0.72">
    <stop offset="30%"  stop-color="{INK}" stop-opacity="0"/>
    <stop offset="72%"  stop-color="{INK}" stop-opacity="0.42"/>
    <stop offset="100%" stop-color="{INK}" stop-opacity="0.88"/>
  </radialGradient>
</defs>

<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="{INK}"/>
  <image xlink:href="chicago-base.jpg" x="0" y="0" width="{W}" height="{H}"
         preserveAspectRatio="xMidYMid slice" filter="url(#tone)"/>
  <rect width="{W}" height="{H}" fill="url(#lakeFade)"/>
  <rect width="{W}" height="{H}" fill="url(#vig)"/>
  <rect width="{W}" height="{H}" fill="url(#baseFade)"/>

  <!-- hairline frame -->
  <rect x="34" y="34" width="{W-68}" height="{H-68}" rx="6" fill="none"
        stroke="{CYAN}" stroke-width="1.6" opacity="0.30"/>

  <text x="92" y="132" font-family="{MONO}" font-size="26" letter-spacing="11"
        fill="{CYAN}">AMATEUR RADIO STATION</text>

  <text x="86" y="840" font-family="{MONO}" font-size="212" font-weight="bold"
        letter-spacing="2" fill="{TEXT}">KC9MHE</text>

  <line x1="94" y1="888" x2="700" y2="888" stroke="{CYAN}" stroke-width="3"/>

  <text x="94" y="944" font-family="{SANS}" font-size="41" letter-spacing="2"
        fill="{TEXT}">Eric Muehlstein</text>
  <text x="94" y="992" font-family="{MONO}" font-size="27" letter-spacing="5"
        fill="{DIM}">CHICAGO, ILLINOIS &#183; GRID EN61DT</text>

  <text x="{W-92}" y="132" text-anchor="end" font-family="{MONO}" font-size="26"
        letter-spacing="6" fill="{DIM}">LAKE MICHIGAN</text>
  <text x="{W-92}" y="992" text-anchor="end" font-family="{MONO}" font-size="26"
        letter-spacing="4" fill="{AMBER}">CHICAGOOFFLINE.COM</text>
</g>
</svg>'''


FIELDS_L = ["DATE (UTC)", "TIME (UTC)", "FREQ / BAND", "MODE", "RST SENT"]
FIELDS_R = ["POWER", "ANTENNA", "2-WAY", "QSL VIA", "REMARKS"]


def back() -> str:
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
         f'width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'''<defs><clipPath id="c"><rect width="{W}" height="{H}" rx="16"/></clipPath>
  <clipPath id="strip"><rect x="0" y="{H-150}" width="{W}" height="150"/></clipPath>
  <linearGradient id="stripFade" x1="0" y1="1" x2="0" y2="0">
    <stop offset="0%" stop-color="{INK}" stop-opacity="0.55"/>
    <stop offset="100%" stop-color="{INK}" stop-opacity="1"/>
  </linearGradient></defs>''',
         '<g clip-path="url(#c)">',
         f'<rect width="{W}" height="{H}" fill="{INK}"/>']

    # faint map strip along the bottom ties the back to the front
    o.append(f'<g clip-path="url(#strip)" opacity="0.22">'
             f'<image xlink:href="chicago-base.jpg" x="0" y="{H-430}" width="{W}" height="430" '
             f'preserveAspectRatio="xMidYMid slice"/></g>')
    o.append(f'<rect x="0" y="{H-150}" width="{W}" height="150" fill="url(#stripFade)"/>')

    o.append(f'<rect x="34" y="34" width="{W-68}" height="{H-68}" rx="6" fill="none" '
             f'stroke="{CYAN}" stroke-width="1.6" opacity="0.30"/>')

    o.append(f'<text x="92" y="126" font-family="{MONO}" font-size="46" font-weight="bold" '
             f'letter-spacing="6" fill="{TEXT}">KC9MHE</text>')
    o.append(f'<text x="{W-92}" y="126" text-anchor="end" font-family="{MONO}" font-size="24" '
             f'letter-spacing="5" fill="{CYAN}">CONFIRMING QSO WITH</text>')
    o.append(f'<line x1="92" y1="162" x2="{W-92}" y2="162" stroke="{CYAN}" '
             f'stroke-width="2" opacity="0.45"/>')

    # callsign-worked line, full width, the most important field
    o.append(f'<text x="92" y="228" font-family="{MONO}" font-size="22" letter-spacing="4" '
             f'fill="{CYAN}">TO RADIO</text>')
    o.append(f'<line x1="92" y1="272" x2="{W-92}" y2="272" stroke="{DIM}" '
             f'stroke-width="1.8" opacity="0.6"/>')

    y0, step = 356, 100
    for col, fields in ((92, FIELDS_L), (880, FIELDS_R)):
        for i, f in enumerate(fields):
            y = y0 + i * step
            o.append(f'<text x="{col}" y="{y-14}" font-family="{MONO}" font-size="22" '
                     f'letter-spacing="4" fill="{CYAN}">{f}</text>')
            o.append(f'<line x1="{col}" y1="{y+18}" x2="{col+678}" y2="{y+18}" '
                     f'stroke="{DIM}" stroke-width="1.6" opacity="0.55"/>')

    o.append(f'<text x="92" y="{H-124}" font-family="{MONO}" font-size="22" '
             f'letter-spacing="4" fill="{AMBER}">PSE / TNX QSL &#183; LoTW &#183; QRZ.COM/DB/KC9MHE</text>')
    o.append(f'<text x="{W-92}" y="{H-124}" text-anchor="end" font-family="{MONO}" '
             f'font-size="22" letter-spacing="4" fill="{DIM}">GRID EN61DT &#183; CHICAGO, IL</text>')
    o += ['</g>', '</svg>']
    return "\n".join(o)


(d / "front-v4.svg").write_text(front())
(d / "back-v4.svg").write_text(back())
print("wrote front-v4.svg, back-v4.svg")
