# twist-grip

**Status:** prototype — modelled, checked, nothing printed yet

## What it is

A fidget that traps a finger. A 40 mm hole goes straight through a 113 mm
disc; twist the fluted ring round the outside and two jaws come in from
opposite sides and close on whatever is in the hole. Twist it all the way and
the two faces meet on the axis. Twist it back and they retreat flush with the
bore, leaving a clean 40 mm circle.

It is a two-jaw scroll chuck, which is how a lathe holds work: the ring
carries two spiral grooves, a pin under each jaw rides one of them, and the
jaw can only move radially because its channel holds it. Half a turn of the
ring is the whole range.

## Why

A finger trap you operate rather than one that operates on you. The appeal is
that it is a real mechanism — the resistance you feel is a cam, not a spring —
and that it holds wherever you leave it.

The spiral is shallow enough to be self-locking: 7.6° at the outer end and
12.8° at the inner, against about 17° for PETG on PETG. Pressing outward on a
jaw cannot unwind the ring, so the thing stays where you set it with nothing
sprung, nothing ratcheted and nothing to wear out.

## Scope

**What it does.** Two jaws, driven in and out together, by twisting. A clear
40 mm bore when open, faces touching when shut, and a positive stop at both
ends.

**What it deliberately does not do.**

- **Measure anything.** No scale, no detents, no numbers on the ring. Where
  you leave it is where it stays, and that is the whole interface.
- **Grip hard.** The pads are flat and 8.6 mm wide. This closes on a finger;
  it is not a vice, and nothing in it is sized for real clamping loads.
- **Come apart in use.** It also does not need a tool, a screw or glue to go
  together — see **How it holds together**.
- **Fit a pocket.** See the next section. It is a desk object.

## The size is not a styling choice

113 mm across, 16 mm tall. That falls out of the brief rather than being
chosen, and the chain is short enough to check:

1. A face flush with a 40 mm bore that ends on the axis travels **20 mm**.
   Both of those are in the brief, so the travel is not adjustable.
2. The cam pin cannot be in front of its face, and the groove cannot cross
   the finger hole. Bore, turning fit, the lip that holds the object
   together, and one wall between that and the groove put the pin's inner
   limit at **r = 28**.
3. So the pin sweeps **r 28 to 48**, and a jaw's tail reaches **r = 52.5**
   when open, which the body plate has to stay under.
4. The ring has to be outside all of that, because it is the part you twist.

Shrinking it means giving up one of the three fixed things, or putting a 2:1
lever between pin and jaw so 10 mm of pin travel gives 20 mm of jaw travel.
That would bring it to about 80 mm, at the cost of two more moving parts and
two more pivots to print and fit. It is the first thing to try if the object
turns out to be too big in the hand — see **Open questions**.

## How it works

`scroll.py` is the mechanism; everything else is housing.

The two jaws sit 180° apart, so as the ring turns through φ each pin moves
backwards through the ring's own frame by φ. Over a sweep of exactly 180°,
one jaw's pin covers ring angles 180°→0° and the other's 360°→180°: the two
halves of the face, with no overlap. Both grooves are then the same spiral
arc, one placed at 0° and one at 180°, and wherever they share an angle they
are a full 20 mm apart in radius. A half turn is also one wrist movement,
which is the reason to want it anyway.

The spiral is Archimedean — radius linear in angle — so the jaws close at a
constant 0.111 mm per degree. Anything else would make the closing speed
change as you turn, which feels like something binding.

Each groove ends in a flat pad, so a pin runs onto a dead stop rather than
into a wedge it can jam in. The pads are **not** a fixed angle: the groove's
end cap is square to its path, so the pin's centre has to stop a pin radius
short of it *measured along the arc* — 6.4° at the inner end, 3.8° at the
outer.

## How it holds together

No screws, no glue, no snap fits. The body's skirt drops through the ring's
bore and carries three lugs that hook under a lip inside the ring. The lugs
pass through notches in that lip to go together.

The notches are at **0°, 100° and 215°** rather than every 120°. Evenly
spaced lugs line up with their notches every 120° — including at 120°, the
middle of the sweep, where the body would lift straight off a shut mechanism.
Unevenly spaced, the only rotation that lines all three up at once is none at
all, so the notches are open at full open and nowhere else. That is also
where it is meant to come apart, which is how it goes together.

Assembly: slide both jaws into their channels, bring the ring up over the
skirt with the lugs through the notches and the pins into the outer ends of
the grooves, then twist. The cam holds the jaws in radially from the moment
the pins are in, and the lip holds the body down from the moment the ring
leaves full open.

## Stack

Parametric CAD as code, in Python — `trimesh` with `manifold3d` for booleans,
`shapely` to sweep the spiral slots, and the shared renderer in
`../3d-tools/`. No GUI, no OpenGL. The same approach `cantstop` uses, chosen
again here rather than inherited: every part is one solid cut out of another,
which is exactly what boolean CAD is for.

| | |
| --- | --- |
| `params.py` | every dimension, as a chain of derivations |
| `scroll.py` | the cam: spiral, kinematics, slopes |
| `parts.py` | the three printed parts, plus the fit coupon |
| `test_fit.py` | 51 design checks |
| `build.py` | STLs into `stl/`, renders into `renders/` |

## How to run

```bash
cd twist-grip
python3 -m pip install -r requirements.txt

python3 scroll.py        # the mechanism's numbers, on one screen
python3 test_fit.py      # 51 checks — run this after editing params.py
python3 build.py         # every STL and render   (~35 s)
python3 build.py --stl   # STLs only              (~2 s)
python3 build.py --fast  # quarter-res renders
```

Everything dimensioned lives in `params.py`. Change a number there, run
`test_fit.py`, rebuild. See `print-guide.md` before printing.

## Where it stands

**Modelled and checked; no filament spent.** All 51 checks pass, and the ones
worth having are the ones that interrogate the finished meshes rather than
the numbers that made them: a 40 mm cylinder passing clean through the open
assembly, no interference between any two parts at seven twist angles, the
jaw blocked from lifting by its lid, the body blocked from lifting by its
lugs at five angles, and coming apart at full open on purpose.

Defects the checks caught, none of which a drawing would have shown:

- **Every groove was in the wrong place.** The arcs were placed at the jaw
  angles instead of the jaw angles less the sweep, putting each pin 48 mm
  from the groove meant to drive it. The ring looked perfectly right either
  way, because the two grooves together are symmetric under a half turn — the
  solid is identical and only the kinematics disagree. Caught by walking the
  pin along its own groove through the sweep.
- **The groove ends cut through the pin.** A flat 2° end pad looked generous;
  at the inner end, where the arc is shortest, it put a third of the pin
  through the end wall of its own groove. The pad has to be a pin radius of
  arc, which is a different angle at each end.
- **The ring's inner wall was 0.35 mm.** Measured outward from the bore
  instead of from the lip that is actually in the way. The whole dimension
  chain was rewritten so each radius derives from the one that forces it, and
  the walls are now checked rather than intended.
- **The body lifted off at 120°.** Three evenly spaced lugs, three notches,
  and a 180° sweep: the notches came back round in the middle of the travel.
  Hence the uneven spacing, and hence the 120° case in the test list.
- **A clearance derived twice disagreed with itself.** The channel lid was
  specified by thickness, giving the jaw 0.6 mm of float where 0.3 was meant,
  because the jaw rides on the ring's face rather than the plate's underside.
  The lid is now positioned from the jaw it has to retain.

What software cannot tell us is the fit. Everything that slides here is
plastic on plastic at a clearance that is currently a guess: 0.35 mm on the
sliding faces and the turning bearing, 0.30 where things only need to miss
each other. `stl/coupon-*.stl` exists for exactly that — a 50° wedge of the
real object, cut from the finished meshes rather than built to resemble them,
about 19 g and well under half an hour. It carries all four fits at once: pin
in groove, jaw in channel, lug under lip, ring on skirt. Print that before
the 145 g set.

## Open questions

- **Is 113 mm too big in the hand?** The honest answer needs the coupon and
  then the whole thing on a desk. If it is, the 2:1 lever gets it to about
  80 mm.
- **Flat pads, or cradled?** They are flat, because the brief says the pieces
  touch and flat faces touch over their whole area. A concave pad would hold
  a finger better and would then meet only at its edges.
- **Nothing stops it at full open.** The ring can be pulled off there by
  design. A sprung tab on the body clicking into the ring's wall would make
  that deliberate rather than available, at the cost of a flexure to print.
- **The channels are open slots when shut.** From r≈32 outward they show the
  ring's grooves underneath. It looks mechanical rather than wrong, but a
  cover plate would tidy it.
- **The jaws drag on the ring's face.** They ride directly on it, so the ring
  turning under them adds friction. That is probably a feature — it is what
  gives the twist some weight — but it is not a decision anyone made yet.
- **Nothing is chamfered.** Every edge is square. The pad edges and the bore
  mouth both want breaking before this is nice to hold.
