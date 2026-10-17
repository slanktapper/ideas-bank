"""A dimensioned drawing of the end cap, generated from params.py.

Three orthographic views and a parameter table. Everything is drawn from
the same numbers and the same outline the STL is built from, so the drawing
cannot drift away from the part -- change a parameter, re-run, and both move
together. That is the whole reason this is code and not a picture.

Not a render: no camera, no mesh. Straight 2D projection of the profile
polygon, because a dimension on a perspective render is a lie by a few
percent and this is meant to be read off.
"""

import math

from PIL import Image, ImageDraw, ImageFont

import params as P

W, H = 3320, 1780
BG = (253, 253, 251)
INK = (28, 32, 40)          # the part
DIMC = (24, 92, 168)        # dimensions
GHOST = (176, 182, 192)     # the aluminium, for context
HID = (150, 156, 168)       # hidden detail
NOTE = (96, 104, 118)
WARN = (184, 72, 32)

SC = 12.0                   # px per mm
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _f(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


F = _f(FONT, 23)
FS = _f(FONT, 19)
FB = _f(FONTB, 26)
FT = _f(FONTB, 34)


def arrow(d, tip, ang, col, size=11):
    a1, a2 = ang + 2.7, ang - 2.7
    d.polygon([tip,
               (tip[0] + size * math.cos(a1), tip[1] + size * math.sin(a1)),
               (tip[0] + size * math.cos(a2), tip[1] + size * math.sin(a2))],
              fill=col)


def dim(d, a, b, text, *, off=0, side=1, col=DIMC, font=F, ext=True, out=False):
    """A linear dimension between two points, offset perpendicular by `off`."""
    ax, ay = a
    bx, by = b
    vx, vy = bx - ax, by - ay
    L = math.hypot(vx, vy) or 1.0
    ux, uy = vx / L, vy / L
    nx, ny = -uy * side, ux * side
    p = (ax + nx * off, ay + ny * off)
    q = (bx + nx * off, by + ny * off)
    if ext:
        for s, e in ((a, p), (b, q)):
            d.line([(s[0] + nx * 5, s[1] + ny * 5),
                    (e[0] + nx * 8, e[1] + ny * 8)], fill=col, width=1)
    d.line([p, q], fill=col, width=2)
    ang = math.atan2(q[1] - p[1], q[0] - p[0])
    if out:
        d.line([(p[0] - ux * 26, p[1] - uy * 26), p], fill=col, width=2)
        d.line([q, (q[0] + ux * 26, q[1] + uy * 26)], fill=col, width=2)
        arrow(d, p, ang, col)
        arrow(d, q, ang + math.pi, col)
    else:
        arrow(d, p, ang + math.pi, col)
        arrow(d, q, ang, col)
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    horiz = abs(ux) > abs(uy)
    tw = d.textlength(text, font=font)
    if horiz:
        box = (mx - tw / 2 - 5, my - 15, mx + tw / 2 + 5, my + 15)
        d.rectangle(box, fill=BG)
        d.text((mx, my), text, font=font, fill=col, anchor="mm")
    else:
        d.text((mx + 10, my), text, font=font, fill=col, anchor="lm")


def leader(d, at, to, text, col=DIMC, font=F, anchor="lm", pad=10):
    d.line([at, to], fill=col, width=2)
    r = 4
    d.ellipse([at[0] - r, at[1] - r, at[0] + r, at[1] + r], fill=col)
    dx = pad if anchor == "lm" else -pad
    d.text((to[0] + dx, to[1]), text, font=font, fill=col, anchor=anchor)


def poly_px(poly, ox, oy, fx=1, fy=-1):
    return [(ox + x * SC * fx, oy + y * SC * fy)
            for x, y in poly.exterior.coords]


def draw():
    import build  # for profile(); imported here to keep the module standalone
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    prof = build.profile()
    cw, cd = P.CAP_W, P.EXT_DEPTH + P.LIP_H
    half = P.HOLE_PITCH / 2.0

    # ---- title block --------------------------------------------------
    d.text((56, 44), "VKB T-Rudder Mk.V \u2014 foot rest end cap", font=FT, fill=INK)
    d.text((58, 92),
           f"all dimensions mm   \u00b7   print 4\u00d7   \u00b7   {P.MATERIAL}   \u00b7   "
           f"generated from params.py", font=FS, fill=NOTE)
    d.line([(56, 126), (W - 56, 126)], fill=(216, 220, 228), width=2)

    # =================== FRONT VIEW ====================================
    ox, oy = 700, 800                      # origin = back edge, on centreline
    L, R = ox - cw / 2 * SC, ox + cw / 2 * SC
    TOP, BOT = oy - cd * SC, oy
    d.text((L, 232), "FRONT   (the face your foot meets)", font=FB, fill=INK)
    d.polygon(poly_px(prof, ox, oy), outline=INK, width=3)

    # the crowned foot face of the extrusion, ghosted in behind
    arc_r = ((P.EXT_WIDTH / 2) ** 2 + P.CROWN ** 2) / (2 * P.CROWN)
    pts = []
    for i in range(61):
        x = -P.EXT_WIDTH / 2 + i * P.EXT_WIDTH / 60
        y = (P.EXT_DEPTH - arc_r) + math.sqrt(max(arc_r ** 2 - x ** 2, 0))
        pts.append((ox + x * SC, oy - y * SC))
    d.line(pts, fill=GHOST, width=3)
    d.text((ox, oy - P.EXT_DEPTH * SC - 62), "crowned face of the extrusion,",
           font=FS, fill=GHOST, anchor="ma")
    d.text((ox, oy - P.EXT_DEPTH * SC - 38), "buried inside the cap",
           font=FS, fill=GHOST, anchor="ma")

    for s_ in (-1, 1):
        cx, cy = ox + s_ * half * SC, oy - P.BOSS_Y * SC
        for dia, col, wdt in ((P.CBORE_D, HID, 2), (P.CLEAR_D, INK, 3)):
            r = dia / 2 * SC
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=wdt)
        d.line([(cx - 42, cy), (cx + 42, cy)], fill=HID, width=1)
        d.line([(cx, cy - 42), (cx, cy + 42)], fill=HID, width=1)

    dim(d, (L, BOT), (L, TOP), f"{cd:.1f}", off=150, side=-1)
    dim(d, (R, BOT), (R, oy - P.EXT_DEPTH * SC), f"{P.EXT_DEPTH:.1f}",
        off=80, side=1)
    dim(d, (R, oy - P.EXT_DEPTH * SC), (R, TOP), f"{P.LIP_H:.1f} lip",
        off=80, side=1)
    dim(d, (ox - half * SC, oy - P.BOSS_Y * SC),
        (ox + half * SC, oy - P.BOSS_Y * SC),
        f"{P.HOLE_PITCH:.1f}  bolt pitch", off=150, side=1)
    dim(d, (L, BOT), (R, BOT), f"{cw:.1f}", off=250, side=1)
    dim(d, (R, oy), (R, oy - P.BOSS_Y * SC), f"{P.BOSS_Y:.1f}  BOSS_Y",
        off=215, side=1, col=WARN, out=True)
    d.text((R + 215, oy + 54), "PROVISIONAL", font=FS, fill=WARN, anchor="mm")

    hx, hy = ox - half * SC, oy - P.BOSS_Y * SC
    d.line([(hx - P.CBORE_D / 2 * SC * 0.71, hy + P.CBORE_D / 2 * SC * 0.71),
            (170, 1118)], fill=DIMC, width=2)
    d.text((170, 1110),
           f"\u2300 {P.CLEAR_D:.1f} bolt hole, through \u2014 for M{P.BOLT_D:.0f}",
           font=F, fill=DIMC)
    d.text((170, 1146),
           f"\u2300 {P.CBORE_D:.1f} pocket \u00d7 {P.CAP_L - P.GRIP:.0f} deep, "
           f"open at the back", font=F, fill=DIMC)
    d.text((170, 1182), f"for a \u2300{P.HEAD_D:.0f} domed head, "
           f"{P.HEAD_SINK:.0f} below the face", font=FS, fill=NOTE)

    leader(d, (ox - (cw / 2 - P.R_TIP * 0.3) * SC, TOP + P.R_TIP * 0.3 * SC),
           (L - 130, TOP - 4), f"R {P.R_TIP:.0f}", anchor="rm")
    leader(d, (ox + (cw / 2 - P.R_BACK * 0.3) * SC, BOT - P.R_BACK * 0.3 * SC),
           (R + 150, BOT + 36), f"R {P.R_BACK:.0f}")

    # =================== SIDE VIEW ======================================
    sx, sy = 1540, 800
    z0, z1 = sx, sx + P.CAP_L * SC
    d.text((z0 - 60, 232), "SIDE", font=FB, fill=INK)
    ch = P.CH_MATE * SC
    d.polygon([(z0 + ch, sy), (z1, sy), (z1, sy - cd * SC),
               (z0 + ch, sy - cd * SC), (z0, sy - cd * SC + ch),
               (z0, sy - ch)], outline=INK, width=3)
    for yy in (sy, sy - P.EXT_DEPTH * SC):
        d.line([(z0, yy), (z0 - 110, yy)], fill=GHOST, width=3)
    d.line([(z0 - 110, sy), (z0 - 110, sy - P.EXT_DEPTH * SC)],
           fill=GHOST, width=2)
    d.text((z0 - 55, sy - P.EXT_DEPTH * SC / 2), "extrusion", font=FS,
           fill=GHOST, anchor="mm")

    gz = z0 + P.GRIP * SC
    by = sy - P.BOSS_Y * SC
    d.line([(gz, by - P.CBORE_D / 2 * SC), (z1, by - P.CBORE_D / 2 * SC)],
           fill=HID, width=2)
    d.line([(gz, by - P.CBORE_D / 2 * SC), (gz, by + P.CBORE_D / 2 * SC)],
           fill=HID, width=2)
    for dy in (-P.CLEAR_D / 2 * SC, P.CLEAR_D / 2 * SC):
        d.line([(z0, by + dy), (gz, by + dy)], fill=HID, width=2)

    dim(d, (z0, sy), (z1, sy), f"{P.CAP_L:.1f}", off=110, side=1)
    dim(d, (z0, sy), (gz, sy), f"{P.GRIP:.0f} grip", off=215, side=1, out=True)
    dim(d, (gz, sy), (z1, sy), f"{P.CAP_L - P.GRIP:.0f} pocket",
        off=300, side=1, out=True)
    d.text((z1 + 60, TOP + 10),
           f"bolt  M{P.BOLT_D:.0f} \u00d7 {P.BOLT_LEN:.0f}\n"
           f"  {P.GRIP:.0f} grip inside the cap\n"
           f"+ {P.BOLT_LEN - P.GRIP:.0f} thread into the boss\n"
           f"= {P.BOLT_LEN:.0f}\n\n"
           f"{P.CH_MATE:.1f} chamfer on the mating\nface, nothing on the outer\n"
           f"face \u2014 see CH_OUTER", font=FS, fill=NOTE)

    # =================== BACK VIEW ======================================
    bx, byo = 700, 1560
    d.text((L, 1300), "BACK   (against the pedal arm)", font=FB, fill=INK)
    d.rectangle([bx - cw / 2 * SC, byo - P.CAP_L * SC,
                 bx + cw / 2 * SC, byo], outline=INK, width=3)
    for s_ in (-1, 1):
        x0 = bx + s_ * half * SC - P.CBORE_D / 2 * SC
        x1 = bx + s_ * half * SC + P.CBORE_D / 2 * SC
        d.rectangle([x0, byo - P.CAP_L * SC, x1, byo - P.GRIP * SC],
                    fill=(243, 238, 230), outline=INK, width=3)
    dim(d, (bx + half * SC - P.CBORE_D / 2 * SC, byo),
        (bx + half * SC + P.CBORE_D / 2 * SC, byo),
        f"{P.CBORE_D:.1f}", off=80, side=1)
    d.text((bx + cw / 2 * SC + 70, byo - P.CAP_L * SC / 2),
           "the two pockets are open at this edge \u2014 deliberate.\n"
           f"the head is \u2300{P.HEAD_D:.0f} and the back face is {P.BOSS_Y:.1f} "
           "from the bolt axis,\nso the head never reaches it. only clearance "
           "air is let out,\nand the ring it bears on is complete.",
           font=FS, fill=NOTE, anchor="lm")

    # =================== PARAMETER TABLE ================================
    tx, ty = 2230, 300
    d.text((tx, ty), "params.py \u2014 what to change", font=FB, fill=INK)
    ty += 48
    d.text((tx, ty), "name", font=FS, fill=NOTE)
    d.text((tx + 290, ty), "mm", font=FS, fill=NOTE, anchor="ra")
    d.text((tx + 330, ty), "where it comes from", font=FS, fill=NOTE)
    d.line([(tx, ty + 30), (W - 56, ty + 30)], fill=(216, 220, 228), width=2)
    ty += 48

    rows = [
        ("HOLE_PITCH", P.HOLE_PITCH, "measured", "caliper, \u00b10.5"),
        ("EXT_WIDTH", P.EXT_WIDTH, "measured", "across the end face"),
        ("EXT_DEPTH", P.EXT_DEPTH, "measured", "at the crown, the deepest point"),
        ("CROWN", P.CROWN, "provisional", "reaches the part only through BOSS_Y"),
        ("BOSS_Y", P.BOSS_Y, "provisional", "bolt centre from the flat back"),
        ("BOLT_D", P.BOLT_D, "hardware", "M5"),
        ("BOLT_LEN", P.BOLT_LEN, "hardware", "with the head, this sets CAP_L"),
        ("HEAD_D", P.HEAD_D, "measured", "domed head, across"),
        ("HEAD_H", P.HEAD_H, "provisional", "over-stating it is safe"),
        ("CLEAR_D", P.CLEAR_D, "choice", "THE BOLT HOLE \u2014 BOLT_D + 1.6"),
        ("CBORE_D", P.CBORE_D, "derived", "HEAD_D + 1.0; domes need the room"),
        ("GRIP", P.GRIP, "choice", "bolt inside the cap; the rest threads in"),
        ("LIP_H", P.LIP_H, "taste", "how hard a stop you want"),
        ("CAP_L", P.CAP_L, "derived", "GRIP + HEAD_H + HEAD_SINK"),
        ("CAP_W", P.CAP_W, "derived", "widens if the bores near the side edge"),
        ("R_TIP", P.R_TIP, "taste", "the corner a foot actually meets"),
        ("R_BACK", P.R_BACK, "taste", "back corners, away from the foot"),
        ("CH_MATE", P.CH_MATE, "choice", "keeps elephant's foot off the seat"),
        ("CH_OUTER", P.CH_OUTER, "forced", "0 \u2014 a chamfer here eats the wall"),
        ("MIN_WALL", P.MIN_WALL, "rule", "least material beside a pocket"),
    ]
    tag_col = {"provisional": WARN, "measured": (26, 120, 72),
               "derived": NOTE, "taste": DIMC, "choice": DIMC,
               "hardware": (26, 120, 72), "forced": WARN, "rule": NOTE}
    for name, val, tag, why in rows:
        bold = tag == "provisional"
        d.text((tx, ty), name, font=_f(FONTB if bold else FONT, 22),
               fill=WARN if bold else INK)
        d.text((tx + 290, ty), f"{val:.1f}", font=F, fill=INK, anchor="ra")
        d.text((tx + 330, ty), tag, font=FS, fill=tag_col[tag])
        d.text((tx + 470, ty), why, font=FS, fill=NOTE)
        ty += 36

    ty += 30
    d.text((tx, ty),
           "Change a number and run  python3 build.py  \u2014 the STL, every\n"
           "render and this drawing all move together.\n\n"
           "Derived values re-solve themselves. Widen the head and CBORE_D,\n"
           "CAP_W and the open back all follow on their own.\n\n"
           "The two in red are still read off a photograph. BOSS_Y is the\n"
           "one that decides whether the cap bolts on at all.",
           font=FS, fill=NOTE)

    out = "renders/08-drawing.png"
    img.save(out)
    return out


if __name__ == "__main__":
    print(draw())
