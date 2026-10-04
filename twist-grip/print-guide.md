# twist-grip — print guide

Read this before spending filament. Nothing here has been printed yet, so
everything below is reasoning from `../available-tools.md` and the geometry,
not experience with this part.

## Print in this order

Three prints, each one answering the question the next one would otherwise
waste filament discovering.

### 1. The fit comb — 27 g, under half an hour

```
stl/comb-grooves.stl   73 x 33 x 7 mm    17.5 g
stl/comb-springs.stl   64 x 22 x 18 mm    8.5 g
stl/comb-pin.stl       12 x 12 x 9 mm     0.8 g
```

Two numbers in `params.py` are guesses only a printer can settle, and both
are expensive to get wrong later:

- **`FIT_SLIDE`, the clearance everything slides on.** `comb-grooves` carries
  five arcs of the real spiral — taken from its inner end, where it curves
  most tightly and a round pin binds soonest — cut at 0.25, 0.30, 0.35, 0.40
  and 0.45 mm. Try `comb-pin` in each; the notches beside each arc count
  which is which, 1 to 5. Keep the tightest that still slides sweetly along
  the whole arc, and put it in `params.py`.
- **The pawl post's thickness, which sets how hard the click is.** `comb-
  springs` has four posts at 0.8, 0.9, 1.0 and 1.1 mm, each with a stop
  exactly 0.8 mm away — which is precisely the deflection a tooth asks for.
  Press each until it meets its stop. Keep the one that feels like a firm
  button rather than a vague squish or a wall, and set
  `POST_R_OUT - POST_R_IN` to it.

Then `python3 test_fit.py && python3 build.py` and move on.

### 2. The fit coupon — 77 g, about two hours

```
stl/coupon-shell.stl   120° wedge, 25 mm grip   33 g
stl/coupon-body.stl                              5 g
stl/coupon-cap.stl                              20 g
stl/coupon-jaw.stl                              17 g
```

The same mechanism with the grip cut from 90 mm to 25 and a 120° wedge taken
out of it — wide enough to take in a slot WALL and not just the slot, because
a 26 mm blade's slot is 84° of the bore on its own. Cut from the finished
meshes rather than modelled to resemble them, so the walls, the groove floor
and every overhang are exactly what the full part would print.

It carries every fit at once:

| fit | clearance as drawn | what wrong feels like |
| --- | --- | --- |
| pin in groove, both ends | 0.35 mm each side | gritty, or slop you can hear |
| blade in slot | 0.35 mm each side | blade rocks, or will not slide |
| lugs under lip and hook | 0.30 mm | body or cap rattles up and down |
| body in the shell's bore | 0.35 mm | wobbles instead of turning true |
| the ratchet | 0.8 mm of tooth | vague click, or one that will not turn |

And it answers the question the comb cannot: **whether a blade driven from
both ends still slides sweetly when the two pins are a print tolerance
apart.** That is the whole reason there are two scroll plates, and the only
way to find out is to feel it.

### 3. The real thing — 374 g, the better part of a day

Only once the coupon moves the way it should.

## Material: PETG, and the reason is the spring

Both are on the shelf and either would *work*, so this is a judgement rather
than a rule. It comes down to one part.

**The pawl post is a living spring in a fidget.** It gets flexed 0.8 mm every
click, eighteen clicks a close, and a fidget is a thing people click
hundreds of times an evening. It is a cantilever printed standing up, so the
bending load falls across its layer lines — which is precisely how PLA
fails: it is stiff and notch-sensitive, and a repeatedly flexed PLA cantilever
cracks at the root and snaps. PETG is tougher and far more fatigue-tolerant,
and that is the normal reason printed flexures are made from it.

PLA is also about 1.75× stiffer, so the same post that needs ~2 N in PETG
needs ~3.5 N in PLA — a click that is less satisfying and a release you have
to lean on.

The secondary reasons both point the same way: PETG does not creep, and this
is a thing meant to be squeezed and left squeezed; and the pins are 5 mm
cantilevers taking side loads, where PLA's brittleness is the wrong property.

**Where PLA would genuinely be better**, for honesty's sake: it prints small
features more crisply, which matters here (a 1.4 mm nose, 0.8 mm teeth), it
is more dimensionally stable over a 115 mm part, and it slides on itself
more happily — PETG on PETG is notoriously grabby, and this mechanism has a
lot of sliding plastic.

So: **PETG throughout, including the test prints.** Validate in the material
you will build in — PETG prints slightly fatter than PLA, so clearances
measured in one do not transfer to the other, and transferring them is the
entire point of the comb.

**If the twist comes out grabby**, the fix is one experiment rather than a
redesign: reprint the shell and cap in PLA and leave the body and blades in
PETG. Almost every sliding pair in this object is body-against-shell, so
that makes them dissimilar plastics, which slide better than like on like —
and the spring stays in the material it needs.

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

### The blade: upright with pins on, or flat with pins loose

Two files, same part, pick one.

**`jaw.stl` — upright, pins moulded on.** Both pins print as vertical
cylinders, so the four surfaces that bear against the groove walls are
printed as walls, which is the best surface the machine makes. Needs a
4.3 mm support block under the top arm, and that arm touches nothing in the
assembly, so the scar does not matter. 34 x 26 footprint, 99 mm tall, so
brim it.

**`jaw-flat.stl` — flat, with the pins as separate dowels on the same
plate.** The blade lies on its contact face: rib and both arms rise straight
off the face plate, so the blade needs **no support at all**, prints three
times faster, and sits rock solid on 26 x 90 mm of bed. The pins come off and
become three 5 x 9.3 mm dowels standing beside it, where a cylinder is the
most accurate thing a printer makes. Two per blade; the third is a spare.

- The sockets are **teardrops**, not round holes: lying flat their axis is
  horizontal, and the roof of a horizontal round hole droops into the bore.
  A 45 degree peak over the circle is self-supporting and the round dowel
  never touches it.
- They are **blind, 5 mm deep in a 6 mm arm**, so a dowel bottoms out and
  the 4.3 mm that stands proud is set by the geometry, not by how hard you
  pressed.
- Press a dowel home dry. If it fights, a few strokes of sandpaper down its
  length; if it is loose, a drop of CA. Printing two blades gives you six
  dowels for the four you need, so there is room to experiment.

A dowel pressed home rebuilds the moulded-on blade exactly — same bounding
box, and lighter only by the 13 mm3 of socket-roof relief the round dowel
does not fill. `test_fit.py` checks that, so the two files cannot drift
apart.

**If you print `jaw.stl` upright, that is the one part needing support, and
which way up decides where.** A blade has a pin at each end pointing opposite ways, so whichever
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
4. **Press and hold the release pad** on top of the post as the cap goes
   down. The pawl's nose stands proud of the tooth crests, so the collar
   cannot pass it otherwise.
5. Twist. All three sets of lugs leave their notches at once, and the
   ratchet starts clicking.

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
- **The click.** 10° a turn, 18 of them over the sweep. It should click
  going closed and refuse to go back until you press the pad. If it clicks
  but will not hold, the nose is not reaching its valley; if it will barely
  turn, the post is too stiff — thin it by 0.1 mm and reprint the body.
- **The faces meeting.** Twisted all the way over, the two blades should land
  flat against each other down their whole 90 mm, not touching at one end
  first. Meeting at the top or bottom first means the blades are cocked.
