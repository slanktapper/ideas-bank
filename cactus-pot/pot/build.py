"""The pebble pot: a straight-sided cylinder with a rounded foot, a stone-like
field of raised cells above a scalloped line, and a smooth panel for the name.

The panel is the point of the design. It is simply a patch of the bare cylinder
left clear of cells, so the lettering sits on a true cylinder of one radius --
every line wraps the same amount, which is what went wrong on the pot we started
from.
"""
from __future__ import annotations
import pathlib
import numpy as np, trimesh
import potlib as P
from text3d import Face, fit_lines
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from shapely import affinity
from scipy.spatial import Voronoi

# The size dial. Rob asked for everything 25% bigger on 2026-10-07, and the
# cactus half took the same 1.25 in its own params.py -- the two have to agree
# or the spigot stops fitting the socket. Every length below is its original
# design number times SCALE, so the shape stays readable and the size is one
# number.
#
# Not scaled: BEAD_GAP and BAND_BITE, which are not shape at all. They are the
# fractions of a millimetre that keep two solids from meeting exactly, because
# coincident faces stop the union being a volume on reload. They depend on the
# boolean engine, not on how big the pot is.
SCALE = 1.25

# ---- the pot itself --------------------------------------------------------
R, H      = 46.0 * SCALE, 76.0 * SCALE        # outer radius, overall height
WALL      = 3.2 * SCALE
FOOT_R    = 20.0 * SCALE              # radius of the roll into the base
BASE_FLAT = 26.0 * SCALE              # flat the pot stands on

# The well and its socket are copied from the pot we started from, so the cactus
# being built alongside this still drops straight in: a 21 mm well, with a blind
# 32.00 mm by 8.00 mm socket in the middle of its floor.
WELL_Z    = 55.0 * SCALE              # inner floor height -- 21 mm below the rim
SOCKET_D  = 32.0 * SCALE
SOCKET_H  = 8.0 * SCALE

# ---- the stone field -------------------------------------------------------
WAVE_Z    = 4.3 * SCALE               # mean position of the scalloped line, measured as
                              # arc length along the outer profile: 4.3 is halfway
                              # round the foot's roll, at z = 5.86
WAVE_A    = 0.6 * SCALE               # the scallops, scaled down to fit under the roll
CELL_H    = 1.15 * SCALE              # how far the cells stand proud
GROOVE    = 1.05 * SCALE              # width of the gap between cells
N_CELLS   = 310               # kept in step with the taller field, for one size
                              # of stone throughout

# ---- the panel -------------------------------------------------------------
PAN_W, PAN_H, PAN_Z = 78.0 * SCALE, 37.0 * SCALE, 48.5 * SCALE
PAN_SINK  = 0.5 * SCALE               # how far the panel sits below the plain wall
TEXT_RAISE = 1.0 * SCALE              # how far the letters stand off the panel face
TEXT_R     = 0.4 * SCALE              # the roll on their top edge. Half the narrowest
                              # stroke is about 0.7 mm, so 0.4 rolls over without
                              # eating a stroke away
TEXT_STEPS = 4                # steps in the roll; 4 puts each riser at 0.1 mm
PAN_INSET  = 5.0 * SCALE              # clear margin left and right of the longest line
BEAD_W    = 1.8 * GROOVE      # the border round each stone. At 1.0x the groove
                              # two neighbouring borders met exactly in the middle
                              # and anything wider than nominal showed gold; at
                              # 1.8x they overlap, so every nominal groove is
                              # filled solid and the bead stands 1.6x taller
BEAD_STEPS = 5                # steps in the rounded section; 5 puts each riser
                              # at 0.10 mm, under any layer this will print at
BEAD_GAP  = 0.02              # how far short of the groove's middle each stone's
                              # half stops. Two halves that met exactly would
                              # leave a coincident pair of faces in the union,
                              # and the mesh stops being a volume on reload.
BAND_D    = CELL_H            # the raised bottom stands as proud as the stones do
BAND_GAP  = GROOVE            # and is held off the lowest of them by the same gap
                              # the stones are set apart by, so the groove reads
                              # the same all over the pot
BAND_BITE = 0.3               # how far its skin reaches into the wall. It has to
                              # overlap the body rather than land on it: two solids
                              # meeting exactly leave coincident faces and the
                              # union stops being a volume on reload.
PAN_MARGIN = 2.5 * SCALE              # clear margin above and below the block of text.
                              # All three lines are set at one size and the block
                              # is centred on its inked extent, so the margin
                              # that comes out top and bottom is this number.
LINES = ['Eleanor', "Shellstrop's", 'File']


def wave(u):
    """The scalloped line, as a function of arc position round the pot.

    The value is a position along the outer profile, not a height: on the straight
    wall the two are the same, and below z = FOOT_R it keeps running round the
    roll. See `potlib.body_point`.
    """
    t = u / R
    return (WAVE_Z + WAVE_A*(4.6*np.sin(5*t + 0.4) + 2.2*np.sin(8*t + 1.9)
                             + 1.3*np.sin(13*t + 0.7)))


def profile_outer():
    pts = [(0.0, 0.0), (BASE_FLAT, 0.0)]
    for a in np.linspace(0, np.pi/2, 26)[1:]:
        pts.append((BASE_FLAT + FOOT_R*np.sin(a), FOOT_R - FOOT_R*np.cos(a)))
    pts += [(R, H-1.2), (R-1.2, H), (0.0, H)]
    return pts


def profile_cavity():
    """The well: a flat floor with a small fillet into a straight inner wall."""
    ri, fr = R - WALL, 4.0
    pts = [(0.0, WELL_Z), (ri - fr, WELL_Z)]
    for a in np.linspace(0, np.pi/2, 10)[1:]:
        pts.append((ri - fr + fr*np.sin(a), WELL_Z + fr - fr*np.cos(a)))
    pts += [(ri, H+1.0), (0.0, H+1.0)]
    return pts


def panel_shape():
    """The clear patch, in (arc, z). Rounded corners, like a cast cartouche."""
    r = 7.0
    return box(-PAN_W/2 + r, PAN_Z - PAN_H/2 + r, PAN_W/2 - r, PAN_Z + PAN_H/2 - r).buffer(r)


def stone_border(cells=None):
    """A rounded border round every stone, filling the grooves between them.

    Each stone gets its own half of the bead: a quarter-round of radius BEAD_W/2
    swept along its outline, rising from nothing at the stone's foot to BEAD_W/2
    out. BEAD_W is 1.8x the nominal groove, so at nominal spacing two neighbours'
    quarters overlap and fill the groove solid, and a wider-than-nominal gap gets
    a border 1.8x as wide as before rather than a sliver of body colour. The
    overlaps are resolved here, so the result is one solid.
    Sweeping rather than stacking extruded bands matters even more here than it
    did for a single ring: the level sets of this shape are 180-hole polygons
    that do not extrude into closed solids at all.
    """
    a, half = BEAD_W / 2, BEAD_W / 2 - BEAD_GAP
    sec = ([(0.0, -1.0)]
           + [(t, float(np.sqrt(max(a*a - (a - t)**2, 0.0))))
              for t in np.linspace(0.0, half, BEAD_STEPS + 1)]
           + [(half, -1.0)])
    beads = []
    for c in (stone_cells() if cells is None else cells):
        # clockwise, so the sweep's normal points out of the stone
        ring = np.asarray(orient(c, -1.0).segmentize(1.8).exterior.coords)[:-1]
        beads.append(P.sweep_on_body(ring, sec, R, FOOT_R, BASE_FLAT))
    return P.union(*beads)


def profile_band():
    """The two (r, z) profiles bounding the raised bottom's skin.

    The outer one is the pot's own profile grown BAND_D along its normal -- so
    the band stands the same height proud of the foot's roll as it does of the
    straight wall -- clipped at z = 0 so the pot still stands on the same flat
    and keeps the same overall height. The inner one is the profile shrunk
    BAND_BITE, so the skin overlaps the body instead of landing on it.
    """
    base = Polygon(profile_outer())
    grown = base.buffer(BAND_D, join_style=2).intersection(box(0.0, 0.0, 200.0, H + 50.0))
    inner = base.buffer(-BAND_BITE, join_style=2)
    out = []
    for poly in (grown, inner):
        ring = np.asarray(orient(poly, 1.0).exterior.coords)[:-1]
        # snap the axis edge back onto the axis: a profile that misses it by
        # BAND_BITE would revolve into a solid with a pinhole down the middle
        out.append([(0.0 if r < BAND_BITE + 1e-6 else float(r), float(z)) for r, z in ring])
    return out


def grown_field(cells=None):
    """The stones, each grown by BAND_GAP, as one solid on the body.

    Growing every stone by the gap it is set apart from its neighbours by closes
    every groove between them, so what is left open below the field is a single
    region: exactly the raised bottom, with the right gap round it already. Each
    stone is grown and wrapped on its own and the overlaps are resolved by the
    union, which keeps the seam out of it -- a single grown polygon would run all
    the way round the pot and have nowhere to start and stop.
    """
    cells = stone_cells() if cells is None else cells
    prisms = [P.wrap_to_body(
                  P.text_prism(c.buffer(BAND_GAP, join_style=1), 2.0, over=2.0, dens=1.5),
                  R, FOOT_R, BASE_FLAT)
              for c in cells]
    return P.union(*prisms)


BAND_CUT = 20.0 * SCALE               # the raised bottom is cut out of the skin below
                              # this height. Anything between it and the bottom's
                              # own edge is under a grown stone, so the one
                              # horizontal cut in all of this falls where nothing
                              # is left to cut.


def bottom_band(cells=None, grown=None):
    """The bottom of the pot, standing as proud as the stones.

    One more raised shape rather than a plinth: it is the pot's own skin below
    BAND_CUT with the grown stones taken out of it, so it stops BAND_GAP short of
    the lowest of them and the groove round it is the groove between any two
    stones. It carries no border of its own -- each stone's own bead reaches
    0.925 of the 1.05 mm across, so that groove fills like any other.
    """
    outer, inner = profile_band()
    skin = P.diff(P.revolve(outer, seg=256), P.revolve(inner, seg=256))
    skin = P.intersect(skin, P.cyl(R + 8.0, -5.0, BAND_CUT, seg=256))
    return P.diff(skin, grown_field(cells) if grown is None else grown)


def stone_cells(seed=11):
    """Voronoi cells over the cylinder, clipped to the field and shrunk apart."""
    rng = np.random.default_rng(seed)
    span = 2*np.pi*R
    lo, hi = WAVE_Z - 6.0, H + 1.0
    n = N_CELLS
    pts = np.c_[rng.uniform(0, span, n), rng.uniform(lo, hi, n)]
    for _ in range(14):                                  # Lloyd relaxation, for even stones
        tiled = np.vstack([pts + [dx, 0] for dx in (-span, 0, span)])
        vor = Voronoi(tiled)
        new = []
        for i in range(n, 2*n):
            reg = vor.regions[vor.point_region[i]]
            if not reg or -1 in reg: new.append(pts[i-n]); continue
            poly = Polygon(vor.vertices[reg])
            if poly.is_empty or not poly.is_valid: new.append(pts[i-n]); continue
            c = poly.centroid
            new.append([c.x % span, min(max(c.y, lo), hi)])
        pts = np.asarray(new)

    tiled = np.vstack([pts + [dx, 0] for dx in (-span, 0, span)])
    vor = Voronoi(tiled)
    # clipped only in height: a cell straddling the seam is kept whole and
    # simply wraps round when it is bent onto the cylinder
    us = np.arange(-span/2 - 30, span/2 + 31, 1.0)
    below = Polygon([(us[0], -20)] + [(u, wave(u)) for u in us] + [(us[-1], -20)])
    field = box(us[0], -15, us[-1], H - 1.4).difference(below)
    clear = panel_shape().buffer(2.2)
    cells = []
    for i in range(len(tiled)):
        reg = vor.regions[vor.point_region[i]]
        if not reg or -1 in reg: continue
        poly = Polygon(vor.vertices[reg])
        if not poly.is_valid: poly = poly.buffer(0)
        # keep one copy of each cell: the one whose centre is in the window
        cx = poly.centroid.x
        if not (-span/2 <= cx < span/2): continue      # one copy of each cell
        p = poly.buffer(-GROOVE/2, join_style=1).buffer(0.45, join_style=1).buffer(-0.45, join_style=1)
        if p.is_empty or p.area < 6.0: continue
        p = p.intersection(field).difference(clear)
        if p.is_empty: continue
        for q in (p.geoms if p.geom_type == 'MultiPolygon' else [p]):
            # drop crumbs and splinters: too small, or too thin to read as a stone
            if q.area < 14.0 or q.buffer(-0.8).is_empty: continue
            cells.append(q)
    return cells


def stone_solid(cells=None):
    """The field of raised cells, as one solid, already wrapped onto the wall."""
    cells = stone_cells() if cells is None else cells
    prisms = [P.text_prism(c, CELL_H, over=1.2, dens=1.2) for c in cells]
    return P.wrap_to_body(trimesh.util.concatenate(prisms), R, FOOT_R, BASE_FLAT)


def panel_pocket():
    """The cutter that sinks the cartouche PAN_SINK below the plain wall."""
    return P.bend_to_cylinder(P.text_prism(panel_shape(), 2.0, over=PAN_SINK, dens=1.2), R)


def text_flat(quiet=False):
    """The three lines as one flat shapely geometry, placed on the panel."""
    face = Face('Outfit-Bold')
    placed = fit_lines(face, LINES, PAN_W - 2*PAN_INSET, PAN_H - 2*PAN_MARGIN, 9.6)
    text = unary_union([affinity.translate(g, 0, PAN_Z) for g, _, _ in placed])
    if not quiet:
        for g, cap, w in placed: print(f'  line cap {cap:.2f} mm, width {w:.1f} mm')
        lo, hi = text.bounds[1], text.bounds[3]
        print('  text z %.2f..%.2f in a panel of %.2f..%.2f -- margins %.2f above, '
              '%.2f below' % (lo, hi, PAN_Z - PAN_H/2, PAN_Z + PAN_H/2,
                              PAN_Z + PAN_H/2 - hi, lo - (PAN_Z - PAN_H/2)))
    return text


def text_solid(quiet=False):
    """The letters, standing TEXT_RAISE off the panel with a rolled top edge.

    The roll is cut as a stack: at height t into the top TEXT_R of the letter the
    outline is pulled in by r - sqrt(r^2 - t^2), which is a quarter-round turning
    the top edge over. Each step is a prism from the back of the letter up to that
    height, so the steps nest and their union is the letter; being nested rather
    than stacked is what keeps it one solid with no seams between slices.

    The letters sit in a panel sunk PAN_SINK, so at TEXT_RAISE proud of its face
    they top out 0.65 mm below the stones and the cartouche still protects them.
    """
    flat = text_flat(quiet)
    prisms = []
    for k in range(TEXT_STEPS + 1):
        t = TEXT_R * k / TEXT_STEPS
        d = TEXT_R - float(np.sqrt(max(TEXT_R*TEXT_R - t*t, 0.0)))
        poly = flat if d <= 0 else flat.buffer(-d, join_style=1)
        if poly.is_empty: continue
        # the panel face is PAN_SINK below the wall, so TEXT_RAISE off that face
        # is TEXT_RAISE - PAN_SINK out from the wall
        prisms.append(P.bend_to_cylinder(
            P.text_prism(poly, TEXT_RAISE - PAN_SINK - TEXT_R + t,
                         over=PAN_SINK + 0.6, dens=1.2), R))
    return P.union(*prisms)


def body_unlettered(quiet=False):
    """The pot with its stone field and sunken panel, before the name goes on."""
    body = P.diff(P.revolve(profile_outer(), seg=256),
                  P.revolve(profile_cavity(), seg=256),
                  P.cyl(SOCKET_D/2, WELL_Z - SOCKET_H, WELL_Z + 1.0, seg=96))
    if not quiet:
        print('body watertight', body.is_watertight, 'volume %.0f' % body.volume)
    cells = stone_cells()
    if not quiet:
        print('cells', len(cells))
    body = P.union(body, stone_solid(cells))
    if not quiet:
        print('with stone', body.is_watertight, len(body.faces))
    body = P.diff(body, panel_pocket())
    body = P.union(body, stone_border(cells), bottom_band(cells))
    if not quiet:
        print('with borders and band', body.is_watertight, len(body.faces))
    return body


def build():
    body = P.union(body_unlettered(), text_solid())
    print('final', body.is_watertight, len(body.faces), 'volume %.0f' % body.volume)
    out = pathlib.Path(__file__).resolve().parent / 'stl'
    out.mkdir(exist_ok=True)
    body.export(out / 'pebble-pot.stl')
    print('wrote', out / 'pebble-pot.stl')
    return body


if __name__ == '__main__':
    build()
