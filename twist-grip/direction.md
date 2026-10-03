# twist-grip

**Status:** prototype — modelled, checked, nothing printed yet

## What it is

A fidget that traps a finger. A 40 mm hole runs straight through a 115 mm
cylinder; twist the fluted outside and two blades come in from opposite sides
and close on whatever is in the hole, gripping **90 mm of it** — the whole
length of a finger, not a band round it. Twist it all the way and the two
faces meet on the axis. Twist it back and they retreat flush with the bore,
leaving a clean 40 mm circle.

It is a two-jaw scroll chuck, which is how a lathe holds work: a spiral
groove in a rotating plate, a pin on each jaw riding it, and the jaw able to
move only radially because a slot holds it. Half a turn is the whole range.

## Why

A finger trap you operate rather than one that operates on you. The appeal is
that the resistance you feel is a cam, not a spring, and that it holds
wherever you leave it: the spiral is 7.3° at its outer end and 12.2° at its
inner, against about 17° for PETG on PETG, so pressing outward on a blade
cannot unwind it. Nothing is sprung, ratcheted, screwed or glued.

## Scope

**What it does.** Two blades, driven in and out together by twisting, holding
90 mm of finger. A clear 40 mm bore when open, faces touching when shut, and
a positive stop at both ends.

**What it deliberately does not do.**

- **Measure anything.** No scale, no detents, no numbers. Where you leave it
  is where it stays, and that is the whole interface.
- **Grip hard.** It closes on a finger; it is not a vice, and nothing in it
  is sized for clamping loads.
- **Fit a pocket.** 115 mm across and 104 mm tall, and both of those are
  forced — see below. It is a desk object.

## The size is not a styling choice

The brief fixes four things, and between them they fix the whole object.

**How wide**, from the first three:

1. A face flush with a 40 mm bore that ends on the axis travels **20 mm**.
2. The cam pin cannot sit in front of its face, and its groove cannot cross
   the finger hole. Bore, body wall, turning fit, the lip that holds the
   thing together and one wall between that and the groove put the pin's
   inner limit at **r = 29.4**.
3. So the pin sweeps **r 29.4 to 49.4**, a blade's tail reaches **r = 53.9**
   when open, and the shell has to be outside all of it. **115 mm.**

**How tall**, from the fourth: 90 mm of grip, plus the scroll plate under it
and the one over it. **104 mm.**

A 2:1 lever between pin and blade would bring the diameter to about 80 mm, at
the cost of two more moving parts and two more pivots per jaw. It is the
first thing to try if the object is too big in the hand.

## How it works

`scroll.py` is the mechanism; everything else is housing.

The two jaws sit 180° apart, so as the shell turns through φ each pin moves
backwards through the shell's frame by φ. Over a sweep of exactly 180°, one
jaw's pin covers plate angles 180°→0° and the other's 360°→180°: the two
halves of the plate, with no overlap. Both grooves are then the same spiral
arc, one placed at 0° and one at 180°, and wherever they share an angle they
are a full 20 mm apart in radius. A half turn is also one wrist movement.

The spiral is Archimedean — radius linear in angle — so the blades close at a
constant 0.111 mm per degree. Anything else would make the closing speed
change as you turn, which feels like something binding.

Each groove ends in a flat pad so a pin runs onto a dead stop rather than
into a wedge. The pads are not a fixed angle: the end cap is square to the
path, so the pin's centre stops a pin radius short of it *measured along the
arc* — 6.1° at the inner end, 3.7° at the outer.

### Why there are two scroll plates

A 90 mm blade driven by a single pin at one end is a drawer pulled by one
corner. The friction of a finger down its length acts about the driven end
and cocks it in its slot, and a cocked blade jams.

So the rotating assembly carries a spiral at each end: the **shell's floor**,
with the groove blind in it, and the **cap**, with the same spiral cut
straight through so the pins are visible travelling. Three pegs on the
shell's rim key the cap to it, and each blade has a pin at each end. Both
ends are driven identically and the couple never exists.

## How it holds together

No screws, no glue, no snap fits — three hooks, all of the same kind.

- the **body's bottom lugs** hook under a lip inside the shell's bore;
- the **cap's hook ring** reaches in under the **body's top lugs**;
- the **body** rests on the shell's floor, and the **cap** on its rim.

Each set of lugs passes through notches to go together, and those notches are
at **uneven angles** — 0°, 100° and 215° at the bottom, the same pattern
turned 40° at the top to miss the jaw slots. Evenly spaced lugs would line up
with their notches every 120°, including at 120°, the middle of the sweep,
where the body would lift straight off a shut mechanism. Unevenly spaced, the
only rotation lining all three up is none at all, so everything is open at
full open and locked everywhere else. The three cap pegs share that pattern,
so the cap goes on exactly one way round and its spiral cannot be fitted out
of phase with the shell's.

Assembly, all of it at full open:

1. slide both blades into the body's slots from outside;
2. lower the body into the shell — bottom lugs through the lip notches,
   bottom pins into the outer ends of the grooves;
3. drop the cap on — pegs into their holes, hook notches over the body's top
   lugs, top pins into the slots;
4. twist.

It comes apart again at full open, deliberately, and nowhere else.

## Stack

Parametric CAD as code, in Python — `trimesh` with `manifold3d` for booleans,
`shapely` to sweep the spiral slots, and the shared renderer in
`../3d-tools/`. No GUI, no OpenGL.

| | |
| --- | --- |
| `params.py` | every dimension, as a chain of derivations; heights come from `stack(grip_length)` |
| `scroll.py` | the cam: spiral, kinematics, slopes |
| `parts.py` | the four printed parts, plus the fit coupon |
| `test_fit.py` | 54 design checks |
| `build.py` | STLs into `stl/`, renders into `renders/` |

Heights are a function of the grip length rather than constants, so the
short-grip test piece is the same model with one argument changed rather than
a second model to keep in step.

## How to run

```bash
cd twist-grip
python3 -m pip install -r requirements.txt

python3 scroll.py        # the mechanism's numbers, on one screen
python3 test_fit.py      # 54 checks — run this after editing params.py
python3 build.py         # every STL and render   (~40 s)
python3 build.py --stl   # STLs only
python3 build.py --fast  # quarter-res renders
```

Everything dimensioned lives in `params.py`. Change a number there, run
`test_fit.py`, rebuild. See `print-guide.md` before printing.

## Where it stands

**Modelled and checked; no filament spent.** All 54 checks pass, and the ones
worth having interrogate the finished meshes rather than the numbers that
made them: a 40 mm cylinder passing clean through all 104 mm of the open
object, no interference between any two of the five parts at five twist
angles, both ends of a blade reaching into their plates, the body blocked
from lifting by its lugs, the cap blocked by its hook, and the whole thing
coming apart at full open on purpose.

Defects the checks caught, none of which a drawing would have shown:

- **The cap was not held down at all.** Its hook sat *above* the body's top
  lugs, so lifting the cap moved it further from the thing meant to stop it.
  It has to hook *under* them — which has to happen in the 6.5 mm of annulus
  between the bore and the start of the spiral, and that is why the body's
  tube is three different diameters up its height.
- **Every groove was in the wrong place.** The arcs were placed at the jaw
  angles instead of the jaw angles less the sweep, putting each pin 48 mm
  from the groove meant to drive it. The ring looked right either way,
  because the two grooves together are symmetric under a half turn — the
  solid is identical and only the kinematics disagree.
- **The groove ends cut through the pin.** A flat 2° end pad put a third of
  the pin through the end wall of its own groove at the inner end.
- **A 0.35 mm wall**, from measuring the shell's inner wall out from the bore
  instead of from the lip actually in the way. The whole chain was rewritten
  so each radius derives from the one that forces it.
- **The body lifted off at 120°**, with evenly spaced lugs. Hence the uneven
  angles, and hence 120° being in the test list.
- **A clearance derived twice disagreed with itself**, giving a blade 0.6 mm
  of float where 0.3 was meant.
- **A check that lied.** The one asserting a blade's two pins share an axis
  failed on a correct part: slicing exactly on a face leaves zero-volume
  slivers in the boolean, and `.centroid` is area-weighted, so the slivers
  dragged the answer 9 mm off while the volume stayed exactly right. It now
  slices inside the pins and uses the volume centroid.

What software cannot tell us is the fit. Everything that slides here is
plastic on plastic at a clearance that is currently a guess. `stl/coupon-*`
is the same mechanism with the grip cut to 25 mm and a 50° wedge taken out of
it — 34 g against 364 — carrying every fit at once: pin in groove at both
ends, blade in slot, lugs under both hooks, body turning in the shell's bore.
Print that first.

## Open questions

- **Is 115 × 104 mm too big in the hand?** It is a tin. The 2:1 lever gets
  the diameter to about 80 mm; nothing gets the height down except a shorter
  grip.
- **Does one twist still feel right over 90 mm?** The blades now have ten
  times the contact area they had as pads, so the friction against a finger
  is far higher while the cam is unchanged. The coupon will say.
- **Flat faces, or cradled?** They are flat, because the brief says the
  pieces touch and flat faces touch over their whole area. A concave blade
  would hold a finger far better over 90 mm, and would then meet only at its
  edges.
- **Nothing stops it at full open.** It can be pulled apart there by design.
- **The shell is a lot of plastic** — 142 cm³ of the 286. A cage of three
  columns between two rings would use a third of that and show the
  mechanism, at the cost of a worse thing to hold.
- **Nothing is chamfered.** Every edge is square. The blade edges and the
  bore mouth both want breaking before this is nice to hold.
