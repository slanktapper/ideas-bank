# flattener

**Status:** prototype — body, levers and braces printed; jaws not yet

## What it is

A fidget that flattens a finger. A 40 mm bore runs into the front of a 90 mm
body; squeeze the two levers and two jaws come in from opposite sides and
close on **77 mm** of whatever is in the hole. Each jaw face is 26 mm wide,
so between them they take a finger on nearly half its perimeter. Squeeze all
the way and the faces meet on the axis; let go and they retreat flush with
the bore, leaving a clean 40 mm circle.

The hand supplies both the force and the reaction. That is the whole point of
the layout and it is what the design is named for: you are not twisting
something while trying to hold something else still.

## Why

The first version of this idea twisted. A fluted shell turned a two-jaw
scroll chuck, the way a lathe holds work — a spiral groove in a rotating
plate, a pin on each jaw riding it. It was built, checked 88 ways, and
printed, and it did not work, for a reason none of the checks asked about:
**the body you had to hold still was entirely enclosed by the shell you had
to turn.** There was nothing to grip. A mechanism can be correct in every
dimension and still have no way for a person to put a force into it.

Levers fix that by making the reaction internal. Everything after that
followed from one constraint at a time, and the record of it is in the git
history, which is worth more than this paragraph.

## Scope

**What it does.** Two jaws, driven together by a squeeze, holding 77 mm of
finger. A clear 40 mm bore when open, faces touching when shut.

**What it deliberately does not do.**

- **Measure anything.** No scale, no numbers, no detents. The ratchet the
  twist version had has not been brought across.
- **Hold itself shut.** Nothing locks. Let go and it opens.
- **Grip hard.** It closes on a finger. Nothing in it is sized for clamping.
- **Fit a pocket.** 176 × 61 × 138 mm open. It is a desk object.

## How it works

`concept_lever.py` is the whole design; `params.py`, `parts.py` and
`scroll.py` belong to the superseded twist version and are kept because the
lever design still imports dimensions and geometry helpers from the first
two.

**The jaws run on vee rails.** Each jaw carries a 45° vee on each side face,
one near each end and 58 mm apart, running in matching grooves in walls the
body extrudes out beside it. That separation is what holds a jaw square when
a grip bears harder on one end than the other. Forty-five degrees is not a
style choice: it makes the rail's half-height equal its depth, so rail and
groove stay parallel however far either is extended, and it leaves every
flank self-supporting.

**The levers are nutcrackers, not see-saws.** Pivot, then drive, then handle,
in that order along the lever. Put the handle on the far side of the pivot
and a squeeze opens the jaws — a search over 428,730 layouts found 763 that
cleared the body and not one of those closed on a squeeze.

**The pivot is outboard**, at r 66, past the end of the guide wall. That
costs a boss on each wall and buys two things: a brace that reaches across
beside the body instead of wrapping round the entrance, and a longer, more
inclined arm — 18.6° of swing for 20 mm of jaw travel instead of 27.8°, which
is the difference between a 93 mm squeeze and a 68 mm one.

**The drive hole is a slot, not a hole.** The runners hold a jaw to pure
radial travel, so its drive post stays at one height while the lever's hole
swings on an arc about the pivot. Pivot-to-post grows from 38.0 to 42.9 mm
across the stroke and the slot absorbs it. A round hole there binds the jaw
against its own runners.

    bore     40 mm, body 90 mm, jaw face 77 mm
    pivot    r 66, z 8      arm to the drive at z 43, mid jaw
    swing    18.6 deg  ->  20 mm of jaw travel a side
    squeeze  118 mm open -> 50 mm shut, on the grab bar
    parts    7 pieces, 4 distinct, about 179 g at 35% infill

## Stack

Python. `trimesh` with `manifold3d` for the booleans, `shapely` for the swept
outlines, and the renderer in `../3d-tools`. No CAD application, no GUI.

## How to run

```bash
cd flattener
pip install -r requirements.txt
python3 concept_lever.py        # checks, renders, STLs, scale models
```

It runs 49 checks and will not write files quietly if one fails — the exit
code is non-zero. STLs land in `stl-lever/`, deliberately not `stl/`, which
`build.py` wipes on every run.

`print-guide-lever.md` is the one to read before printing. `print-guide.md`
and `stl/` belong to the twist version.

## What the checks are for

Several of them exist because something passed every check that came before
it and was still wrong. Worth keeping in mind before trusting a green run:

- **A jaw can be slid in radially.** Every running check passed on a design
  whose grooves were blind at their outer ends, so no jaw could ever be put
  in.
- **The jaw has real clearance, not coincident faces.** Two surfaces resting
  flush overlap by nothing, so every boolean test passes. Only nudging the
  part finds it.
- **The two sides of the body are tied together.** 20 mm² of material crossed
  the y = 0 plane, holding two walls a squeeze works to prise apart. Nothing
  was asking.

## Open questions

- **Nothing holds it shut.** The twist version had a flat-bottomed ratchet
  and a release pad. Between the two handles, locking-pliers style, is the
  obvious home for one here.
- **The drive web is thin.** 3 mm front-to-back, a quarter of the block it
  replaced. If a jaw racks under a hard squeeze, `DRIVE_WEB_T` is the number
  to raise; 4 or 5 mm still prints clean face-down.
- **The posts need support.** They are horizontal cylinders and have to stay
  round, so they cannot be teardropped — the lever turns on one and slides
  along the other.
- **The braces set the width.** 176 mm overall, from the braces having to
  reach past the lever's outermost sweep. Shortening the guide walls would
  pull it in, at the cost of runner engagement.
- **The twist version is still in the folder.** `build.py`, `scroll.py`,
  `test_fit.py`, `stl/` and `print-guide.md` all still build and pass. They
  are kept for the record and because the lever design imports from
  `params.py` and `parts.py`; retiring them properly means moving those
  imports first.
