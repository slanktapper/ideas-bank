# smb-parts — map source

Where the level maps come from, and what they actually are. Measured 2026-10-15 MDT.

## The source

Ian Albert's *Super Mario Bros.* map collection — full levels stitched together from
screenshots, at 1:1 game pixels:

<https://ian-albert.com/games/super_mario_bros_maps/>

Rob downloaded the set and committed all 50 files to `maps/` on 2026-10-15 MDT. Every
figure below was read from those files, not inferred.

## What is here: 50 GIFs, three kinds

`./fetch-maps.sh --check` regenerates all of this on demand.

### The 32 main levels

Every one is **224 px tall**. Widths in tiles are px ÷ 16.

| Level | File | Width px | Tiles | Bytes |
| --- | --- | --- | --- | --- |
| 1-1 | `mario-1-1.gif` | 3384 | 211.5 | 22343 |
| 1-2 | `mario-1-2.gif` | 3056 | 191.0 | 20696 |
| 1-3 | `mario-1-3.gif` | 2632 | 164.5 | 20389 |
| 1-4 | `mario-1-4.gif` | 2560 | 160.0 | 14360 |
| 2-1 | `mario-2-1.gif` | 3416 | 213.5 | 28010 |
| 2-2 | `mario-2-2.gif` | 3078 | 192.4 | 26512 |
| 2-3 | `mario-2-3.gif` | 3800 | 237.5 | 25154 |
| 2-4 | `mario-2-4.gif` | 2561 | 160.1 | 15221 |
| 3-1 | `mario-3-1.gif` | 3416 | 213.5 | 27580 |
| 3-2 | `mario-3-2.gif` | 3560 | 222.5 | 22111 |
| 3-3 | `mario-3-3.gif` | 2616 | 163.5 | 18597 |
| 3-4 | `mario-3-4.gif` | 2561 | 160.1 | 14709 |
| 4-1 | `mario-4-1.gif` | 3816 | 238.5 | 23486 |
| 4-2 | `mario-4-2.gif` | 3584 | 224.0 | 22716 |
| 4-3 | `mario-4-3.gif` | 2552 | 159.5 | 20782 |
| 4-4 | `mario-4-4.gif` | 3072 | 192.0 | 15212 |
| 5-1 | `mario-5-1.gif` | 3400 | 212.5 | 23036 |
| 5-2 | `mario-5-2.gif` | 3416 | 213.5 | 27087 |
| 5-3 | `mario-5-3.gif` | 2632 | 164.5 | 20794 |
| 5-4 | `mario-5-4.gif` | 2561 | 160.1 | 16172 |
| 6-1 | `mario-6-1.gif` | 3224 | 201.5 | 19894 |
| 6-2 | `mario-6-2.gif` | 3672 | 229.5 | 27640 |
| 6-3 | `mario-6-3.gif` | 2872 | 179.5 | 18176 |
| 6-4 | `mario-6-4.gif` | 2560 | 160.0 | 15149 |
| 7-1 | `mario-7-1.gif` | 3080 | 192.5 | 27054 |
| 7-2 | `mario-7-2.gif` | 3078 | 192.4 | 27512 |
| 7-3 | `mario-7-3.gif` | 3800 | 237.5 | 26253 |
| 7-4 | `mario-7-4.gif` | 3584 | 224.0 | 14791 |
| 8-1 | `mario-8-1.gif` | 6232 | 389.5 | 41233 |
| 8-2 | `mario-8-2.gif` | 3672 | 229.5 | 28440 |
| 8-3 | `mario-8-3.gif` | 3672 | 229.5 | 27976 |
| 8-4 | `mario-8-4.gif` | 5889 | 368.1 | 39333 |

### 13 area maps — the rooms off the main levels

Also all 224 px tall, so they share the level geometry.

| File | Width px | Tiles | Bytes |
| --- | --- | --- | --- |
| `mario-bonusarea-a.gif` | 256 | 16.0 | 3370 |
| `mario-bonusarea-b.gif` | 256 | 16.0 | 3685 |
| `mario-bonusarea-c.gif` | 256 | 16.0 | 3542 |
| `mario-bonusarea-d.gif` | 256 | 16.0 | 3479 |
| `mario-bonusarea-e.gif` | 256 | 16.0 | 3262 |
| `mario-bonusarea-f.gif` | 1031 | 64.4 | 12916 |
| `mario-bonusarea-g.gif` | 1031 | 64.4 | 12899 |
| `mario-bonusarea-h.gif` | 1248 | 78.0 | 4357 |
| `mario-bonusarea-i.gif` | 1505 | 94.1 | 4939 |
| `mario-bonusarea-j.gif` | 1024 | 64.0 | 12108 |
| `mario-bonusarea-k.gif` | 1505 | 94.1 | 4909 |
| `mario-underground-end.gif` | 568 | 35.5 | 6113 |
| `mario-underground-transition.gif` | 256 | 16.0 | 3076 |

The five 256 px ones are single-screen rooms — 256 px is exactly 16 tiles, one
NES screen wide.

### 5 files that are not maps at all

`mario-all-*.gif` are 4:3 and 5:4 screen sizes, and they are the only files in the
set that are not 224 px tall. They are **wallpapers** of the whole game, not level
data. Do not feed them to anything that expects a level.

| File | Size | Aspect |
| --- | --- | --- |
| `mario-all-640.gif` | 640 × 480 | 1.33 |
| `mario-all-800.gif` | 800 × 600 | 1.33 |
| `mario-all-1024.gif` | 1024 × 768 | 1.33 |
| `mario-all-1280.gif` | 1280 × 1024 | 1.25 |
| `mario-all-1600.gif` | 1600 × 1200 | 1.33 |

## What the measurements changed

Three things in earlier versions of this file were wrong. Corrected:

**The playfield is 14 tiles tall, not 15.** Every level and area map is exactly
224 px high, and 224 ÷ 16 = 14.0 exactly. This file previously asserted a 15-tile,
240 px playfield as a "fact about the game". It is not what these maps are. Anything
sizing a part off the height should use **14 tiles**.

**The files are small.** All 50 together are **1.63 MB** on disk and 31 megapixels
summed. This file previously warned they might be in the 100–900 megapixel range and
asked whether Git LFS was needed. It is not: they are indexed-palette GIFs and they
compress hard. **The size question is settled — committed as ordinary blobs, no LFS,
no `.gitignore`.**

**Widths are mostly not tile-aligned.** Only **6 of the 32** levels have a width
divisible by 16. Twenty are 8 px over — half a tile — and a few are 1 or 6 px over
(`mario-2-4`, `mario-3-4`, `mario-5-4` and `mario-8-4` are all 1 px over; `2-2` and
`7-2` are 6 px over). Two area maps are odd numbers of pixels wide. This is stitching
slop, and it matters: **a slicer that assumes an exact 16 px grid will not line up.**
Snap to the grid and decide deliberately what happens to the leftover column.

## Level lengths, for scale

| | Level | Width | Tiles |
| --- | --- | --- | --- |
| longest | mario-8-1.gif | 6232 px | 389.5 |
| shortest | mario-4-3.gif | 2552 px | 159.5 |

The 32 levels come to 6688 tiles end to end. At 10 mm per tile the longest single
level is 3.90 m long and 140 mm tall, which is the number that decides whether a
whole-level piece is a wall or a shelf.

## Re-fetching from the source

The naming is now confirmed for the main levels:

```
https://ian-albert.com/games/super_mario_bros_maps/mario-<world>-<level>.gif
```

`./fetch-maps.sh --fetch` pulls those 32. It needs `ian-albert.com` to be reachable —
this session's network policy denied it (403 at the egress proxy, 32 attempts, no
partial files), which is why Rob supplied the files by hand. To enable it: add
`ian-albert.com` under Network access → Allowed domains in the environment's settings
(cloud environment menu in the title bar, then Edit), leaving "Allow package managers"
ticked. Steps: <https://code.claude.com/docs/en/cloud-environments#network-access>

Note that `--fetch` only knows the 32 main levels. The 13 area maps and 5 wallpapers
came from the site's own page and are not on that pattern; re-fetching the whole set
means reading the index page for the real links.
