# twist-grip — print guide

Read this before spending filament. Nothing here has been printed yet, so
everything below is reasoning from `../available-tools.md` and the geometry,
not experience with this part.

## Print the coupon first

```
stl/coupon-shell.stl   50° wedge, 25 mm grip   14 g
stl/coupon-body.stl                             2 g
stl/coupon-cap.stl                              8 g
stl/coupon-jaw.stl                             10 g
```

About 34 g all told, against **364 g and the better part of a day** for the
real set. It is the same mechanism with the grip cut from 90 mm to 25 and a
50° wedge taken out of it — cut from the finished meshes rather than modelled
to resemble them, so the walls, the groove floor and every overhang are
exactly what the full part would print.

It carries every fit that matters:

| fit | clearance as drawn | what wrong feels like |
| --- | --- | --- |
| pin in groove, both ends | 0.35 mm each side | gritty, or slop you can hear |
| blade in slot | 0.35 mm each side | blade rocks, or will not slide |
| lugs under lip and hook | 0.30 mm | body or cap rattles up and down |
| body in the shell's bore | 0.35 mm | wobbles instead of turning true |

Assemble the wedge and run the blade through its 25° or so of travel. If it
binds, raise `FIT_SLIDE` in `params.py` by 0.05 and reprint the coupon; if it
is sloppy, lower it. Then rebuild and print the real thing.

**The coupon answers one more question the full part cannot afford to get
wrong:** whether a blade driven from both ends still slides sweetly when the
two pins are a print tolerance apart. That is the whole reason there are two
scroll plates, and the only way to find out is to feel it.

## Material

**PETG**, from the five colours on the shelf. It is the functional default
for good reasons here: it slides on itself without the galling PLA does, it
is tough enough for a pin in a groove taking a side load, and — the one that
decides it — **it does not creep**. This object is meant to be squeezed and
left squeezed, which is precisely the load that makes PLA sag over days in a
warm room.

ABS would also do and has the chamber for it, but there is one colour of it
and no reason to spend the chamber's time.

Suggested colours, all on hand: **black** shell and cap, **white** body,
**orange** blades. The blades are the moving part and want to read as
separate — and with a 40 mm bore you see a lot of them. Any pairing works.

**Quantities.** One shell, one body, one cap, and **two** blades from the one
`jaw.stl`.

## Orientation

All three print flat, no supports, nothing to clean up.

| part | orientation | why |
| --- | --- | --- |
| shell | as modelled, floor down | every cavity opens to the sky; 101 mm of thin tube, so watch it is stuck down |
| body | as modelled, standing on its skirt | 104 mm tall, 50 mm across — brim it |
| cap | **turned over** | the pocket under its hook ring then opens upward instead of overhanging 5 mm inward |
| jaw | **turned over** | see below |

`build.py` already writes them in these orientations — load the STLs as they
come and do not let the slicer "optimise" them.

**The blades are the one part needing support, and which way up decides
where.** A blade has a pin at each end pointing opposite ways, so whichever
way it stands one pin points down and the arm above it hangs in air. Printed
**upside down**, that support lands under the *top* arm, which touches
nothing in use — while the one face that does bear on something, the
underside of the bottom arm riding on the shell's floor, prints as a top
surface, and the pin that runs in the shell's groove prints as a clean
vertical cylinder. Printed the other way up you get the support scar on the
bearing face instead. Support on build plate only, 4.3 mm of it.

Other overhangs, all small and all fine in PETG:

- the three lugs on the skirt and the three at the top stand about 1.6 mm
  proud, printing as short ledges over air;
- the shell's inner lip juts 1.6 mm inward at z = 3.8;
- the cap's hook ring, once the cap is turned over, prints flat.

None of those is a bearing surface, so ragged is cosmetic.

## Settings

Nothing exotic. 0.4 mm nozzle, 0.2 mm layers.

- **Walls: 4.** The thinnest wall in the object is 1.6 mm, which is exactly
  four lines, so it wants to be solid perimeter rather than thin infill.
- **Infill: 25%+.** The ring and body are mostly plate; the jaws are small
  enough to print solid and should be, since the pin is cantilevered.
- **Blades: print two.** `stl/jaw.stl` is one blade; the mechanism needs two
  identical ones. Print them solid — each pin is a cantilever.
- **Tall thin parts.** The shell is 101 mm of 3 mm wall and the body 104 mm of
  3 mm tube. Brim both, and keep the chamber shut to stop a draught from
  pulling them off the plate.
- Dry filament. PETG strings when damp and this part has slots everywhere for
  strings to land in.

## Assembly

No screws, no glue, no tools.

All of it happens at full open — the only angle where the lugs line up with
their notches.

1. Slide both blades into the body's slots from outside, faces inward.
2. Lower the body into the shell: the three bottom lugs through the notches
   in the shell's lip, and the bottom pins into the outer ends of the
   grooves.
3. Drop the cap on: three pegs into their three holes — it only goes on one
   way round — its hook notches over the body's top lugs, and the top pins up
   into the slots.
4. Twist. All three sets of lugs leave their notches at once and it is
   together.

From then on the cam holds the blades radially, the shell's lip holds the
body down, and the body's top lugs hold the cap down. It comes apart again by
twisting back to full open and lifting, which is deliberate and the only
position it is possible in.

## What to look at when it comes off the plate

- **The bore.** A 40 mm circle, clear all 104 mm through, with both blades
  flush with it at full open. If a blade stands proud it is not reaching its
  outer stop.
- **Cocking.** Push one blade in by hand at the top only, then at the bottom
  only. It should not tilt noticeably either way: that is what the second
  scroll plate is for, and if it tilts the cap is not keyed tightly enough to
  the shell.
- **The sweep.** Half a turn, stopping positively at both ends. It should
  stop because a pin met the flat end of its groove, not because something
  wedged.
- **Holding.** Press on a jaw face with the ring part way round. It should
  not unwind; the spiral is shallow enough to lock on friction alone. If it
  creeps, the surfaces are more slippery than the 0.3 assumed and the design
  wants a detent.
- **The faces meeting.** Twisted all the way over, the two blades should land
  flat against each other down their whole 90 mm, not touching at one end
  first. Meeting at the top or bottom first means the blades are cocked.
