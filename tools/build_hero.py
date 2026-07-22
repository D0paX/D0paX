# -*- coding: utf-8 -*-
"""
Generates dark.svg / light.svg -- an animated GitHub profile hero.
Pure SMIL, no JS, no external assets. Single source of truth for both themes.
"""
import math, random, os, io, base64

W, H = 1180, 610
# write the SVGs into the repo root, one level up from tools/
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------------------------------
# AVATAR
# --------------------------------------------------------------------------
# Crop window measured against the 940x1672 source portrait. Landmarks, in source
# pixels: hair peak y=386 (at x=456), chin y=795, eye midpoint (420, 597).
#
# Centred on the FACE, not on the frame and not on the head silhouette.
#
# Tuned by measurement rather than by eye: segment skin pixels between the hairline
# (y=470) and the chin (y=795), take their centroid, and drive that centroid onto
# the circle centre. Earlier windows left it well off-centre, which is exactly what
# read as "wrong" on the card:
#     cx=412  ->  face centroid +52px right of centre
#     cx=426  ->  +34px  (better, still visibly right and low)
#     cx=460  ->   +8px  (this window)
#
# The head is turned, so more cheek is visible on one side; the face's optical
# centre therefore sits well right of both the eye midline (x=420) and the hair
# silhouette centre (x=412). Centring on either of those is what pushed the face
# off-centre in the first place.
#
# 505px square: a 12% zoom over the original 565px window, with the eye line at
# ~44% of the circle and ~11px between the hair peak (y=386 at x=456) and the mask
# edge. Below ~500px that gap closes and the hairline starts to read as clipped.
AVATAR_SRC   = os.path.join(OUT, "shrisht.png")
AVATAR_CACHE = os.path.join(HERE, "avatar.b64.txt")
AVATAR_BOX   = (207, 373, 712, 878)
AVATAR_PX    = 460      # covers the 164px disc at 3x DPR in a README (~371px
                        # needed); stays a downscale from the 505px crop
AVATAR_Q     = 86

def avatar_uri():
    """Crop + downscale + inline the portrait. Falls back to the cached data URI
    so the build still works if the 1.9 MB original is moved or Pillow is absent."""
    if os.path.exists(AVATAR_SRC):
        try:
            from PIL import Image
        except ImportError:
            Image = None
        if Image is not None:
            im = (Image.open(AVATAR_SRC).convert("RGB")
                  .crop(AVATAR_BOX).resize((AVATAR_PX, AVATAR_PX), Image.LANCZOS))
            buf = io.BytesIO()
            im.save(buf, format="JPEG", quality=AVATAR_Q, optimize=True, progressive=True)
            uri = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
            with open(AVATAR_CACHE, "w", encoding="utf-8") as f:
                f.write(uri)
            return uri
    if os.path.exists(AVATAR_CACHE):
        return open(AVATAR_CACHE, encoding="utf-8").read().strip()
    raise SystemExit("avatar source missing: expected shrisht.png in the repo root "
                     "or a cached tools/avatar.b64.txt")

AVATAR = avatar_uri()

UI   = "-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Roboto,'Helvetica Neue',Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def n(v):
    """compact number"""
    if isinstance(v, float):
        s = f"{v:.4f}".rstrip("0").rstrip(".")
        return s if s else "0"
    return str(v)

# --------------------------------------------------------------------------
# THEMES
# --------------------------------------------------------------------------
DARK = dict(
    key="dark", pfx="d",
    bg="#030712", bg2="#070D1C",
    panel="#0F172A", panel2="#0B1120",
    panelOp=.72, panelOp2=.52,
    stroke="#FFFFFF", strokeOp=.09,
    hi="#FFFFFF", hiOp=.18,
    text="#F8FAFC", sub="#CBD5E1", muted="#94A3B8", dim="#64748B",
    a1="#7C3AED", a2="#22D3EE", a3="#10B981", aLite="#A5F3FC",
    glowOp=.34, orbOp=.26,
    noiseOp=.05, gridOp=.032, gridCol="#FFFFFF",
    partCol="#CBD5E1", partOp=.6,
    shadow="#000000", shadowOp=.55,
    scanCol="#FFFFFF", scanOp=.06,
    reflCol="#FFFFFF", reflOp=.05,
    pillFill="#FFFFFF", pillFillOp=.05, pillStrokeOp=.15, haloOp=.18,
    barCol="#FFFFFF", barOp=.035,
    monoBg1="#1E293B", monoBg2="#0F172A",
    ringBase=.10, rimCol="#FFFFFF", rimOp=.16,
)
LIGHT = dict(
    key="light", pfx="l",
    bg="#FFFFFF", bg2="#F1F5F9",
    panel="#F8FAFC", panel2="#FFFFFF",
    panelOp=.88, panelOp2=.72,
    stroke="#0F172A", strokeOp=.10,
    hi="#FFFFFF", hiOp=.95,
    text="#0F172A", sub="#334155", muted="#475569", dim="#64748B",
    a1="#2563EB", a2="#06B6D4", a3="#10B981", aLite="#0EA5E9",
    glowOp=.17, orbOp=.14,
    noiseOp=.03, gridOp=.055, gridCol="#0F172A",
    partCol="#2563EB", partOp=.32,
    shadow="#0F172A", shadowOp=.14,
    scanCol="#2563EB", scanOp=.045,
    reflCol="#FFFFFF", reflOp=.6,
    pillFill="#FFFFFF", pillFillOp=.9, pillStrokeOp=.16, haloOp=.11,
    barCol="#0F172A", barOp=.028,
    monoBg1="#E2E8F0", monoBg2="#F1F5F9",
    ringBase=.14, rimCol="#0F172A", rimOp=.14,
)

# --------------------------------------------------------------------------
# CONTENT
# --------------------------------------------------------------------------
PHRASES = [
    "AI Systems Engineer",
    "Building Aether AI OS",
    "Full Stack Engineer",
    "AI Agent Architect",
    "Cloudflare Edge Developer",
]
BUILDING = ["Aether AI OS", "AI Agent Platform", "Enterprise Applications"]
FOCUS    = ["AI Systems", "Cloudflare Workers", "Production Infrastructure", "AI Agents"]
SKILL_ROWS = [
    ["Python", "FastAPI", "TypeScript", "React", "Next.js", "Tailwind CSS"],
    ["Cloudflare Workers", "Docker", "Git", "PostgreSQL", "Turso"],
    ["OpenAI", "Gemini", "Claude", "Pydantic", "Playwright"],
]
ASCII_ART = [
    "  ·   ·   ·   ·  ",
    "╭───────────────╮",
    "│  ▁▂▃▅▇█▇▅▃▂▁  │",
    "│               │",
    "│   •───•───•   │",
    "│   │ \\ │ / │   │",
    "│   •──[█]──•   │",
    "│   │ / │ \\ │   │",
    "│   •───•───•   │",
    "│               │",
    "╰───────────────╯",
    "  ·   ·   ·   ·  ",
]
# monospace art only aligns if every row has an identical advance count
_w = {len(l) for l in ASCII_ART}
assert len(_w) == 1, f"ASCII rows must be equal width, got {sorted(_w)}"

# --------------------------------------------------------------------------
# GEOMETRY
# --------------------------------------------------------------------------
LP  = dict(x=24, y=24, w=430, h=562)          # left panel
TP  = dict(x=474, y=24, w=682, h=386)         # terminal panel
SP  = dict(x=474, y=426, w=682, h=160)        # skills panel
TX  = 500                                     # terminal content left
TXR = 1130                                    # terminal content right
ASC = dict(x=966, y=210, w=166, h=186)        # ascii panel

# --------------------------------------------------------------------------
# LEFT COLUMN RHYTHM
# --------------------------------------------------------------------------
# The portrait is the panel's hero, so the whole column is derived from its
# radius rather than hand-placed. AVK scales every satellite of the avatar
# (ring, glow, reflection, stroke weights, float travel) off the original
# 140px component, so the assembly grows as one object instead of a big disc
# wearing thin rings sized for a smaller one.
AV_R   = 82                                   # 164px disc, ~15% down from 192px, so
AVK    = AV_R / 70.0                          # the name carries the panel instead
AV_TOP = LP["y"] + 34
AV  = dict(cx=LP["x"] + LP["w"] // 2, cy=AV_TOP + AV_R, r=AV_R)

NAME_Y     = AV["cy"] + AV_R + 60             # was +46: more air under the portrait
USER_Y     = NAME_Y + 24
PILL_Y     = USER_Y + 13
PILL_H     = 26                               # compact role badge
RULE_Y     = PILL_Y + PILL_H + 18
INFO_Y     = RULE_Y + 16
INFO_PITCH = 35
CHIP_Y     = INFO_Y + 4 * INFO_PITCH + 12
CHIP_H     = 36

assert CHIP_Y + CHIP_H <= LP["y"] + LP["h"] - 6, "left column overflows its panel"

# typing metrics
ADV   = 11.4
CYCLE = 25.0

# --------------------------------------------------------------------------
# ANIMATION HELPERS
# --------------------------------------------------------------------------
EASE = ".33 0 .12 1"          # apple-ish ease-out
SOFT = ".45 0 .55 1"          # sine in-out

# Reveals deliberately start at begin="0s" and encode their stagger as a flat leading
# segment in keyTimes, rather than using begin="<delay>s". That lets every revealed
# element keep a *static* opacity of 1, so a renderer with no SMIL support (resvg,
# librsvg, some OpenGraph rasterisers) shows the finished composition instead of a
# blank card. With begin-delays and opacity="0" bases, the whole hero would vanish.
def _staged(delay, dur, extra=""):
    total = delay + dur
    return round(delay / total, 5), total, extra

def reveal(delay, dur=.9, dy=10):
    """fade + rise, plays once and freezes"""
    k, total, _ = _staged(delay, dur)
    return (f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{n(k)};1" '
            f'dur="{n(total)}s" calcMode="spline" keySplines="0 0 1 1;{EASE}" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 {n(dy)};0 {n(dy)};0 0" keyTimes="0;{n(k)};1" dur="{n(total)}s" '
            f'calcMode="spline" keySplines="0 0 1 1;{EASE}" fill="freeze"/>')

def fade(delay, dur=.6):
    """opacity-only reveal, same static-safe staging as reveal()"""
    k, total, _ = _staged(delay, dur)
    return (f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{n(k)};1" '
            f'dur="{n(total)}s" calcMode="spline" keySplines="0 0 1 1;{EASE}" fill="freeze"/>')

def float_y(amp, dur, begin=0.0):
    return (f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;0 {n(-amp)};0 0" dur="{n(dur)}s" begin="{n(begin)}s" '
            f'calcMode="spline" keySplines="{SOFT};{SOFT}" repeatCount="indefinite"/>')

def pulse(attr, a, b, dur, begin=0.0):
    return (f'<animate attributeName="{attr}" values="{n(a)};{n(b)};{n(a)}" dur="{n(dur)}s" '
            f'begin="{n(begin)}s" calcMode="spline" keySplines="{SOFT};{SOFT}" repeatCount="indefinite"/>')

# --------------------------------------------------------------------------
# TYPING TIMELINE
# --------------------------------------------------------------------------
def typing_steps():
    """-> [(t_seconds, char_count)] across the full 25s loop"""
    steps = [(0.0, 0)]
    for i, p in enumerate(PHRASES):
        ln = len(p)
        s = i * 5.0 + .25
        for k in range(0, ln + 1):
            steps.append((s + k * 1.5 / ln, k))
        m = math.ceil(ln / 2)
        for j in range(1, m + 1):
            steps.append((s + 3.5 + j * .8 / m, max(0, ln - round(ln * j / m))))
    return steps

def steps_anim(attr, steps, fn):
    kt = ";".join(n(round(t / CYCLE, 5)) for t, _ in steps)
    vs = ";".join(n(fn(c)) for _, c in steps)
    return (f'<animate attributeName="{attr}" calcMode="discrete" dur="{n(CYCLE)}s" '
            f'repeatCount="indefinite" keyTimes="{kt}" values="{vs}"/>')

# --------------------------------------------------------------------------
# ICONS  (16x16 grid)
# --------------------------------------------------------------------------
IC_GITHUB = ('<path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49'
             '-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82'
             '.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15'
             '-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82'
             '.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07'
             '-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z" fill="CC"/>')
IC_LINKEDIN = ('<path d="M2.6 6.1h2.6V14H2.6zM3.9 2.2a1.55 1.55 0 1 1 0 3.1 1.55 1.55 0 0 1 0-3.1zM7.1 6.1h2.5v1.08h.04'
               'c.35-.66 1.2-1.36 2.47-1.36 2.64 0 3.13 1.7 3.13 3.92V14h-2.6v-3.47c0-.83 0-1.9-1.16-1.9-1.16 0-1.34.9'
               '-1.34 1.84V14H7.1z" fill="CC"/>')
IC_GLOBE = ('<g fill="none" stroke="CC" stroke-width="1.35" stroke-linecap="round">'
            '<circle cx="8" cy="8" r="6.6"/><ellipse cx="8" cy="8" rx="3.05" ry="6.6"/>'
            '<path d="M1.75 5.9h12.5M1.75 10.1h12.5"/></g>')
IC_MAIL = ('<g fill="none" stroke="CC" stroke-width="1.35" stroke-linejoin="round" stroke-linecap="round">'
           '<rect x="1.5" y="3.3" width="13" height="9.4" rx="2"/><path d="M2.5 5.3 8 9.15l5.5-3.85"/></g>')
IC_PIN = ('<g fill="none" stroke="CC" stroke-width="1.35" stroke-linejoin="round">'
          '<path d="M8 14.6s5.1-4.7 5.1-8.1a5.1 5.1 0 1 0-10.2 0c0 3.4 5.1 8.1 5.1 8.1z"/>'
          '<circle cx="8" cy="6.4" r="1.95"/></g>')
IC_CAP = ('<g fill="none" stroke="CC" stroke-width="1.35" stroke-linejoin="round" stroke-linecap="round">'
          '<path d="M8 2.4 15 5.6 8 8.8 1 5.6z"/><path d="M4 7v3.6c0 1.05 1.79 1.9 4 1.9s4-.85 4-1.9V7"/>'
          '<path d="M14.6 6.1v3.5"/></g>')
IC_LINK = ('<g fill="none" stroke="CC" stroke-width="1.35" stroke-linecap="round">'
           '<path d="M6.6 9.4a2.75 2.75 0 0 0 4.15.3l2-2a2.75 2.75 0 0 0-3.89-3.89l-1.15 1.14"/>'
           '<path d="M9.4 6.6a2.75 2.75 0 0 0-4.15-.3l-2 2a2.75 2.75 0 0 0 3.89 3.89l1.14-1.14"/></g>')

def icon(path, color, x, y, scale=1.0, op=1.0):
    o = f' opacity="{n(op)}"' if op != 1.0 else ""
    tf = f'translate({n(x)} {n(y)})' + (f' scale({n(scale)})' if scale != 1.0 else "")
    return f'<g transform="{tf}"{o}>{path.replace("CC", color)}</g>'

# --------------------------------------------------------------------------
# BUILD
# --------------------------------------------------------------------------
def build(T):
    p = T["pfx"]
    def i(name): return f"{p}-{name}"
    def u(name): return f"url(#{p}-{name})"
    o = []
    a = o.append

    # ==================== DEFS ====================
    a('<defs>')

    # -- gradients ---------------------------------------------------------
    a(f'<linearGradient id="{i("bg")}" x1="0" y1="0" x2="1" y2="1">'
      f'<stop offset="0" stop-color="{T["bg"]}"/><stop offset="1" stop-color="{T["bg2"]}"/></linearGradient>')

    for name, col in (("o1", T["a1"]), ("o2", T["a2"]), ("o3", T["a3"])):
        a(f'<radialGradient id="{i(name)}"><stop offset="0" stop-color="{col}" stop-opacity="{n(T["glowOp"])}"/>'
          f'<stop offset=".55" stop-color="{col}" stop-opacity="{n(T["glowOp"]*.28)}"/>'
          f'<stop offset="1" stop-color="{col}" stop-opacity="0"/></radialGradient>')

    # accent sweep used for text / strokes
    a(f'<linearGradient id="{i("acc")}" x1="0" y1="0" x2="1" y2="0" gradientUnits="objectBoundingBox">'
      f'<stop offset="0" stop-color="{T["a1"]}"/><stop offset=".5" stop-color="{T["a2"]}"/>'
      f'<stop offset="1" stop-color="{T["a3"]}"/></linearGradient>')

    # moving accent gradient for the typed line
    a(f'<linearGradient id="{i("type")}" x1="480" y1="0" x2="900" y2="0" gradientUnits="userSpaceOnUse">'
      f'<stop offset="0" stop-color="{T["a1"]}"/><stop offset=".38" stop-color="{T["a2"]}"/>'
      f'<stop offset=".72" stop-color="{T["a3"]}"/><stop offset="1" stop-color="{T["a2"]}"/>'
      f'<animateTransform attributeName="gradientTransform" type="translate" values="-170 0;170 0;-170 0" '
      f'dur="9s" calcMode="spline" keySplines="{SOFT};{SOFT}" repeatCount="indefinite"/></linearGradient>')

    # name gradient (static-ish, gentle shift)
    a(f'<linearGradient id="{i("name")}" x1="0" y1="0" x2="1" y2="0">'
      f'<stop offset="0" stop-color="{T["text"]}"/><stop offset=".55" stop-color="{T["a2"]}"/>'
      f'<stop offset="1" stop-color="{T["a1"]}">'
      f'<animate attributeName="stop-color" values="{T["a1"]};{T["a3"]};{T["a1"]}" dur="12s" repeatCount="indefinite"/>'
      f'</stop></linearGradient>')

    # panel glass fill
    a(f'<linearGradient id="{i("glass")}" x1="0" y1="0" x2=".6" y2="1">'
      f'<stop offset="0" stop-color="{T["panel"]}" stop-opacity="{n(T["panelOp"])}"/>'
      f'<stop offset="1" stop-color="{T["panel2"]}" stop-opacity="{n(T["panelOp2"])}"/></linearGradient>')

    # thin top highlight for panels
    a(f'<linearGradient id="{i("edge")}" x1="0" y1="0" x2="1" y2="0">'
      f'<stop offset="0" stop-color="{T["hi"]}" stop-opacity="0"/>'
      f'<stop offset=".5" stop-color="{T["hi"]}" stop-opacity="{n(T["hiOp"])}"/>'
      f'<stop offset="1" stop-color="{T["hi"]}" stop-opacity="0"/></linearGradient>')

    # hairline divider
    a(f'<linearGradient id="{i("rule")}" x1="0" y1="0" x2="1" y2="0">'
      f'<stop offset="0" stop-color="{T["stroke"]}" stop-opacity="0"/>'
      f'<stop offset=".5" stop-color="{T["stroke"]}" stop-opacity="{n(T["strokeOp"]*1.6)}"/>'
      f'<stop offset="1" stop-color="{T["stroke"]}" stop-opacity="0"/></linearGradient>')

    # rotating border shimmer
    a(f'<linearGradient id="{i("shim")}" x1="0" y1="0" x2="1" y2="0" gradientUnits="objectBoundingBox">'
      f'<stop offset="0" stop-color="{T["a1"]}" stop-opacity="0"/>'
      f'<stop offset=".34" stop-color="{T["a1"]}" stop-opacity=".45"/>'
      f'<stop offset=".5" stop-color="{T["aLite"]}" stop-opacity=".8"/>'
      f'<stop offset=".66" stop-color="{T["a3"]}" stop-opacity=".45"/>'
      f'<stop offset="1" stop-color="{T["a2"]}" stop-opacity="0"/>'
      f'<animateTransform attributeName="gradientTransform" type="rotate" values="0 .5 .5;360 .5 .5" '
      f'dur="16s" repeatCount="indefinite"/></linearGradient>')

    # comet trail along the card border
    a(f'<linearGradient id="{i("comet")}" x1="0" y1="0" x2="1" y2="1">'
      f'<stop offset="0" stop-color="{T["a2"]}"/><stop offset=".5" stop-color="{T["aLite"]}"/>'
      f'<stop offset="1" stop-color="{T["a1"]}"/></linearGradient>')

    # avatar ring
    a(f'<linearGradient id="{i("ring")}" x1="0" y1="0" x2="1" y2="1">'
      f'<stop offset="0" stop-color="{T["a1"]}"/><stop offset=".45" stop-color="{T["a2"]}"/>'
      f'<stop offset="1" stop-color="{T["a3"]}"/></linearGradient>')

    # halved from .55: the glow was competing with the name for attention
    a(f'<radialGradient id="{i("avglow")}">'
      f'<stop offset=".62" stop-color="{T["a2"]}" stop-opacity="0"/>'
      f'<stop offset=".82" stop-color="{T["a2"]}" stop-opacity="{n(T["glowOp"]*.275)}"/>'
      f'<stop offset="1" stop-color="{T["a1"]}" stop-opacity="0"/></radialGradient>')

    # monogram fallback (shown if the photo href is not replaced)
    a(f'<linearGradient id="{i("mono")}" x1="0" y1="0" x2="1" y2="1">'
      f'<stop offset="0" stop-color="{T["monoBg1"]}"/><stop offset="1" stop-color="{T["monoBg2"]}"/></linearGradient>')

    # reflection under avatar
    a(f'<radialGradient id="{i("refl")}">'
      f'<stop offset="0" stop-color="{T["a2"]}" stop-opacity="{n(T["glowOp"]*.25)}"/>'
      f'<stop offset="1" stop-color="{T["a2"]}" stop-opacity="0"/></radialGradient>')

    # vertical scanline sweep
    a(f'<linearGradient id="{i("scan")}" x1="0" y1="0" x2="0" y2="1">'
      f'<stop offset="0" stop-color="{T["scanCol"]}" stop-opacity="0"/>'
      f'<stop offset=".5" stop-color="{T["scanCol"]}" stop-opacity="{n(T["scanOp"])}"/>'
      f'<stop offset="1" stop-color="{T["scanCol"]}" stop-opacity="0"/></linearGradient>')

    # diagonal glass reflection band
    a(f'<linearGradient id="{i("sheen")}" x1="0" y1="0" x2="1" y2="0">'
      f'<stop offset="0" stop-color="{T["reflCol"]}" stop-opacity="0"/>'
      f'<stop offset=".5" stop-color="{T["reflCol"]}" stop-opacity="{n(T["reflOp"])}"/>'
      f'<stop offset="1" stop-color="{T["reflCol"]}" stop-opacity="0"/></linearGradient>')

    # ascii gradient (cyan -> blue, animated)
    a(f'<linearGradient id="{i("ascii")}" x1="0" y1="0" x2="0" y2="1" gradientUnits="objectBoundingBox">'
      f'<stop offset="0" stop-color="{T["a2"]}"/><stop offset=".45" stop-color="{T["aLite"]}"/>'
      f'<stop offset="1" stop-color="{T["a1"]}"/>'
      f'<animateTransform attributeName="gradientTransform" type="translate" values="0 -.55;0 .55;0 -.55" '
      f'dur="11s" calcMode="spline" keySplines="{SOFT};{SOFT}" repeatCount="indefinite"/></linearGradient>')

    # radial fade mask for the grid
    a(f'<radialGradient id="{i("fade")}">'
      f'<stop offset="0" stop-color="#fff" stop-opacity="1"/>'
      f'<stop offset=".7" stop-color="#fff" stop-opacity=".35"/>'
      f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>')
    a(f'<mask id="{i("gridmask")}"><rect width="{W}" height="{H}" fill="{u("fade")}"/></mask>')

    # -- patterns ----------------------------------------------------------
    a(f'<pattern id="{i("grid")}" width="34" height="34" patternUnits="userSpaceOnUse">'
      f'<path d="M34 0H0v34" fill="none" stroke="{T["gridCol"]}" stroke-opacity="{n(T["gridOp"])}" '
      f'stroke-width="1"/></pattern>')

    a(f'<filter id="{i("nz")}" x="0" y="0" width="100%" height="100%">'
      f'<feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="3" stitchTiles="stitch" seed="7"/>'
      f'<feColorMatrix type="saturate" values="0"/></filter>')
    a(f'<pattern id="{i("noise")}" width="180" height="180" patternUnits="userSpaceOnUse">'
      f'<rect width="180" height="180" filter="url(#{i("nz")})"/></pattern>')

    # -- filters -----------------------------------------------------------
    a(f'<filter id="{i("shadow")}" x="-10%" y="-10%" width="120%" height="130%">'
      f'<feDropShadow dx="0" dy="10" stdDeviation="14" flood-color="{T["shadow"]}" '
      f'flood-opacity="{n(T["shadowOp"])}"/></filter>')
    a(f'<filter id="{i("soft")}" x="-30%" y="-25%" width="160%" height="150%">'
      f'<feGaussianBlur stdDeviation="3"/></filter>')

    # -- clips -------------------------------------------------------------
    a(f'<clipPath id="{i("card")}"><rect x="0" y="0" width="{W}" height="{H}" rx="24"/></clipPath>')
    a(f'<clipPath id="{i("avatar")}"><circle cx="{AV["cx"]}" cy="{AV["cy"]}" r="{AV["r"]}"/></clipPath>')
    a(f'<clipPath id="{i("term")}"><rect x="{TP["x"]}" y="{TP["y"]}" width="{TP["w"]}" height="{TP["h"]}" rx="18"/></clipPath>')
    a(f'<clipPath id="{i("asc")}"><rect x="{ASC["x"]}" y="{ASC["y"]}" width="{ASC["w"]}" height="{ASC["h"]}" rx="12"/></clipPath>')

    # typing reveal clip (one rect, shared by all phrases)
    steps = typing_steps()
    # static width reveals phrase 0 in full for no-SMIL renderers
    a(f'<clipPath id="{i("typeclip")}"><rect x="0" y="150" height="34" '
      f'width="{n(TX + round(len(PHRASES[0]) * ADV, 1))}">'
      + steps_anim("width", steps, lambda c: TX + round(c * ADV, 1))
      + '</rect></clipPath>')

    a('</defs>')

    # ==================== BACKGROUND ====================
    a(f'<g clip-path="url(#{i("card")})">')
    a(f'<rect width="{W}" height="{H}" fill="{u("bg")}"/>')

    # ambient orbs
    orbs = [
        ("o1", 210, 90, 330, 20.0, 26, 0.0),
        ("o2", 1010, 250, 380, 24.0, 30, 3.0),
        ("o3", 690, 600, 330, 28.0, 24, 6.0),
        ("o2", 120, 520, 260, 22.0, 22, 9.0),
    ]
    for gid, cx, cy, r, dur, amp, beg in orbs:
        a(f'<g opacity="{n(T["orbOp"])}">{pulse("opacity", T["orbOp"]*.7, T["orbOp"]*1.25, dur*.7, beg)}'
          f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{int(r*.78)}" fill="{u(gid)}">'
          f'<animateTransform attributeName="transform" type="translate" '
          f'values="0 0;{amp} {-amp*.6};{-amp*.5} {amp*.5};0 0" dur="{n(dur)}s" begin="{n(beg)}s" '
          f'calcMode="spline" keySplines="{SOFT};{SOFT};{SOFT}" repeatCount="indefinite"/></ellipse></g>')

    # grid
    a(f'<rect width="{W}" height="{H}" fill="{u("grid")}" mask="url(#{i("gridmask")})"/>')

    # particles
    rnd = random.Random(20260721)
    a('<g>')
    for k in range(18):
        px = rnd.uniform(20, W - 20)
        py = rnd.uniform(20, H - 20)
        pr = round(rnd.uniform(.9, 2.1), 2)
        dur = round(rnd.uniform(13, 26), 1)
        beg = round(rnd.uniform(0, 12), 1)
        dx = round(rnd.uniform(-26, 26), 1)
        dy = round(rnd.uniform(-34, -12), 1)
        op = round(T["partOp"] * rnd.uniform(.35, 1.0), 3)
        col = [T["partCol"], T["a2"], T["a1"], T["a3"]][k % 4]
        a(f'<circle cx="{n(px)}" cy="{n(py)}" r="{n(pr)}" fill="{col}" opacity="0">'
          f'<animate attributeName="opacity" values="0;{n(op)};{n(op*.6)};0" dur="{n(dur)}s" '
          f'begin="{n(beg)}s" repeatCount="indefinite"/>'
          f'<animateTransform attributeName="transform" type="translate" values="0 0;{n(dx)} {n(dy)}" '
          f'dur="{n(dur)}s" begin="{n(beg)}s" repeatCount="indefinite"/></circle>')
    a('</g>')

    # diagonal glass sheen
    a(f'<g opacity=".9"><rect x="-460" y="-160" width="300" height="930" fill="{u("sheen")}" '
      f'transform="rotate(18 590 305)">'
      f'<animateTransform attributeName="transform" type="translate" values="0 0;2100 0" '
      f'dur="13s" repeatCount="indefinite" additive="sum"/></rect></g>')

    # scanline sweep
    a(f'<rect x="0" y="0" width="{W}" height="150" fill="{u("scan")}">'
      f'<animateTransform attributeName="transform" type="translate" values="0 -170;0 {H+30}" '
      f'dur="10s" repeatCount="indefinite"/></rect>')

    # ==================== PANEL BODIES ====================
    a(f'<g filter="url(#{i("shadow")})">')
    for pn, rx in ((LP, 22), (TP, 18), (SP, 18)):
        a(f'<rect x="{pn["x"]}" y="{pn["y"]}" width="{pn["w"]}" height="{pn["h"]}" rx="{rx}" fill="{u("glass")}"/>')
    a('</g>')
    for pn, rx in ((LP, 22), (TP, 18), (SP, 18)):
        a(f'<rect x="{pn["x"]+.5}" y="{pn["y"]+.5}" width="{pn["w"]-1}" height="{pn["h"]-1}" rx="{rx}" '
          f'fill="none" stroke="{T["stroke"]}" stroke-opacity="{n(T["strokeOp"])}"/>')
        a(f'<rect x="{pn["x"]+rx}" y="{pn["y"]+.5}" width="{pn["w"]-rx*2}" height="1" fill="{u("edge")}"/>')

    # ==================== LEFT PANEL ====================
    a(f'<g>{reveal(.25, 1.0, 14)}')

    # avatar block (floats). Every offset and stroke weight is multiplied by AVK so
    # the ring, glow, reflection and float travel grow with the disc.
    RING_R = n(round(AV["r"] + 7 * AVK, 1))
    a(f'<g>{float_y(round(5 * AVK, 1), 7.5)}')
    a(f'<ellipse cx="{AV["cx"]}" cy="{n(round(AV["cy"] + AV["r"] + 8 * AVK, 1))}" '
      f'rx="{n(round(AV["r"] * .943, 1))}" ry="{n(round(9 * AVK, 1))}" fill="{u("refl")}" opacity=".7">'
      + pulse("opacity", .45, .8, 6.0) + '</ellipse>')
    a(f'<circle cx="{AV["cx"]}" cy="{AV["cy"]}" r="{n(round(AV["r"] + 22 * AVK, 1))}" '
      f'fill="{u("avglow")}">' + pulse("opacity", .55, 1.0, 5.5) + '</circle>')
    a(f'<circle cx="{AV["cx"]}" cy="{AV["cy"]}" r="{RING_R}" fill="none" stroke="{T["stroke"]}" '
      f'stroke-opacity="{n(T["ringBase"])}" stroke-width="{n(round(.8 * AVK, 2))}"/>')
    a(f'<circle cx="{AV["cx"]}" cy="{AV["cy"]}" r="{RING_R}" fill="none" stroke="{u("ring")}" '
      f'stroke-width="{n(round(1.25 * AVK, 2))}" stroke-linecap="round" pathLength="100" '
      f'stroke-dasharray="26 74">'
      f'<animate attributeName="stroke-dashoffset" values="100;0" dur="7s" repeatCount="indefinite"/></circle>')
    # neutral backdrop so the disc is never a transparent hole if the photo fails to decode
    a(f'<circle cx="{AV["cx"]}" cy="{AV["cy"]}" r="{AV["r"]}" fill="{u("mono")}"/>')
    a('<!-- Profile photo, inlined as a base64 JPEG. It has to be a data URI: GitHub\n'
      '     serves this SVG inside an <img>, and browsers block every external fetch\n'
      '     from that context, so a path or https:// URL would render nothing.\n'
      '     The source is already cropped square, so slice only fills, never crops\n'
      '     further and never distorts. Regenerate via tools/build_hero.py.\n'
      '     xlink:href alone is deliberate: every current browser still honours it\n'
      '     and older rasterisers accept nothing else, so one attribute covers both\n'
      '     without duplicating ~35 KB of base64 into a second attribute. -->')
    a(f'<image xlink:href="{AVATAR}" '
      f'x="{AV["cx"]-AV["r"]}" y="{AV["cy"]-AV["r"]}" width="{AV["r"]*2}" height="{AV["r"]*2}" '
      f'preserveAspectRatio="xMidYMid slice" clip-path="url(#{i("avatar")})"/>')
    # rim that separates the portrait from the panel. A white rim reads as a specular
    # edge on dark, but washes into a warm light-toned photo on the light theme, so
    # the colour flips with the theme rather than being shared.
    a(f'<circle cx="{AV["cx"]}" cy="{AV["cy"]}" r="{n(round(AV["r"] - .5 * AVK, 1))}" fill="none" '
      f'stroke="{T["rimCol"]}" stroke-opacity="{n(T["rimOp"])}" '
      f'stroke-width="{n(round(.8 * AVK, 2))}"/>')
    a('</g>')

    # name + handle
    a(f'<g>{reveal(.8, .9, 12)}'
      f'<text x="{AV["cx"]}" y="{NAME_Y}" text-anchor="middle" font-family="{UI}" font-size="35" '
      f'font-weight="700" letter-spacing="-.8" fill="{u("name")}">Shrisht</text></g>')
    a(f'<g>{reveal(.95, .9, 12)}'
      f'<text x="{AV["cx"]}" y="{USER_Y}" text-anchor="middle" font-family="{MONO}" font-size="13.5" '
      f'letter-spacing=".4" fill="{T["muted"]}">@D0paX</text></g>')

    # role pill
    pw = 224
    a(f'<g>{reveal(1.1, .9, 10)}')
    a(f'<rect x="{AV["cx"]-pw/2}" y="{PILL_Y}" width="{pw}" height="{PILL_H}" '
      f'rx="{n(PILL_H/2)}" fill="{T["a2"]}" fill-opacity="{n(T["haloOp"]*.55)}"/>')
    a(f'<rect x="{AV["cx"]-pw/2+.5}" y="{PILL_Y+.5}" width="{pw-1}" height="{PILL_H-1}" '
      f'rx="{n((PILL_H-1)/2)}" fill="none" stroke="{u("acc")}" stroke-opacity=".55" stroke-width="1"/>')
    a(f'<text x="{AV["cx"]}" y="{PILL_Y+17}" text-anchor="middle" font-family="{UI}" font-size="12" '
      f'font-weight="600" letter-spacing=".3" fill="{T["sub"]}">AI Systems Engineer '
      f'<tspan fill="{T["a2"]}">·</tspan> Founder</text>')
    a('</g>')

    a(f'<rect x="56" y="{RULE_Y}" width="366" height="1" fill="{u("rule")}"/>')

    # info rows
    rows = [
        (IC_PIN,  "LOCATION",  "India", T["sub"]),
        (IC_CAP,  "EDUCATION", "Bachelor of Computer Applications (BCA)", T["sub"]),
        (IC_LINK, "PORTFOLIO", "https://shrisht.space", T["a2"]),
        (IC_MAIL, "EMAIL",     "contact@shrisht.space", T["a2"]),
    ]
    for k, (ic, label, value, col) in enumerate(rows):
        ry = INFO_Y + k * INFO_PITCH
        a(f'<g>{reveal(1.25 + k * .13, .8, 8)}')
        a(icon(ic, T["muted"], 52, ry + 9, 1.0, .85))
        a(f'<text x="78" y="{ry+11}" font-family="{UI}" font-size="9" font-weight="600" '
          f'letter-spacing="1.4" fill="{T["dim"]}">{label}</text>')
        fam = MONO if k >= 2 else UI
        a(f'<text x="78" y="{ry+28}" font-family="{fam}" font-size="12.5" fill="{col}">{esc(value)}</text>')
        a('</g>')

    # social chips: LinkedIn, Website, Email. Purely visual, no anchors.
    # GitHub serves this SVG through an <img>, where SVG is inert -- links never
    # activate and pointer events never arrive. The interactive navigation is the
    # markdown link row directly under the banner in README.md; this row is its
    # visual echo. Geometry: 3 x 44 + 2 x 16 = 164 wide, centred on the panel axis.
    socials = [IC_LINKEDIN, IC_GLOBE, IC_MAIL]
    CHIP_W, CHIP_GAP = 44, 16
    row_w = len(socials) * CHIP_W + (len(socials) - 1) * CHIP_GAP
    row_x = AV["cx"] - row_w // 2
    a(f'<g>{reveal(1.85, .9, 10)}')
    for k, ic in enumerate(socials):
        cx0 = row_x + k * (CHIP_W + CHIP_GAP)
        a(f'<g>{float_y(2.5, 5.4 + k * .45, k * .35)}')
        a(f'<rect x="{cx0}" y="{CHIP_Y}" width="{CHIP_W}" height="{CHIP_H}" rx="12" '
          f'fill="{T["a2"]}" fill-opacity="0">'
          + pulse("fill-opacity", T["haloOp"]*.25, T["haloOp"]*.7, 4.5 + k*.4, k*.3) + '</rect>')
        a(f'<rect x="{cx0+.5}" y="{CHIP_Y+.5}" width="{CHIP_W-1}" height="{CHIP_H-1}" rx="11.5" '
          f'fill="{T["pillFill"]}" '
          f'fill-opacity="{n(T["pillFillOp"])}" stroke="{T["stroke"]}" stroke-opacity="{n(T["strokeOp"]*1.4)}"/>')
        a(icon(ic, T["sub"], cx0 + 14, CHIP_Y + (CHIP_H - 16) // 2, 1.0, .92))
        a('</g>')
    a('</g>')
    a('</g>')   # /left panel reveal

    # ==================== TERMINAL ====================
    a(f'<g>{reveal(.45, 1.0, 14)}')

    # title bar
    a(f'<g clip-path="url(#{i("term")})">')
    a(f'<rect x="{TP["x"]}" y="{TP["y"]}" width="{TP["w"]}" height="40" fill="{T["barCol"]}" '
      f'fill-opacity="{n(T["barOp"])}"/>')
    a(f'<rect x="{TP["x"]}" y="{TP["y"]+39.5}" width="{TP["w"]}" height="1" fill="{T["stroke"]}" '
      f'fill-opacity="{n(T["strokeOp"])}"/>')
    a('</g>')
    for k, dc in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        a(f'<circle cx="{500 + k*18}" cy="44" r="5.5" fill="{dc}" opacity=".88"/>')
    a(f'<text x="815" y="48" text-anchor="middle" font-family="{MONO}" font-size="11.5" '
      f'letter-spacing=".3" fill="{T["dim"]}">shrisht@aether — ~/profile</text>')
    a(f'<circle cx="1092" cy="44" r="3.2" fill="{T["a3"]}">' + pulse("opacity", .45, 1, 2.6) + '</circle>')
    a(f'<text x="1102" y="47.5" font-family="{MONO}" font-size="10.5" letter-spacing=".8" '
      f'fill="{T["dim"]}">live</text>')

    # prompt
    a(f'<g>{reveal(.9, .7, 8)}'
      f'<text x="{TX}" y="96" font-family="{MONO}" font-size="12.5" fill="{T["dim"]}">'
      f'<tspan fill="{T["a3"]}">$</tspan> aether whoami <tspan fill="{T["dim"]}" opacity=".6">--profile</tspan>'
      f'</text></g>')

    # greeting
    a(f'<g>{reveal(1.05, .9, 12)}'
      f'<text x="{TX}" y="136" font-family="{UI}" font-size="28" font-weight="700" letter-spacing="-.5" '
      f'fill="{T["text"]}">Hi <tspan font-size="26">\U0001F44B</tspan>, I’m '
      f'<tspan fill="{u("name")}">Shrisht</tspan></text></g>')

    # typing line
    a(f'<g>{reveal(1.45, .7, 8)}')
    a(f'<g clip-path="url(#{i("typeclip")})" font-family="{MONO}" font-size="19" fill="{u("type")}" '
      f'font-weight="500">')
    for k, ph in enumerate(PHRASES):
        s = k * 5.0 + .25
        kt = f'0;{n(round(s/CYCLE,5))};{n(round((s+4.4)/CYCLE,5))}'
        # phrase 0 keeps a static opacity of 1 so the no-SMIL fallback shows one
        # complete, fully-typed line rather than an empty row
        base = "" if k == 0 else ' opacity="0"'
        a(f'<text x="{TX}" y="176" textLength="{n(round(len(ph)*ADV,1))}" lengthAdjust="spacing"{base}>'
          f'{esc(ph)}<animate attributeName="opacity" calcMode="discrete" dur="{n(CYCLE)}s" '
          f'repeatCount="indefinite" keyTimes="{kt}" values="0;1;0"/></text>')
    a('</g>')
    a(f'<rect x="{n(TX + 2 + round(len(PHRASES[0]) * ADV, 1))}" y="159" width="2.6" height="22" '
      f'rx="1.3" fill="{T["a2"]}">'
      + steps_anim("x", steps, lambda c: TX + 2 + round(c * ADV, 1))
      + f'<animate attributeName="opacity" calcMode="discrete" dur="1.06s" repeatCount="indefinite" '
      f'keyTimes="0;.5" values="1;.05"/></rect>')
    a('</g>')

    a(f'<rect x="{TX}" y="199" width="{TXR-TX}" height="1" fill="{u("rule")}">'
      + fade(1.5, .8) + '</rect>')

    # column A -- currently building
    a(f'<g>{reveal(1.7, .7, 8)}'
      f'<text x="{TX}" y="226" font-family="{UI}" font-size="9.5" font-weight="700" letter-spacing="1.5" '
      f'fill="{T["dim"]}">CURRENTLY BUILDING</text></g>')
    for k, item in enumerate(BUILDING):
        iy = 252 + k * 26
        a(f'<g>{reveal(1.9 + k * .16, .75, 8)}')
        a(f'<circle cx="{TX+4}" cy="{iy-4.5}" r="3" fill="{u("acc")}">'
          + pulse("opacity", .55, 1, 3.4 + k*.5, k*.4) + '</circle>')
        a(f'<text x="{TX+18}" y="{iy}" font-family="{UI}" font-size="13.5" font-weight="500" '
          f'fill="{T["sub"]}">{esc(item)}</text>')
        a('</g>')

    # column B -- current focus
    CB = 754
    a(f'<g>{reveal(1.8, .7, 8)}'
      f'<text x="{CB}" y="226" font-family="{UI}" font-size="9.5" font-weight="700" letter-spacing="1.5" '
      f'fill="{T["dim"]}">CURRENT FOCUS</text></g>')
    for k, item in enumerate(FOCUS):
        iy = 252 + k * 26
        a(f'<g>{reveal(2.05 + k * .16, .75, 8)}')
        a(f'<rect x="{CB}" y="{iy-9}" width="7" height="7" rx="1.6" fill="{T["a2"]}" opacity=".8" '
          f'transform="rotate(45 {CB+3.5} {iy-5.5})">'
          + pulse("opacity", .45, .95, 3.8 + k*.4, k*.35) + '</rect>')
        a(f'<text x="{CB+18}" y="{iy}" font-family="{UI}" font-size="13.5" font-weight="500" '
          f'fill="{T["sub"]}">{esc(item)}</text>')
        a('</g>')

    # bottom command line
    a(f'<rect x="{TX}" y="352" width="440" height="1" fill="{u("rule")}">'
      + fade(2.5, .8) + '</rect>')
    a(f'<g>{reveal(2.7, .8, 8)}'
      f'<text x="{TX}" y="378" font-family="{MONO}" font-size="12" fill="{T["dim"]}">'
      f'<tspan fill="{T["a3"]}">$</tspan> aether deploy <tspan fill-opacity=".65">--target '
      f'cloudflare-workers</tspan>'
      # cursor rides in the text flow, so it stays glued to the last glyph in any monospace face
      f'<tspan fill="{T["a3"]}" fill-opacity=".8">█'
      f'<animate attributeName="fill-opacity" calcMode="discrete" dur="1.06s" '
      f'repeatCount="indefinite" keyTimes="0;.5" values=".8;.05"/></tspan>'
      f'</text></g>')

    # ---- ASCII panel ----
    a(f'<g>{reveal(2.0, 1.0, 10)}')
    a(f'<rect x="{ASC["x"]}" y="{ASC["y"]}" width="{ASC["w"]}" height="{ASC["h"]}" rx="12" '
      f'fill="{T["a1"]}" fill-opacity="{n(T["haloOp"]*.4)}"/>')
    a(f'<rect x="{ASC["x"]+.5}" y="{ASC["y"]+.5}" width="{ASC["w"]-1}" height="{ASC["h"]-1}" rx="11.5" '
      f'fill="none" stroke="{u("acc")}" stroke-opacity=".3"/>')

    acx = ASC["x"] + ASC["w"] / 2
    ay0, ALH = 234, 13          # baseline of row 0, and row pitch
    # Box-drawing and block glyphs are often served by a different fallback face than
    # ASCII, with a different advance width -- which shears the art into a ragged mess.
    # Pinning every row to one textLength (identical glyph count => identical column
    # grid) and scaling glyphs to fill it keeps the frame joined in any font.
    alen = len(ASCII_ART[0])
    atl = round(alen * 6.9, 1)
    lines = []
    for k, ln in enumerate(ASCII_ART):
        lines.append(f'<text x="{n(acx)}" y="{ay0 + k*ALH}" text-anchor="middle" xml:space="preserve" '
                     f'textLength="{n(atl)}" lengthAdjust="spacingAndGlyphs">{esc(ln)}'
                     + fade(2.35 + k * .1, .5) + '</text>')
    body = "".join(lines)
    a(f'<g clip-path="url(#{i("asc")})">')
    a(f'<g font-family="{MONO}" font-size="11.5" font-weight="500">{float_y(4, 9.0, .5)}')
    a(f'<g filter="url(#{i("soft")})" fill="{T["a2"]}" opacity=".42">{body}</g>')
    a(f'<g fill="{u("ascii")}">{body}</g>')
    a('</g>')
    a(f'<rect x="{ASC["x"]}" y="{ASC["y"]}" width="{ASC["w"]}" height="46" fill="{u("scan")}" opacity="1">'
      f'<animateTransform attributeName="transform" type="translate" values="0 -60;0 {ASC["h"]+20}" '
      f'dur="6.5s" begin="2.8s" repeatCount="indefinite"/></rect>')
    a('</g></g>')
    a('</g>')   # /terminal reveal

    # ==================== SKILLS ====================
    a(f'<g>{reveal(.65, 1.0, 14)}')
    a(f'<text x="{TX}" y="454" font-family="{UI}" font-size="9.5" font-weight="700" letter-spacing="1.5" '
      f'fill="{T["dim"]}">TECH STACK</text>')
    a(f'<text x="{TXR}" y="454" text-anchor="end" font-family="{MONO}" font-size="9.5" '
      f'letter-spacing=".6" fill="{T["dim"]}" opacity=".75">16 tools · production</text>')

    idx = 0
    for r, row in enumerate(SKILL_ROWS):
        x = TX
        y = 468 + r * 40
        for label in row:
            pw = round(len(label) * 6.6) + 30
            dly = 2.15 + idx * .055
            a(f'<g>{fade(dly, .6)}')
            a(f'<g>{float_y(2.6, 5.0 + (idx % 5) * .55, (idx % 7) * .42)}')
            a(f'<rect x="{x-2.5}" y="{y-2.5}" width="{pw+5}" height="33" rx="16.5" fill="{u("acc")}" '
              f'fill-opacity="0">'
              + pulse("fill-opacity", T["haloOp"]*.35, T["haloOp"], 5.2 + (idx % 4)*.6, (idx % 6)*.5) + '</rect>')
            a(f'<rect x="{x}" y="{y}" width="{pw}" height="28" rx="14" fill="{T["pillFill"]}" '
              f'fill-opacity="{n(T["pillFillOp"])}" stroke="{T["stroke"]}" '
              f'stroke-opacity="{n(T["pillStrokeOp"])}"/>')
            a(f'<rect x="{x+8}" y="{y+.5}" width="{pw-16}" height="1" rx=".5" fill="{u("edge")}"/>')
            a(f'<text x="{n(x+pw/2)}" y="{y+18}" text-anchor="middle" font-family="{UI}" font-size="12" '
              f'font-weight="600" letter-spacing=".1" fill="{T["sub"]}">{esc(label)}</text>')
            a('</g></g>')
            x += pw + 10
            idx += 1
    a('</g>')

    # ==================== OVERLAYS ====================
    # plain alpha, no mix-blend-mode: overlay-blending mid-grey noise is a no-op on
    # dark backgrounds, and blend support in SVG-as-<img> is inconsistent anyway
    a(f'<rect width="{W}" height="{H}" fill="{u("noise")}" opacity="{n(T["noiseOp"])}"/>')
    a('</g>')  # /card clip

    # ==================== BORDER ====================
    a(f'<rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="23.5" fill="none" '
      f'stroke="{T["stroke"]}" stroke-opacity="{n(T["strokeOp"]*1.5)}" stroke-width="1.5"/>')
    a(f'<rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="23.5" fill="none" '
      f'stroke="{u("shim")}" stroke-width="1.5" opacity=".9"/>')
    a(f'<rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="23.5" fill="none" '
      f'stroke="{u("comet")}" stroke-width="2" stroke-linecap="round" pathLength="100" '
      f'stroke-dasharray="9 91" opacity=".85">'
      f'<animate attributeName="stroke-dashoffset" values="100;0" dur="9s" repeatCount="indefinite"/></rect>')

    head = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {W} {H}" width="{W}" height="{H}" fill="none" role="img" '
            f'text-rendering="geometricPrecision" font-family="{UI}">'
            f'<title>Shrisht (@D0paX) — AI Systems Engineer · Founder, Aether AI OS</title>'
            f'<desc>Animated profile hero: portrait, rotating role typewriter, current focus, '
            f'tech stack and contact links.</desc>')
    return head + "".join(o) + "</svg>"


for T in (DARK, LIGHT):
    svg = build(T)
    path = os.path.join(OUT, f'{T["key"]}.svg')
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    print(f'{path}  {len(svg.encode("utf-8")):,} bytes')
