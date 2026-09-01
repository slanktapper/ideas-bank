# What a new month tab looks like

Captured from **`Sept2026 - Var Expenses`** on **2026-08-31 MDT**, the day it was
created and before a single receipt went into it. This is the blank template every
month starts from, and it is what the script is built and tested against.

The machine-readable copy is `apps-script/test/fixtures/blank-month-tab.json`. The
tests build their fake sheet from it, so the geometry below is not a description of
the code's assumptions — it is the thing the code is checked against.

## The grid

Twenty columns wide. Rows 1–4 are the month's summary, row 5 is the header, rows
6–125 are where receipts go.

| Row | A | B | C | D | M | N … T |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | | | | | | *(blank)* |
| 2 | | | | `= Bought for the other person expense not shared` | `Budget` | 300, 500, 250, 500, 1, 1, 470 |
| 3 | *total for the month* | `Total Expenses for the month` | | | `Actual` | *spent per category* |
| 4 | `Shared (+ owes -)` | *what he is owed* | *what she is owed* | | `Ratio` | *actual ÷ budget* |
| 5 | `Description` | `Paid by Rob` | `Paid by Danielle` | `Date` | `Error` | `Transportation`, `Groceries`, `Restaurant`, `Entertainment`, `Camping`, `Dog`, `Home` |
| 6–125 | *(blank)* | *(blank)* | *(blank)* | *(blank)* | | formula per row, showing `0` |

Columns E and F on the header row are `Category` and `Card`. Rows 6–125 are
completely empty across A–F — all 120 of them, identically.

## The formulas are the point

Every one of those 120 rows already carries a formula in each of N–T. Each one asks
"is this row's category mine?" and, if so, adds that row's amount into the column —
which is what rows 3 and 4 total up, and what the budget comparison in row 4 is
measured against.

A row **appended below 125** has no such formula. It would look completely normal in
the sheet and count for nothing. That single fact is why the script finds the first
blank row *inside* rows 6–125 and writes into it, and why it refuses to write at all
once they are used up.

## Capacity

120 receipts in a month. August 2026 used five of them, so this is not a limit
anyone is likely to reach — but the script checks rather than assumes, and says so
plainly if a month ever fills up.

## What the script takes from this tab at run time

Nothing here is hard-coded in `Config.gs`. Every run, from the tab itself:

- **the header row** — found by looking for `Description` in column A within the
  first twelve rows;
- **which column is which** — by header text, so `Paid by Rob` and `Paid by
  Danielle` are located rather than assumed to be B and C. A tab missing either one
  is not treated as a month tab at all;
- **the categories** — read from the header cells to the right of `Card`, skipping
  `Error`. These become the list of categories Claude is allowed to choose from, so
  the sheet decides what a valid category is, not the code;
- **how far the formulas go** — by reading the formulas in column N.

The consequence: renaming a category, adding one, or extending the formulas further
down the sheet all just work, with no code change. Moving the header row or renaming
`Description` would not, and the script would say so rather than write to the wrong
place.

## Recapturing this

If the sheet's shape changes, update `apps-script/test/fixtures/blank-month-tab.json`
from a freshly created month tab and run `node test/logic-test.js`. The tests read
their geometry from the fixture, so they will fail exactly where the script's
assumptions no longer hold.
