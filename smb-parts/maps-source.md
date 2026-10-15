# smb-parts — map source

Where the level maps come from. Recorded 2026-10-15 MDT.

## The source

Ian Albert's *Super Mario Bros.* map collection — full levels stitched together from
screenshots, at 1:1 game pixels:

<https://ian-albert.com/games/super_mario_bros_maps/>

The two URLs Rob gave, which anchor the set:

- first — World 1-1: <https://ian-albert.com/games/super_mario_bros_maps/mario-1-1.gif>
- last — World 8-4: <https://ian-albert.com/games/super_mario_bros_maps/mario-8-4.gif>

## ⚠ Nothing below has been verified against a real file

**No map has been downloaded.** This session's network policy denies
`ian-albert.com` — `curl` gets a 403 at the egress proxy, and the fetch tool cannot
resolve the host at all. So:

- the filename pattern is **inferred from the two URLs above**, not confirmed
- whether all 32 files exist on that pattern is **unconfirmed**
- no image's **pixel dimensions have been measured**, and none should be quoted as
  fact from this file until one has been

The two things here that are *not* guesses are facts about the game itself: SMB has
8 worlds of 4 levels each, and its tiles are 16 × 16 px on a playfield 15 tiles tall.

Clear this warning once the maps are in hand and measured.

## Inferred pattern

```
https://ian-albert.com/games/super_mario_bros_maps/mario-<world>-<level>.gif
```

with `<world>` 1–8 and `<level>` 1–4 — 32 files.

| Level | Inferred URL |
| --- | --- |
| 1-1 | `mario-1-1.gif` |
| 1-2 | `mario-1-2.gif` |
| 1-3 | `mario-1-3.gif` |
| 1-4 | `mario-1-4.gif` |
| 2-1 | `mario-2-1.gif` |
| 2-2 | `mario-2-2.gif` |
| 2-3 | `mario-2-3.gif` |
| 2-4 | `mario-2-4.gif` |
| 3-1 | `mario-3-1.gif` |
| 3-2 | `mario-3-2.gif` |
| 3-3 | `mario-3-3.gif` |
| 3-4 | `mario-3-4.gif` |
| 4-1 | `mario-4-1.gif` |
| 4-2 | `mario-4-2.gif` |
| 4-3 | `mario-4-3.gif` |
| 4-4 | `mario-4-4.gif` |
| 5-1 | `mario-5-1.gif` |
| 5-2 | `mario-5-2.gif` |
| 5-3 | `mario-5-3.gif` |
| 5-4 | `mario-5-4.gif` |
| 6-1 | `mario-6-1.gif` |
| 6-2 | `mario-6-2.gif` |
| 6-3 | `mario-6-3.gif` |
| 6-4 | `mario-6-4.gif` |
| 7-1 | `mario-7-1.gif` |
| 7-2 | `mario-7-2.gif` |
| 7-3 | `mario-7-3.gif` |
| 7-4 | `mario-7-4.gif` |
| 8-1 | `mario-8-1.gif` |
| 8-2 | `mario-8-2.gif` |
| 8-3 | `mario-8-3.gif` |
| 8-4 | `mario-8-4.gif` |

All 32 share the directory above, so the table lists bare filenames to stay readable.

## Getting them, when that is wanted

Either route works; neither has been taken yet.

1. **Allow the domain.** Add `ian-albert.com` under Network access → Allowed domains
   in the environment's settings, leaving "Allow package managers" ticked. Then a
   session can pull all 32 and measure them. Steps:
   <https://code.claude.com/docs/en/cloud-environments#network-access>
2. **Commit them by hand.** Download locally and add them to this folder. Note the
   repo has no large-file handling set up, and these are reportedly big images.
