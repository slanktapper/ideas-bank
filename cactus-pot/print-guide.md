# Printing it

Numbers that are not in `params.py` because they are slicer settings rather
than geometry. Machine is the H2D; see `../available-tools.md`.

## The parts

| File | How many | Notes |
| --- | --- | --- |
| `stl/cactus.stl` | 1 | 187 mm tall, stands on the flat end of its spigot |
| `stl/spikes-x72.stl` | 2 plates | 108 sockets, so print a few spare |
| `stl/spike.stl` | — | the single part, to arrange your own plate |
| `stl/fit-test-coupon.stl` | 1 | **print this first** |
| `stl/test-print-wedge.stl` | 1 | **and this second** — 150° of the real trunk |

## Print the coupon first

The coupon has seven holes stepping 0.06 mm either side of the modelled
socket. Print it with the same filament, nozzle and flow you will use for the
cactus, print a handful of spikes alongside it, and push a spike into each
hole.

What you want is the hole a spike enters with firm thumb pressure and stays
in when the coupon is turned over. If that is the middle hole, the model is
right. If it is one of the others, change `SOCKET_COMP` in `params.py` by that
hole's step and rebuild — the step is marked by its position, leftmost is
−0.18 mm, rightmost is +0.18.

Doing this costs about fifteen minutes and three grams. Not doing it risks
81 sockets at the wrong size on a part that takes most of a day.

## Then the wedge

The coupon settles one number. The wedge settles whether the joint works on
the surface it will actually live on, which is not the same question: a socket
in the cactus is drilled at 34° into a curved, ribbed wall, so it breaks out
through a crest, its mouth is an ellipse rather than a circle, and the layers
closing over it are bridging. None of that happens in a flat block.

`test-print-wedge.stl` is 150° of the real trunk between z=25 and z=70 — same
ribs, same pads, same eleven sockets at their real rake, printed standing up
exactly as the cactus is. About 45 g and under two hours.

What to look at when it comes off:

- Does a spike seat with the same thumb pressure it took in the coupon? If it
  is tighter here, the socket's elliptical mouth is the reason and
  `SOCKET_MOUTH_CHAMFER` is the dial.
- Is the mouth clean, or did the bridge over it sag into the hole? A sag is
  what `SOCKET_RELIEF_L` is for, and it can grow.
- Pull a seated spike out sideways. It should resist and then break the pad
  before it slips, not slide out.
- And the part nobody measures: stand back and look at it. Eleven spines at
  the real spacing is the first honest view of what 108 will look like.

## The cactus

- **Orientation:** as exported, standing on the flat end of the spigot. Do not
  tilt it; the ribs and the socket mouths are all better for being printed
  upright. The first 10 mm above the spigot is a 45° flare out to full width,
  so nothing down there needs bridging — and all of it ends up inside the pot.
- **Supports:** needed under the two arms only — about 4% of the part. Tree
  supports, or a PETG interface under a PLA body for breakaway supports from
  filament already on the shelf.
- **Walls:** 3 perimeters. The sockets are bored 3.4 mm into the skin and the
  pin has to bite on solid plastic, not on sparse infill.
- **Infill:** 10–15% is plenty. It is decorative and the spigot carries it.
- **Layer:** 0.20 mm. Finer buys little here — the ribs are 3.6 mm deep.
- **Material:** PLA for the look, PETG if it will sit in a window. PLA at 60 °C
  will droop on a sunny sill; the arms are the part that will show it.

## The spikes

- **Orientation:** as exported, standing on the pin, point up. No supports.
  Every layer is smaller than the one below except the collar, which bridges
  0.5 mm off the pin and needs nothing.
- **Walls:** as many perimeters as the slicer will fit. At Ø1.86 the pin wants
  to be solid plastic; set infill to 100% for this plate, it costs nothing.
- **Speed:** slow the outer wall right down, 30 mm/s or so. The tip is one
  extrusion wide and the toolhead is turning a 0.4 mm circle at the top of
  every spike; at normal speeds that is where they go furry.
- **Colour:** white, jade white or the milky pink read as spines against a
  green body. Black looks like a sea urchin, which may be the point.

## Seating them

Dry fit, no glue. Push the pin in square, not at an angle — the socket is
raked, so follow the hole rather than the surface. The collar lands on the
areole pad and that is the stop; if a spike will not go the last half
millimetre, it is a blob in the hole bottom, so clear it rather than pushing
harder. A spike at Ø1.86 shears before the socket does.

Work from the crown down, so a seated spike is never in the way of your hand.

## In the pot

The cactus drops into the Ø32 socket in the pot's floor and lands on the floor
itself, not on the bottom of the hole. It lifts straight out again — the fit is
0.35 mm of clearance per side, because a 220 mm assembly is a long lever and a
press fit down there would be a wrestling match every time the pot is cleaned.

If it rocks, the culprit is elephant's foot on the cactus's first layer, not
the socket. Scrape the bottom edge of the spigot's flange rather than reaming
the pot.
