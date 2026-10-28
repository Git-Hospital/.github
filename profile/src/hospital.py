#!/usr/bin/env python3
"""Draw the Git Hospital organization profile.

  python3 profile/src/hospital.py hero            -> profile/assets/{hospital,logo,pathway}.svg
  python3 profile/src/hospital.py vitals --out D  -> D/<repo>.svg, one patient monitor per tool,
                                                     and D/cases.svg, the case board

The monitors and the case board show live numbers from the GitHub API, so a scheduled workflow
(.github/workflows/vitals.yml) redraws them every day and pushes them to the
`vitals` branch. Set GH_TOKEN to avoid the anonymous rate limit.

GitHub serves README images through a proxy that blocks external fonts, so the
fonts are subset to the glyphs each image uses and embedded as base64 woff2.
Needs fonttools and brotli (pip install fonttools brotli).
"""
import argparse
import base64
import datetime as dt
import json
import math
import os
import random
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
CACHE = HERE / ".fonts"
CDN = "https://cdn.jsdelivr.net/npm/@fontsource"
FONTS = {
    "display": f"{CDN}/fraunces@5.1.0/files/fraunces-latin-600-normal.woff2",
    "sans4": f"{CDN}/inter@5.1.0/files/inter-latin-400-normal.woff2",
    "sans5": f"{CDN}/inter@5.1.0/files/inter-latin-500-normal.woff2",
    "mono": f"{CDN}/jetbrains-mono@5.1.0/files/jetbrains-mono-latin-500-normal.woff2",
}
FAMILY = {"display": ("Display", 600), "sans4": ("Sans", 400), "sans5": ("Sans", 500), "mono": ("Mono", 500)}

BG, SURFACE, BORDER = "#0c0a09", "#171310", "#3a2f28"
INK50, INK200, INK400, INK600 = "#f4ece2", "#d1c3b4", "#968779", "#695c51"
RED, AMBER, BLUE = "#c7331e", "#d9a441", "#3b82f6"
GREEN, MUTED = "#4ade80", "#7d8f84"  # monitor trace and labels
WARM, COOL = "#e9c27a", "#d6e6f5"     # lit windows

ORG = "Git-Hospital"
WARDS = [  # repo, display name, bed label, one-line description
    ("helmbulance", "Helmbulance", "BED 01 · EMERGENCY", "Day-2 behaviour tests for Helm charts on a throwaway cluster"),
    ("meshmedic", "MeshMedic", "BED 02 · INTENSIVE CARE", "Istio telemetry in, reviewed GitOps pull request out"),
    ("boards", "boards", "BED 03 · CLINICAL TRIALS", "Benchmark that scores diagnosis tools on known defects"),
    ("githealthcheck", "GitHealthCheck", "BED 04 · CHECK-UP", "Code health analyzer: a measurement, or null with a reason"),
]
PULSE_DAYS = 90


# ---------------------------------------------------------------- svg helpers

def fonts_css(used: dict) -> str:
    """used: font key -> text drawn in that font."""
    CACHE.mkdir(exist_ok=True)
    faces = []
    for key, chars in used.items():
        if not chars:
            continue
        src = CACHE / f"{key}.woff2"
        if not src.exists():
            urllib.request.urlretrieve(FONTS[key], src)
        with tempfile.NamedTemporaryFile(suffix=".woff2") as out:
            subprocess.run(["pyftsubset", str(src), f"--text={chars}", "--flavor=woff2",
                            "--layout-features=kern,liga", f"--output-file={out.name}"], check=True)
            data = base64.b64encode(Path(out.name).read_bytes()).decode()
        family, weight = FAMILY[key]
        faces.append(f"@font-face {{ font-family: '{family}'; font-weight: {weight}; "
                     f"src: url(data:font/woff2;base64,{data}) format('woff2'); }}")
    return "\n".join(faces)


class Canvas:
    """Collects elements and the text each font has to cover."""

    def __init__(self):
        self.parts, self.used = [], {k: "" for k in FONTS}

    def add(self, *parts):
        self.parts.extend(parts)

    def text(self, x, y, cls, s, font, **attrs):
        self.used[font] += s
        extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in attrs.items())
        self.parts.append(f'<text class="{cls}" x="{x}" y="{y}"{extra}>{escape(s)}</text>')

    def svg(self, w, h, label, css) -> str:
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
                f'role="img" aria-label="{escape(label, {chr(34): "&quot;"})}">\n'
                f"<style>\n{fonts_css(self.used)}\n{css}\n"
                "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }\n"
                f"</style>\n" + "\n".join(self.parts) + "\n</svg>\n")


GLOW_FILTER = ('<filter id="neon" x="-20%" y="-60%" width="140%" height="220%">'
               '<feGaussianBlur stdDeviation="3.5" result="b"/>'
               '<feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')


# ---------------------------------------------------------------- hero: the hospital at night

def ambulance() -> str:
    """Ambulance facing right, drawn around its rear bottom corner (0, 0)."""
    def wheel(x):
        spokes = "".join(
            f'<line x1="{x}" y1="-12" x2="{x + 7 * math.cos(a):.1f}" y2="{-12 + 7 * math.sin(a):.1f}" '
            f'stroke="{INK400}" stroke-width="2"/>' for a in (0, 2.094, 4.189))
        return (f'<circle cx="{x}" cy="-12" r="13" fill="#1b1714" stroke="{INK600}" stroke-width="3"/>'
                f'<g class="roll">{spokes}<circle cx="{x}" cy="-12" r="2.5" fill="{INK200}"/></g>')
    lights = "".join(
        f'<circle class="flash {cls}" cx="{x}" cy="-82" r="22" fill="url(#glow-{c})"/>'
        f'<rect class="flash {cls}" x="{x - 6}" y="-87" width="12" height="9" rx="2" fill="{col}"/>'
        for x, c, col, cls in ((156, "r", RED, ""), (170, "b", BLUE, "late")))
    waves = "".join(
        f'<circle class="wave" cx="163" cy="-83" r="16" fill="none" stroke="{RED if k % 2 == 0 else BLUE}" '
        f'stroke-width="2" style="animation-delay:{k * .45:.2f}s"/>' for k in range(3))
    speed = "".join(
        f'<line class="speed" x1="{-70 + d}" y1="{y}" x2="-18" y2="{y}" stroke="{INK400}" stroke-width="2" stroke-linecap="round"/>'
        for y, d in ((-62, 0), (-44, 22), (-26, 10)))
    return "".join([
        speed,
        '<path d="M204 -27 L300 -52 L300 -2 Z" fill="url(#beam)"/>',
        '<ellipse cx="103" cy="0" rx="112" ry="5" fill="#000" fill-opacity=".45"/>',
        waves,
        f'<rect x="0" y="-80" width="146" height="66" rx="6" fill="{INK50}"/>',
        f'<path d="M140 -80 L170 -80 L196 -52 L207 -47 L207 -20 Q207 -14 201 -14 L140 -14 Z" fill="{INK50}"/>',
        '<path d="M150 -72 L167 -72 L187 -52 L150 -52 Z" fill="#2b3138"/>',
        f'<rect x="0" y="-38" width="207" height="7" fill="{RED}"/>',
        f'<rect x="60" y="-68" width="8" height="24" rx="1.5" fill="{RED}"/><rect x="52" y="-60" width="24" height="8" rx="1.5" fill="{RED}"/>',
        f'<line x1="140" y1="-50" x2="140" y2="-16" stroke="{INK400}" stroke-opacity=".6"/>',
        f'<rect x="200" y="-30" width="7" height="6" rx="1.5" fill="{AMBER}"/>',
        f'<rect x="-3" y="-22" width="8" height="6" rx="1.5" fill="{RED}"/>',
        f'<rect x="146" y="-82" width="34" height="4" rx="2" fill="{INK400}"/>',
        lights, wheel(42), wheel(168),
    ])


def windows(rnd, x0, x1, y0, y1, dx, dy, w, h, lit=.45, rooms=.12) -> str:
    """A grid of windows: some lit, some switching on and off like occupied rooms."""
    out = []
    for y in range(y0, y1, dy):
        for x in range(x0, x1, dx):
            r = rnd.random()
            if r < lit:
                col = COOL if rnd.random() < .7 else WARM
                op = .55 + rnd.random() * .35
                if rnd.random() < rooms:
                    delay = rnd.random() * 9
                    dur = 7 + rnd.random() * 8
                    out.append(f'<rect class="room" style="animation-duration:{dur:.1f}s;animation-delay:-{delay:.1f}s" '
                               f'x="{x}" y="{y}" width="{w}" height="{h}" fill="{col}" fill-opacity="{op:.2f}"/>')
                else:
                    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{col}" fill-opacity="{op:.2f}"/>')
            else:
                out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#15110f"/>')
    return "".join(out)


def hero() -> str:
    W, H, road = 1200, 620, 500
    rnd = random.Random(11)
    c = Canvas()
    c.add("<defs>", GLOW_FILTER,
          '<clipPath id="frame"><rect width="1200" height="620" rx="18"/></clipPath>',
          f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b0908"/><stop offset="1" stop-color="#1c1512"/></linearGradient>',
          f'<radialGradient id="glow-r"><stop offset="0" stop-color="{RED}" stop-opacity=".75"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>',
          f'<radialGradient id="glow-b"><stop offset="0" stop-color="{BLUE}" stop-opacity=".75"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>',
          f'<radialGradient id="crossglow"><stop offset="0" stop-color="{RED}" stop-opacity=".6"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>',
          f'<linearGradient id="beam" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{AMBER}" stop-opacity=".45"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></linearGradient>',
          f'<linearGradient id="pool" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{AMBER}" stop-opacity=".30"/><stop offset="1" stop-color="{AMBER}" stop-opacity=".04"/></linearGradient>',
          f'<linearGradient id="lamp" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{AMBER}" stop-opacity=".2"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></linearGradient>',
          f'<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{COOL}" stop-opacity=".35"/><stop offset="1" stop-color="{COOL}" stop-opacity="0"/></linearGradient>',
          f'<linearGradient id="glass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{COOL}" stop-opacity=".55"/><stop offset="1" stop-color="{WARM}" stop-opacity=".25"/></linearGradient>',
          "</defs>",
          '<g clip-path="url(#frame)">',
          f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')

    # stars and moon
    for _ in range(46):
        x, y, r = rnd.uniform(10, W - 10), rnd.uniform(10, 300), rnd.choice((0.8, 1, 1.2, 1.6))
        tw = ' class="twinkle" style="animation-delay:-%.1fs"' % rnd.uniform(0, 4) if rnd.random() < .35 else ""
        c.add(f'<circle{tw} cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{INK50}" fill-opacity="{rnd.uniform(.25, .7):.2f}"/>')
    c.add(f'<circle cx="1096" cy="86" r="22" fill="{INK200}" fill-opacity=".9"/><circle cx="1106" cy="79" r="20" fill="#0d0b0a"/>')

    # far skyline
    x = -20
    while x < W:
        w, h = rnd.choice((60, 74, 90, 110)), rnd.randint(70, 170)
        c.add(f'<rect x="{x}" y="{road - h}" width="{w - 8}" height="{h}" fill="#1a1512"/>')
        c.add(windows(rnd, x + 8, x + w - 18, road - h + 12, road - 10, 13, 15, 5, 7, lit=.14, rooms=.05))
        x += w

    # main tower
    tx0, tx1, top = 330, 880, 190
    c.add(f'<rect x="{tx0}" y="{top}" width="{tx1 - tx0}" height="{road - top}" fill="#2a221d"/>',
          f'<rect x="{tx0 - 6}" y="{top - 6}" width="{tx1 - tx0 + 12}" height="8" fill="#3a2f28"/>')
    for fy in range(top + 52, road - 60, 44):  # floor lines
        c.add(f'<rect x="{tx0}" y="{fy + 26}" width="{tx1 - tx0}" height="3" fill="#231c18"/>')
    c.add(windows(rnd, tx0 + 22, tx1 - 30, top + 34, road - 74, 42, 44, 26, 18))
    # vertical accent with a lit cross
    c.add(f'<rect x="575" y="{top}" width="60" height="{road - top}" fill="#30271f"/>',
          f'<circle cx="605" cy="{top + 48}" r="40" fill="url(#crossglow)" class="buzz"/>',
          f'<rect x="597" y="{top + 26}" width="16" height="44" rx="2" fill="{RED}"/>',
          f'<rect x="583" y="{top + 40}" width="44" height="16" rx="2" fill="{RED}"/>')
    # main entrance
    c.add(f'<rect x="560" y="{road - 62}" width="90" height="62" fill="url(#glass)"/>',
          f'<line x1="605" y1="{road - 62}" x2="605" y2="{road}" stroke="#2a221d" stroke-width="3"/>',
          f'<rect x="548" y="{road - 72}" width="114" height="10" fill="#3a2f28"/>')

    # rooftop sign on a truss, the second I flickers like a tired tube
    c.add(f'<g stroke="#3a2f28" stroke-width="3">' + "".join(
        f'<line x1="{x}" y1="{top - 6}" x2="{x}" y2="{top - 40}"/>' for x in (430, 520, 610, 700, 790)) +
        f'<line x1="420" y1="{top - 40}" x2="800" y2="{top - 40}"/></g>')
    c.used["sans5"] += "GIT HOSPITAL"
    c.add(f'<text class="sign" x="610" y="{top - 50}" text-anchor="middle" filter="url(#neon)">'
          f'GIT HOSP<tspan class="tube">I</tspan>TAL</text>')
    # mast with a rotating beacon and an aviation light
    mx = 850
    c.add(f'<line x1="{mx}" y1="{top - 6}" x2="{mx}" y2="{top - 92}" stroke="#3a2f28" stroke-width="3"/>',
          f'<g class="beacon" style="transform-origin:{mx}px {top - 70}px">'
          f'<path d="M{mx} {top - 70} L{mx + 170} {top - 92} L{mx + 170} {top - 48} Z" fill="url(#sweep)"/></g>',
          f'<rect x="{mx - 7}" y="{top - 76}" width="14" height="12" rx="3" fill="{COOL}"/>',
          f'<circle class="blink" cx="{mx}" cy="{top - 96}" r="4" fill="{RED}" filter="url(#neon)"/>')

    # outpatient wing (left)
    c.add(f'<rect x="150" y="330" width="180" height="{road - 330}" fill="#251e1a"/>',
          f'<rect x="144" y="324" width="192" height="7" fill="#3a2f28"/>',
          windows(rnd, 166, 318, 350, road - 40, 34, 38, 22, 16, lit=.5))
    # emergency wing (right) with canopy
    c.add(f'<rect x="880" y="350" width="150" height="{road - 350}" fill="#251e1a"/>',
          f'<rect x="874" y="344" width="162" height="7" fill="#3a2f28"/>',
          windows(rnd, 896, 1018, 368, 410, 34, 30, 22, 14, lit=.6),
          f'<path d="M870 {road} L870 418 L1150 418 L1150 {road} Z" fill="url(#pool)"/>',
          f'<rect x="900" y="{road - 64}" width="64" height="64" fill="url(#glass)"/>',
          f'<rect x="868" y="404" width="292" height="16" rx="2" fill="#3a2f28"/>',
          f'<rect x="1142" y="420" width="8" height="{road - 420}" fill="#3a2f28"/>',
          f'<rect x="960" y="383" width="150" height="22" rx="3" fill="{RED}" class="buzz" filter="url(#neon)"/>')
    c.text(1035, 399, "er", "EMERGENCY", "mono", text_anchor="middle")

    # trees and street lamps in front
    for tx_, s in ((96, 1), (300, .8), (1180, .9)):
        c.add(f'<g fill="#16120f"><rect x="{tx_ - 3}" y="{road - 40 * s}" width="6" height="{40 * s}"/>'
              f'<circle cx="{tx_}" cy="{road - 58 * s}" r="{26 * s}"/><circle cx="{tx_ - 16 * s}" cy="{road - 44 * s}" r="{18 * s}"/>'
              f'<circle cx="{tx_ + 16 * s}" cy="{road - 44 * s}" r="{18 * s}"/></g>')
    for lx in (470, 760):
        c.add(f'<path d="M{lx - 60} {road} L{lx - 8} {road - 98} L{lx + 8} {road - 98} L{lx + 60} {road} Z" fill="url(#lamp)"/>',
              f'<line x1="{lx + 18}" y1="{road}" x2="{lx + 18}" y2="{road - 104}" stroke="#3a2f28" stroke-width="3"/>',
              f'<path d="M{lx + 18} {road - 104} Q{lx + 18} {road - 112} {lx + 8} {road - 110} L{lx} {road - 106}" fill="none" stroke="#3a2f28" stroke-width="3"/>',
              f'<rect x="{lx - 9}" y="{road - 108}" width="16" height="6" rx="2" fill="{AMBER}"/>')

    # road
    c.add(f'<rect x="0" y="{road}" width="{W}" height="44" fill="#100d0b"/>',
          f'<line x1="0" y1="{road}" x2="{W}" y2="{road}" stroke="{INK600}"/>',
          f'<line x1="0" y1="{road + 22}" x2="{W}" y2="{road + 22}" stroke="{INK600}" stroke-opacity=".6" stroke-dasharray="26 18"/>')

    # the ambulance arrives from the right and stops under the canopy (mirrored: it faces left)
    park = 1136
    c.add(f'<g class="arrive"><g transform="translate({park} {road + 14}) scale(-1 1)">{ambulance()}</g></g>')

    # caption strip
    c.add(f'<rect x="0" y="{road + 44}" width="{W}" height="{H - road - 44}" fill="{SURFACE}"/>',
          f'<line x1="0" y1="{road + 44}" x2="{W}" y2="{road + 44}" stroke="{BORDER}"/>')
    c.text(48, 590, "cap", "Open-source tools that diagnose infrastructure and code.", "sans4")
    c.text(W - 48, 590, "mono", "OPEN 24/7  ·  github.com/Git-Hospital", "mono", text_anchor="end")
    c.add("</g>")

    css = f"""
.sign {{ font: 500 40px 'Sans', 'Helvetica Neue', Arial, sans-serif; letter-spacing: 9px; fill: #ffe9e2; stroke: {RED}; stroke-width: 1.2px; }}
.er   {{ font: 500 13px 'Mono', monospace; letter-spacing: 3px; fill: {INK50}; }}
.cap  {{ font: 400 19px 'Sans', 'Helvetica Neue', Arial, sans-serif; fill: {INK200}; }}
.mono {{ font: 500 14px 'Mono', 'SFMono-Regular', Menlo, monospace; fill: {INK400}; letter-spacing: .5px; }}
.tube {{ animation: tube 5s steps(1) infinite; }}
.buzz {{ animation: buzz 4.3s steps(1) infinite; }}
.room {{ animation: room 11s steps(1) infinite; }}
.twinkle {{ animation: twinkle 3.2s ease-in-out infinite; }}
.blink {{ animation: blink 1.6s steps(1) infinite; }}
.beacon {{ animation: beacon 4s linear infinite; }}
.arrive {{ animation: arrive 12s cubic-bezier(.15,.6,.35,1) infinite; }}
.roll {{ transform-box: fill-box; transform-origin: center; animation: roll 12s cubic-bezier(.15,.6,.35,1) infinite; }}
.speed {{ animation: speed 12s linear infinite; }}
.flash {{ animation: flash .5s steps(1) infinite; }}
.late {{ animation-delay: .25s; }}
.wave {{ transform-box: fill-box; transform-origin: center; opacity: 0; animation: wave 1.35s ease-out infinite; }}
@keyframes tube {{ 0%, 62% {{ opacity: 1; }} 63% {{ opacity: .15; }} 65% {{ opacity: 1; }} 67% {{ opacity: .2; }} 70%, 100% {{ opacity: 1; }} }}
@keyframes buzz {{ 0%, 90% {{ opacity: 1; }} 91% {{ opacity: .55; }} 93% {{ opacity: 1; }} 95% {{ opacity: .7; }} 96%, 100% {{ opacity: 1; }} }}
@keyframes room {{ 0%, 55% {{ opacity: 1; }} 56%, 100% {{ opacity: .08; }} }}
@keyframes twinkle {{ 50% {{ opacity: .2; }} }}
@keyframes blink {{ 0%, 70% {{ opacity: 1; }} 71%, 100% {{ opacity: .15; }} }}
@keyframes beacon {{ to {{ transform: rotate(-360deg); }} }}
@keyframes arrive {{ 0% {{ transform: translateX(380px); opacity: 1; }} 32%, 88% {{ transform: none; opacity: 1; }} 96%, 100% {{ transform: none; opacity: 0; }} }}
@keyframes roll {{ 0% {{ transform: rotate(0); }} 32%, 100% {{ transform: rotate(1260deg); }} }}
@keyframes speed {{ 0%, 22% {{ opacity: .6; }} 30%, 100% {{ opacity: 0; }} }}
@keyframes flash {{ 0% {{ opacity: 1; }} 50% {{ opacity: .12; }} }}
@keyframes wave {{ 0% {{ opacity: .9; transform: scale(.5); }} 100% {{ opacity: 0; transform: scale(2.6); }} }}
@media (prefers-reduced-motion: reduce) {{ .wave, .speed {{ opacity: 0 !important; }} }}
"""
    label = ("Git Hospital at night: a hospital with a neon GIT HOSPITAL sign on the roof, a rotating beacon, "
             "lit wards and an ambulance arriving at the emergency entrance. Open-source tools that diagnose "
             "infrastructure and code. github.com/Git-Hospital")
    return c.svg(W, H, label, css)


def logo() -> str:
    """Square avatar: the red cross with a git branch running through it."""
    c = Canvas()
    c.add(f'<rect width="512" height="512" fill="{BG}"/>',
          f'<circle cx="256" cy="256" r="200" fill="url(#g)"/>',
          f'<defs><radialGradient id="g"><stop offset="0" stop-color="{RED}" stop-opacity=".28"/>'
          f'<stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient></defs>',
          f'<rect x="206" y="96" width="100" height="320" rx="18" fill="{RED}"/>',
          f'<rect x="96" y="206" width="320" height="100" rx="18" fill="{RED}"/>',
          # branch: trunk down the vertical bar, a branch off to the right arm
          f'<g fill="none" stroke="{INK50}" stroke-width="14" stroke-linecap="round">'
          f'<line x1="256" y1="136" x2="256" y2="376"/><path d="M256 330 C256 280 300 256 350 256"/></g>',
          f'<g fill="{BG}" stroke="{INK50}" stroke-width="12"><circle cx="256" cy="136" r="20"/>'
          f'<circle cx="256" cy="376" r="20"/><circle cx="356" cy="256" r="20"/></g>')
    return c.svg(512, 512, "Git Hospital logo: a red cross with a git branch", "")


# ---------------------------------------------------------------- pathway: how the wards fit together

STATIONS = [  # name, two lines on what happens there, the tools or outputs that do it
    ("SYMPTOM", ("Day two breaks: an upgrade,", "a 503, a repo nobody trusts"), ()),
    ("TRIAGE", ("Match the symptom", "to the ward that treats it"), ("triage desk",)),
    ("DIAGNOSIS", ("Reproduce it: a throwaway", "cluster, telemetry or git"), ("Helmbulance", "MeshMedic", "GitHealthCheck")),
    ("EVIDENCE", ("Commands, events, measures,", "or null with the reason"), ("Markdown", "JSON", "SARIF")),
    ("TREATMENT", ("A fix a person reviews:", "a patch or a pull request"), ("MeshMedic", "Helmbulance")),
    ("SECOND OPINION", ("Score the tools on known", "defects and clean twins"), ("boards",)),
]


def pathway() -> str:
    W, H, base = 1200, 400, 178
    c = Canvas()
    xs = [110 + i * 196 for i in range(len(STATIONS))]
    # a flat line with one heartbeat between each pair of stations
    blip = [(0, 0), (8, -5), (14, 0), (20, 0), (24, 7), (29, -34), (34, 14), (38, 0)]
    pts = [(48, base)]
    for a, b in zip(xs, xs[1:]):
        mid = (a + b) / 2 - 19
        pts += [(a, base)] + [(mid + dx, base + dy) for dx, dy in blip]
    pts += [(xs[-1], base), (W - 48, base)]
    path = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    run = [0.0]  # distance along the line to each point
    for p, q in zip(pts, pts[1:]):
        run.append(run[-1] + math.dist(p, q))
    length, cycle = math.ceil(run[-1]), 7.0
    at = {x: run[pts.index((x, base))] for x in xs}

    c.add("<defs>", GLOW_FILTER,
          '<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse">'
          f'<path d="M24 0H0V24" fill="none" stroke="{GREEN}" stroke-opacity=".05"/></pattern>',
          f'<radialGradient id="halo"><stop offset="0" stop-color="{GREEN}" stop-opacity=".45"/>'
          f'<stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></radialGradient>',
          "</defs>",
          f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="22" fill="#1d1916" stroke="{BORDER}"/>',
          f'<rect x="16" y="16" width="{W - 32}" height="{H - 32}" rx="14" fill="#060807"/>',
          f'<rect x="16" y="16" width="{W - 32}" height="{H - 32}" rx="14" fill="url(#grid)"/>')
    c.text(48, 58, "lbl", "PATIENT PATHWAY", "mono")
    c.text(48, 100, "head", "From a symptom to a fix you can review", "display")
    c.text(W - 48, 58, "lbl", "EVERY STEP LEAVES EVIDENCE", "mono", text_anchor="end")

    c.add(f'<path d="{path}" fill="none" stroke="{GREEN}" stroke-opacity=".18" stroke-width="2" stroke-linejoin="round"/>',
          f'<path class="pulse" d="{path}" fill="none" stroke="{GREEN}" stroke-width="2.5" stroke-linejoin="round" '
          f'stroke-linecap="round" filter="url(#neon)"/>')
    for i, (x, (name, lines, chips)) in enumerate(zip(xs, STATIONS)):
        delay = cycle * at[x] / (length + 140)  # light up as the head of the pulse arrives
        c.add(f'<circle class="halo" style="animation-delay:{delay:.2f}s" cx="{x}" cy="{base}" r="34" fill="url(#halo)"/>',
              f'<circle cx="{x}" cy="{base}" r="17" fill="#060807" stroke="{GREEN}" stroke-opacity=".55" stroke-width="2"/>',
              f'<circle class="node" style="animation-delay:{delay:.2f}s" cx="{x}" cy="{base}" r="17" fill="none" '
              f'stroke="{GREEN}" stroke-width="2.5" filter="url(#neon)"/>')
        c.text(x, base + 5, "num", f"{i + 1:02d}", "mono", text_anchor="middle")
        c.text(x, base + 52, "stn", name, "mono", text_anchor="middle")
        for k, line in enumerate(lines):
            c.text(x, base + 76 + k * 18, "desc", line, "sans4", text_anchor="middle")
        for k, chip in enumerate(chips):
            w = 18 + 7.8 * len(chip)
            y = base + 112 + k * 28
            c.add(f'<rect x="{x - w / 2:.1f}" y="{y}" width="{w:.1f}" height="21" rx="10.5" fill="{GREEN}" '
                  f'fill-opacity=".08" stroke="{GREEN}" stroke-opacity=".35"/>')
            c.text(x, y + 15, "chip", chip, "mono", text_anchor="middle")

    css = f"""
.lbl  {{ font: 500 12px 'Mono', monospace; fill: {MUTED}; letter-spacing: 1.6px; }}
.head {{ font: 600 30px 'Display', Georgia, serif; fill: {INK50}; letter-spacing: -.3px; }}
.num  {{ font: 500 12px 'Mono', monospace; fill: {GREEN}; }}
.stn  {{ font: 500 13px 'Mono', monospace; fill: {INK50}; letter-spacing: 1.6px; }}
.desc {{ font: 400 13.5px 'Sans', 'Helvetica Neue', Arial, sans-serif; fill: {INK400}; }}
.chip {{ font: 500 12px 'Mono', monospace; fill: {INK200}; }}
.pulse {{ stroke-dasharray: 140 {length}; animation: travel {cycle}s linear infinite; }}
.node  {{ opacity: 0; animation: node {cycle}s ease-out infinite; }}
.halo  {{ opacity: 0; animation: node {cycle}s ease-out infinite; }}
@keyframes travel {{ from {{ stroke-dashoffset: 140; }} to {{ stroke-dashoffset: -{length}; }} }}
@keyframes node {{ 0% {{ opacity: 1; }} 18% {{ opacity: 0; }} 100% {{ opacity: 0; }} }}
@media (prefers-reduced-motion: reduce) {{ .node {{ opacity: 1; }} .pulse {{ stroke-dasharray: none; }} }}
"""
    label = ("Patient pathway, from a symptom to a fix you can review: " + "; ".join(
        f"{i + 1}. {name.lower()}: {' '.join(lines)}" + (f" ({', '.join(chips)})" if chips else "")
        for i, (name, lines, chips) in enumerate(STATIONS)) + ".")
    return c.svg(W, H, label, css)


# ---------------------------------------------------------------- vitals: one patient monitor per tool

def api(path, token, tries=4):
    """GET one API page; retries network errors and 5xx with backoff."""
    req = urllib.request.Request(f"https://api.github.com/{path}",
                                 headers={"Accept": "application/vnd.github+json", "User-Agent": "git-hospital-vitals"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r), r.headers.get("Link", "")
        except urllib.error.HTTPError as e:
            if e.code < 500 or attempt == tries - 1:
                raise
        except urllib.error.URLError:
            if attempt == tries - 1:
                raise
        time.sleep(2 ** attempt * 3)


def paged(path, token, key=None, cap=1000):
    """Items of a list endpoint, 100 per page, at most `cap`."""
    items, page = [], 1
    while len(items) < cap:
        body, link = api(f"{path}{'&' if '?' in path else '?'}per_page=100&page={page}", token)
        items += body[key] if key else body
        if 'rel="next"' not in link:
            break
        page += 1
    return items


PASSED = {"success", "neutral", "skipped"}
IGNORED = {"cancelled", "stale"}  # superseded runs say nothing about the commit


def vitals_of(repo, token, now):
    meta, _ = api(f"repos/{ORG}/{repo}", token)
    branch = meta["default_branch"]
    since = (now - dt.timedelta(days=PULSE_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    pulse = len(paged(f"repos/{ORG}/{repo}/commits?sha={branch}&since={since}", token))
    head, _ = api(f"repos/{ORG}/{repo}/commits/{branch}", token)
    last = dt.datetime.fromisoformat(head["commit"]["committer"]["date"].replace("Z", "+00:00"))
    runs = paged(f"repos/{ORG}/{repo}/commits/{head['sha']}/check-runs", token, key="check_runs")
    states = [r["conclusion"] if r["status"] == "completed" else "running" for r in runs]
    states = [st for st in states if st not in IGNORED]
    if not states:
        checks = "NONE"
    elif any(st != "running" and st not in PASSED for st in states):
        checks = "FAIL"
    elif "running" in states:
        checks = "RUNNING"
    else:
        checks = "PASS"
    releases = [r for r in paged(f"repos/{ORG}/{repo}/releases", token, cap=100) if not r["draft"]]
    release = releases[0]["tag_name"] if releases else None
    prs = len(paged(f"repos/{ORG}/{repo}/pulls?state=open", token))
    return {
        "pulse": pulse, "checks": checks, "release": release, "last": last,
        "stars": meta["stargazers_count"], "issues": max(0, meta["open_issues_count"] - prs), "prs": prs,
        "language": meta["language"] or "", "license": (meta.get("license") or {}).get("spdx_id") or "",
    }


def ago(then, now) -> str:
    days = (now - then).days
    if days == 0:
        return "today"
    return "1 day ago" if days == 1 else f"{days} days ago"


def ecg(x0, x1, base, beats) -> str:
    """Flat line with `beats` evenly spaced heartbeats (none = flatline)."""
    shape = [(0, 0), (10, -6), (18, 0), (26, 0), (30, 8), (36, -46), (42, 18), (47, 0), (60, 0), (70, -10), (82, 0)]
    pts = [(x0, base)]
    for k in range(beats):
        bx = x0 + (x1 - x0) * (k + .5) / beats - 41
        pts += [(bx + dx, base + dy) for dx, dy in shape]
    pts.append((x1, base))
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)


def monitor(index, name, bed, desc, v, now) -> str:
    W, H = 600, 360
    c = Canvas()
    dormant = v["pulse"] == 0
    if v["checks"] == "FAIL":
        status, s_fill, s_ink = "CRITICAL", RED, INK50
    elif dormant:
        status, s_fill, s_ink = "DORMANT", INK600, INK50
    elif v["checks"] == "PASS":
        status, s_fill, s_ink = "STABLE", GREEN, "#06210f"
    elif v["checks"] == "RUNNING":
        status, s_fill, s_ink = "PENDING", AMBER, "#2a1a05"
    else:
        status, s_fill, s_ink = "NO CHECKS", INK600, INK50
    trace = RED if status == "CRITICAL" else (INK400 if dormant else GREEN)
    beats = 0 if v["pulse"] == 0 else 1 if v["pulse"] <= 5 else 2 if v["pulse"] <= 20 else 3 if v["pulse"] <= 60 else 4
    path = ecg(36, 392, 176, beats)
    nums = [tuple(map(float, q.split())) for q in path[1:].split(" L")]
    length = math.ceil(sum(math.dist(a, b) for a, b in zip(nums, nums[1:]))) + 4

    c.add("<defs>", GLOW_FILTER,
          '<pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">'
          f'<path d="M20 0H0V20" fill="none" stroke="{GREEN}" stroke-opacity=".06"/></pattern>',
          "</defs>",
          f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="22" fill="#1d1916" stroke="{BORDER}"/>',
          f'<rect x="16" y="16" width="{W - 32}" height="270" rx="12" fill="#060807"/>',
          f'<rect x="16" y="16" width="{W - 32}" height="270" rx="12" fill="url(#grid)"/>',
          f'<line x1="408" y1="34" x2="408" y2="240" stroke="{GREEN}" stroke-opacity=".15"/>',
          f'<line x1="36" y1="248" x2="{W - 36}" y2="248" stroke="{GREEN}" stroke-opacity=".15"/>')
    c.text(36, 46, "lbl", bed, "mono")
    chip_w = 14 + 8.4 * len(status)
    c.add(f'<rect class="{"alarm" if status == "CRITICAL" else ""}" x="{392 - chip_w}" y="31" width="{chip_w:.0f}" height="21" rx="4" fill="{s_fill}"/>')
    c.text(392 - chip_w / 2, 46, "chip", status, "mono", text_anchor="middle", fill=s_ink)
    c.text(36, 100, "name", name, "display")

    c.add(f'<path d="{path}" fill="none" stroke="{trace}" stroke-opacity=".16" stroke-width="2.5" stroke-linejoin="round"/>',
          f'<path class="{"trace" if beats else ""}" d="{path}" fill="none" stroke="{trace}" stroke-width="2.5" '
          f'stroke-linejoin="round" stroke-linecap="round" filter="url(#neon)"/>')

    def vital(y, label, value, unit, color):
        c.text(426, y, "lbl", label, "mono")
        size = min(30, int(146 / (.6 * len(value))))  # keep long tags inside the 150 px column
        c.text(426, y + 32, "big", value, "mono", fill=color, style=f"font-size:{size}px")
        if unit:
            c.text(426, y + 48, "unit", unit, "mono")

    vital(46, "PULSE", str(v["pulse"]), f"commits / {PULSE_DAYS} d", trace)
    check_col = {"PASS": GREEN, "FAIL": RED, "RUNNING": AMBER}.get(v["checks"], INK400)  # NONE stays grey
    vital(124, "CHECKS", v["checks"], "on latest commit", check_col)
    vital(198, "RELEASE", v["release"] or "none", "", AMBER if v["release"] else INK400)

    meta = [f'stars {v["stars"]}', f'issues {v["issues"]}', f'PRs {v["prs"]}', f'last commit {ago(v["last"], now)}']
    meta += [s for s in (v["language"], v["license"]) if s]
    c.text(36, 272, "meta", "  ·  ".join(meta), "mono")

    c.text(26, 318, "desc", desc, "sans4")
    c.text(26, 342, "foot", f"checked {now:%Y-%m-%d %H:%M} UTC from the GitHub API", "mono")
    c.text(W - 26, 342, "foot", f"MONITOR {index:02d}", "mono", text_anchor="end")
    c.add(f'<circle class="led" cx="{W - 32}" cy="314" r="4" fill="{trace}" filter="url(#neon)"/>')

    css = f"""
.lbl  {{ font: 500 12px 'Mono', monospace; fill: {MUTED}; letter-spacing: 1.2px; }}
.chip {{ font: 500 12px 'Mono', monospace; letter-spacing: 1.4px; }}
.name {{ font: 600 40px 'Display', Georgia, serif; fill: {INK50}; letter-spacing: -.5px; }}
.big  {{ font: 500 30px 'Mono', monospace; }}
.unit {{ font: 500 11px 'Mono', monospace; fill: {MUTED}; }}
.meta {{ font: 500 12px 'Mono', monospace; fill: {MUTED}; }}
.desc {{ font: 400 16px 'Sans', 'Helvetica Neue', Arial, sans-serif; fill: {INK200}; }}
.foot {{ font: 500 11px 'Mono', monospace; fill: {INK600}; }}
.trace {{ stroke-dasharray: {length} {length}; animation: sweep 2.8s linear infinite; }}
.alarm {{ animation: alarm 1s steps(1) infinite; }}
.led   {{ animation: alarm 2s steps(1) infinite; }}
@keyframes sweep {{ from {{ stroke-dashoffset: {length}; }} to {{ stroke-dashoffset: -{length}; }} }}
@keyframes alarm {{ 50% {{ opacity: .35; }} }}
"""
    label = (f"Patient monitor for {name} ({bed}): status {status}; pulse {v['pulse']} commits in the last "
             f"{PULSE_DAYS} days; checks {v['checks']}; release {v['release'] or 'none'}; " + ", ".join(meta) +
             f". {desc}. Checked {now:%Y-%m-%d} from the GitHub API.")
    return c.svg(W, H, label, css)


# ---------------------------------------------------------------- case board: bugs found in public charts

# Each case was reproduced on kind before it went upstream. Status is read live from the upstream issue
# and pull request; `check` is the Helmbulance pull request that adds the check, while it is not merged.
# chart, what broke, finding, upstream repo, issue, fix pull request, Helmbulance pull request with the check
OURS = [
    ("SeaweedFS", "First upgrade restarts the filer and S3 gateway", "HB-UV-003", "seaweedfs/seaweedfs", 11719, 11720, None),
    ("JupyterHub", "First upgrade restarts the hub and the proxy", "HB-UV-003", "jupyterhub/zero-to-jupyterhub-k8s", 3996, 3997, None),
    ("Semaphore", "First upgrade restarts Semaphore", "HB-UV-003", "semaphoreui/charts", 34, 35, None),
    ("yugabyte", "Patch release changes a selector; upgrades fail", "HB-CU-001", "yugabyte/charts", 240, None, None),
    ("SeaweedFS", "Unquoted number or boolean in env fails install", "HB-SCAN-004", "seaweedfs/seaweedfs", None, 12137, 42),
    ("SeaweedFS", "Reinstall writes a new filer database password", "HB-RI-004", "seaweedfs/seaweedfs", None, 12138, 43),
]
CONFIRMED = [  # reported by others, reproduced with Helmbulance
    ("Jenkins", "Argo CD replaces the admin password on every sync", "HB-GR-001", "jenkinsci/helm-charts", 1026, None, None),
    ("docker-registry", "haSharedSecret changes on every upgrade", "HB-UV-001", "twuni/docker-registry.helm", 187, None, None),
    ("docker-registry-ui", "App version in the selector breaks upgrades", "HB-SCAN-001", "Joxit/helm-charts", None, 22, None),
    ("grafana", "Admin password changes on every upgrade", "HB-UV-001", "grafana/helm-charts", 10, 62, None),
]
CASE_STATUS = {  # label, fill, ink
    "FIXED": ("FIXED", GREEN, "#06210f"),
    "APPROVED": ("FIX APPROVED", AMBER, "#2a1a05"),
    "IN REVIEW": ("FIX IN REVIEW", BLUE, INK50),
    "REPORTED": ("REPORTED", INK600, INK50),
    "CLOSED": ("CLOSED", "#2a221d", INK400),
    "UNKNOWN": ("UNKNOWN", "#2a221d", INK400),  # the upstream lookup failed this time
}


def case_status(repo, issue, pr, token):
    """FIXED, APPROVED, IN REVIEW, REPORTED or CLOSED, from the fix pull request first, then the issue."""
    if pr:
        p, _ = api(f"repos/{repo}/issues/{pr}", token)
        if p["pull_request"].get("merged_at"):
            return "FIXED"
        if p["state"] == "open":
            latest = {}
            for r in paged(f"repos/{repo}/pulls/{pr}/reviews", token):
                if r["state"] in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED"):
                    latest[r["user"]["login"]] = r["state"]
            states = set(latest.values())
            return "APPROVED" if "APPROVED" in states and "CHANGES_REQUESTED" not in states else "IN REVIEW"
    if issue:
        i, _ = api(f"repos/{repo}/issues/{issue}", token)
        if i["state"] == "open":
            return "REPORTED"
        return "FIXED" if i.get("state_reason") == "completed" else "CLOSED"
    return "CLOSED"


def check_merged(pr, token):
    p, _ = api(f"repos/{ORG}/helmbulance/issues/{pr}", token)
    return bool(p["pull_request"].get("merged_at"))


def cases_of(token):
    """One failed lookup (a deleted or renamed repository, a 404) shows that case as UNKNOWN, so the
    board and the monitors are still drawn."""
    out = []
    for group, rows in (("ours", OURS), ("confirmed", CONFIRMED)):
        for chart, what, finding, repo, issue, pr, check in rows:
            try:
                status = case_status(repo, issue, pr, token)
            except (urllib.error.URLError, KeyError) as e:
                print(f"cases: {repo}#{pr or issue}: {e}")
                status = "UNKNOWN"
            try:
                pending = bool(check) and not check_merged(check, token)
            except (urllib.error.URLError, KeyError):
                pending = False
            out.append({"group": group, "chart": chart, "what": what, "finding": finding,
                        "ref": f"{repo.split('/')[0]}#{pr or issue}", "status": status, "pending": pending})
    return out


def caseboard(cases, now) -> str:
    W, row, top = 1200, 38, 176
    groups = [("REPORTED BY US", [k for k in cases if k["group"] == "ours"]),
              ("REPORTED BY OTHERS · REPRODUCED WITH HELMBULANCE", [k for k in cases if k["group"] == "confirmed"])]
    H = top + sum(36 + row * len(rows) for _, rows in groups) + 56
    c = Canvas()
    c.add("<defs>", GLOW_FILTER,
          f'<linearGradient id="scan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{GREEN}" stop-opacity="0"/>'
          f'<stop offset="1" stop-color="{GREEN}" stop-opacity=".07"/></linearGradient>',
          f'<clipPath id="screen"><rect x="16" y="16" width="{W - 32}" height="{H - 32}" rx="14"/></clipPath>',
          "</defs>",
          f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="22" fill="#1d1916" stroke="{BORDER}"/>',
          f'<rect x="16" y="16" width="{W - 32}" height="{H - 32}" rx="14" fill="#0b0908"/>',
          f'<g clip-path="url(#screen)"><rect class="scan" x="16" y="-120" width="{W - 32}" height="120" fill="url(#scan)"/></g>')
    c.text(48, 58, "lbl", "CASE BOARD · UPSTREAM", "mono")
    c.text(48, 100, "head", "Bugs found in public Helm charts", "display")
    c.text(48, 128, "sub", "Every case was reproduced with Helmbulance before it was listed.", "sans4")

    fixed = sum(k["status"] == "FIXED" for k in cases if k["group"] == "ours")
    review = sum(k["status"] in ("APPROVED", "IN REVIEW") for k in cases)
    tallies = [("CASES", len(cases), INK50), ("REPORTED BY US", len(groups[0][1]), INK50),
               ("FIX IN REVIEW", review, AMBER), ("OUR FIXES MERGED", fixed, GREEN)]
    for i, (label, n, col) in enumerate(reversed(tallies)):
        x = W - 48 - i * 175
        c.text(x, 58, "lbl", label, "mono", text_anchor="end")
        c.text(x, 104, "big", str(n), "mono", text_anchor="end", fill=col)

    y = top
    for title, rows in groups:
        c.add(f'<line x1="48" y1="{y}" x2="{W - 48}" y2="{y}" stroke="{BORDER}"/>')
        c.text(48, y + 24, "lbl", title, "mono")
        y += 36
        for k in rows:
            label, fill, ink = CASE_STATUS[k["status"]]
            mid = y + row / 2
            if k["status"] != "FIXED":
                c.add(f'<circle class="led" cx="56" cy="{mid}" r="4" fill="{fill}" filter="url(#neon)" '
                      f'style="animation-delay:-{(y % 7) / 3:.2f}s"/>')
            else:
                c.add(f'<circle cx="56" cy="{mid}" r="4" fill="{fill}"/>')
            c.add(f'<rect x="72" y="{mid - 11}" width="128" height="22" rx="4" fill="{fill}" fill-opacity=".9"/>')
            c.text(136, mid + 4.5, "pill", label, "mono", text_anchor="middle", fill=ink)
            c.text(222, mid + 5, "chart", k["chart"], "sans5")
            c.text(392, mid + 5, "what", k["what"], "sans4")
            c.text(786, mid + 4.5, "find", k["finding"], "mono")
            if k["pending"]:
                c.text(786 + 8.4 * len(k["finding"]) + 8, mid + 4.5, "note", "check in review", "mono")
            c.text(W - 48, mid + 4.5, "ref", k["ref"], "mono", text_anchor="end")
            c.add(f'<line x1="72" y1="{y + row}" x2="{W - 48}" y2="{y + row}" stroke="{BORDER}" stroke-opacity=".45"/>')
            y += row
    c.text(48, H - 34, "foot", f"checked {now:%Y-%m-%d %H:%M} UTC from the GitHub API", "mono")
    c.text(W - 48, H - 34, "foot", "details: github.com/Git-Hospital/helmbulance#found-in-public-charts", "mono", text_anchor="end")

    css = f"""
.lbl   {{ font: 500 12px 'Mono', monospace; fill: {MUTED}; letter-spacing: 1.6px; }}
.head  {{ font: 600 30px 'Display', Georgia, serif; fill: {INK50}; letter-spacing: -.3px; }}
.sub   {{ font: 400 15px 'Sans', 'Helvetica Neue', Arial, sans-serif; fill: {INK400}; }}
.big   {{ font: 500 36px 'Mono', monospace; }}
.pill  {{ font: 500 11px 'Mono', monospace; letter-spacing: 1.2px; }}
.chart {{ font: 500 15px 'Sans', 'Helvetica Neue', Arial, sans-serif; fill: {INK50}; }}
.what  {{ font: 400 14.5px 'Sans', 'Helvetica Neue', Arial, sans-serif; fill: {INK200}; }}
.find  {{ font: 500 13px 'Mono', monospace; fill: {GREEN}; }}
.note  {{ font: 500 11px 'Mono', monospace; fill: {AMBER}; }}
.ref   {{ font: 500 13px 'Mono', monospace; fill: {INK400}; }}
.foot  {{ font: 500 11px 'Mono', monospace; fill: {INK600}; }}
.led   {{ animation: led 2.2s ease-in-out infinite; }}
.scan  {{ animation: scan 9s linear infinite; }}
@keyframes led  {{ 50% {{ opacity: .25; }} }}
@keyframes scan {{ from {{ transform: translateY(0); }} to {{ transform: translateY({H + 120}px); }} }}
"""
    label = ("Case board: bugs found in public Helm charts, each reproduced on a throwaway kind cluster. " +
             f"{len(cases)} cases, {len(groups[0][1])} reported by us, {review} with a fix in review, {fixed} of ours fixed upstream. " +
             " ".join(f"{k['chart']}: {k['what']} ({k['finding']}, {k['ref']}, {CASE_STATUS[k['status']][0].lower()})."
                      for k in cases) + f" Checked {now:%Y-%m-%d} from the GitHub API.")
    return c.svg(W, H, label, css)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=("hero", "vitals"))
    ap.add_argument("--out", type=Path, default=ASSETS)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if args.what == "hero":
        files = {"hospital.svg": hero(), "logo.svg": logo(), "pathway.svg": pathway()}
    else:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
        now = dt.datetime.now(dt.timezone.utc)
        files = {f"{repo}.svg": monitor(i + 1, name, bed, desc, vitals_of(repo, token, now), now)
                 for i, (repo, name, bed, desc) in enumerate(WARDS)}
        files["cases.svg"] = caseboard(cases_of(token), now)
    for fname, content in files.items():
        (args.out / fname).write_text(content)
        print(f"{args.out / fname}  {len(content) // 1024} KB")


if __name__ == "__main__":
    main()
