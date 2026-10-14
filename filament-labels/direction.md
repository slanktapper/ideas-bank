# filament-labels

**Status:** prototype

## What it is

Three tags that say **PLA**, **PETG** and **ABS**, to tape to the side of the bins
the filament lives in. Each is an 80 × 30 × 3.0 mm rounded slab in two colours:
a jade white background with the word in black, indigo purple or cocoa brown.
At 3 mm it is a plaque rather than a sticker — rigid, no flex, nothing for a
knocked corner to peel back.

They print face down, so the face you read is the one that was against the plate
and carries its texture. The lettering is not engraved or raised — it is the
second filament coming through the white, flush with the surface, so there is no
relief to catch dust and nothing to rub off.

The models are generated from `build.py`; there is no mesh to edit by hand. Change
a number in `params.py` and every tag follows, lettering included.

## Why

Rob's filament holders have no way of saying what is in them. A bin of white
filament is a bin of white filament whether the white is PLA or PETG, and the two
want different temperatures, different bed prep and different expectations about
what the part will do at 70 °C. The label has to survive being handled, so a
printed tag beats a paper one; and since the printer has eight slots, a two-colour
tag costs an evening on the plate rather than a trip to a label maker.

## Scope

**It does:** three tags, one per material, at one size, generated from one set of
parameters. Colour and material come from `../filament.md`, which is the only
stock list. It also lays out a plate, because these are printed in batches of one
type — 24 fit, and a batch costs no more purge than a single tag does.

**It deliberately does not:**

- Carry anything but the material name. No temperatures, no brand, no colour
  swatch, no QR code. A bin label is read from across a workshop, and every extra
  thing on it costs letter height.
- Mount. It is taped on. No clips, no magnets, no hooks — those depend on the bin,
  and the bin is not modelled here.
- Cover materials that are not on the shelf. There is no ASA, TPU, PVA, PC or
  nylon tag, because `../filament.md` says there is none of it to put in a bin.
  Adding one is a row in `params.py`.

## The two decisions worth knowing

**Everything is PLA, including the tag that says PETG.** The letter colours Rob
asked for — indigo purple and cocoa brown — exist only in PLA. The white he asked
for exists only in PETG: `../filament.md` is explicit that there is no plain white
PLA, and that the white in stock is PETG. Those two cannot be one part.
`../available-tools.md` notes that PLA and PETG barely bond, and leans on exactly
that to make breakaway supports — so a PLA letter set into a PETG tag is a part
designed to shed its lettering. The whole set is PLA, and the background is jade
white, which is the only pale PLA on the shelf. A tag reading "PETG" printed in
PLA is a label, not a sample, so this costs nothing.

**The white is the thin part, and that is why it is 0.80 mm.** Rob asked for the
white to be a skin so the jade white spool lasts, and suggested two layers. Two
layers is 0.40 mm, and a pale filament over a dark one at 0.40 mm reads grey. The
working minimum is about 0.60 mm, and bright white over black — the ABS tag — wants
0.80 mm. Printing face-down makes it worse rather than better: the first layer is
squashed into the plate texture, so in the valleys the skin is thinner than its
nominal 0.20 mm. So the skin is 4 layers, with the letter colour filling the
remaining 2.20 mm behind it.

Thickness is the one number that does not touch this. The skin is set by opacity,
so making the tag thicker spends letter colour and no more jade white at all: the
white has stayed at 5.6 g through every version.

The saving is still most of what was asked for: the white went from the whole tag
to a skin, 9.5 g down to 5.6 g across the three. `build.py` prints what 2, 3, 4 and
5 layers each cost, so dropping to 3 is one number away if the black tag turns out
to be fine at 0.60 mm.

## Stack

Python 3.10+, `numpy` + `trimesh` with the `manifold3d` boolean engine, `shapely`
for the 2D work. Lettering comes from `../3d-tools/text3d.py` and renders from
`../3d-tools/render.py`. No GUI, no CAD application.

`text3d.py` and the Outfit Bold typeface were moved into `../3d-tools` for this
project — they were `cactus-pot`'s, and a second consumer is what the shared folder
exists for. The pot's STL is unchanged by the move, byte for byte, which is how
that was checked.

    python3 -m pip install -r requirements.txt

## How to run

    python3 build.py                # stl/ and renders/
    python3 build.py --no-renders   # just the STLs, a couple of seconds
    python3 test_fit.py             # 42 checks, about 2 seconds

`print-guide.md` is what to do with the files once they exist.

## The numbers that matter

| | |
| --- | --- |
| `TAG_W`, `TAG_H`, `TAG_T` | 80 × 30 × 3.00 mm — 15 layers at 0.20 |
| `WHITE_D` | 0.80 mm of jade white, 4 layers, on the printed face |
| `COLOUR_BEHIND` | 2.20 mm of letter colour behind the skin |
| `CORNER_R` | 4.0 mm, so a knocked corner does not lift the tape |
| cap height | 18.12 mm, solved — not set by hand. See below |
| `MARGIN_X`, `MARGIN_Y` | 7.0 and 5.0 mm of clear tag around the word |
| `BED_W`, `BED_D` | 300 × 320 mm — the **dual-nozzle** envelope, 24 tags a plate |

**The cap height is solved, and "PETG" is what solves it.** All three words are set
at one size, the largest at which the widest of them still fits the panel, so the
set reads as a set. At 80 mm wide that size is 18.12 mm, and it is the *width* of
PETG that binds — the height would allow 19.40. Make the tag narrower and all three
words shrink together; make it taller and nothing changes until height becomes the
binding constraint.

The three also share a baseline, because each word is centred on its cap box rather
than on its ink. ABS and PETG have round letters that overshoot the cap line and
baseline by 0.28 mm; PLA does not. Centring on ink would put the three baselines at
three different heights, which is visible when the tags are side by side.

## Open questions

- **Jade white is not white.** It is a soft off-white with a green cast. It should
  look right next to the printed colours, but nobody has held one yet. If it reads
  as dirty rather than as a warm white, the alternative on the shelf is milky pink
  PLA, which is worse, or ordering white PLA.
- **Does 0.80 mm actually hide black?** It should. The first tag printed settles it,
  and the answer is a number in `params.py` either way. Print the ABS tag first —
  black is the worst case of the three.
- **Tape, or something better.** Taped on is what was asked for, and 3 mm makes it
  more of a question than 1.2 mm did: a thicker tag stands further off the bin, so a
  knock has more leverage on the adhesive. Nothing has been changed for it, because
  the tag being rigid also means it will not peel progressively the way a thin one
  does — it either holds or it comes off whole. If it comes off, the cheap fix is a
  3M VHB square; the expensive one is modelling the bin and clipping on.
- **No PETG or ABS tag in its own material.** There is an argument that the PETG tag
  should be printed in PETG so the label is also a sample of the material. It cannot
  be, for the colour reasons above, and it would mean a separate job in a different
  material for one tag. Noted and rejected, not forgotten.
- **How many of each.** Unanswered, and it does not need answering in code: a
  plate holds 24 of one type and the purge is the same at any count, so the number
  is whatever Rob wants on the day. `plate_layout()` fills the plate; printing six
  means deleting eighteen in the slicer.
- **The other bins.** This does three materials because that is what is on the shelf.
  Mistletoe green, silk gold and the rest are colours rather than materials, and a
  colour label is a different idea — probably a swatch, not a word.
