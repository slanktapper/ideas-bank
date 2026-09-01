# What a month tab looks like

Read out of the workbook itself — exported as `.xlsx` — on **2026-09-01 MDT**, so
this is formulas and fills, not a text rendering of them. An earlier version of this
file was taken from a text export and had the rows off by one; this replaces it.

The machine-readable copy is `apps-script/test/fixtures/blank-month-tab.json`, and
the real tab names are in `tab-names.json` beside it. The tests build their fake
sheet from both, so what follows is not a description of the code's assumptions — it
is the thing the code is checked against.

## The grid

Twenty columns wide. Rows 1–3 are the month's summary, **row 4 is the header**, and
**rows 5–164** are where receipts go.

| Row | A | B | C | D | M | N … T |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | | | | `= Bought for the other person expense not shared` | `Budget` | pulled from `Variable Expenses History` |
| 2 | `=sum(B5:B163)+SUM(C5:C164)` | `Total Expenses for the month` | | | `Actual` | `=SUM(N$5:N$164)` per category |
| 3 | `Shared (+ owes -)` | `=$A$2/2-SUM(B5:B164)` | *hers, the mirror of it* | | `Ratio` | actual ÷ budget |
| 4 | `Description` | `Paid by Rob` | `Paid by Danielle` | `Date` | `Error` | `Transportation`, `Groceries`, `Restaurant`, `Entertainment`, `Camping`, `Dog`, `Home` |
| 5–164 | *(blank)* | *(blank)* | *(blank)* | *(blank)* | error check | `=IF(N$4=$E5,$B5+$C5,0)` per row |

Columns E and F on row 4 are `Category` and `Card`. The blank entry rows are empty
across A–F but already **formatted**: B and C carry `"$"#,##0.00`, D carries
`M/d/yyyy`. So a plain number and a real Date written into them come out looking
like every other row, with no formatting work.

## The formulas are the point

Every one of those 160 rows already carries a formula in each of N–T. Each asks "is
this row's category mine?" and, if so, adds the row's amount into the column — which
is what rows 2 and 3 total up, and what the budget comparison is measured against.

A row **appended below 164** has no such formula. It would look completely normal in
the sheet and count for nothing. That single fact is why the script finds the first
blank row *inside* rows 5–164 and writes into it, and why it refuses to write at all
once they are used up.

## Bought for the other person

The legend in D1 — `= Bought for the other person expense not shared` — is a
convention, and it is worth spelling out because it looks like a typo and is not.

When one of them buys something *for* the other, at their request, it is not a shared
expense: the other owes the whole of it, not half. The sheet's arithmetic splits
everything 50/50, so the way to make that come out right is to **enter twice the
amount**. Half of double is the whole, and row 3 lands on the correct figure with no
special case anywhere.

It is entered as a **formula, not a doubled number**:

```
B5 =34.95*2        displays $69.90, highlighted solid yellow (#ffff00)
A5 Danielle purse
```

Written that way, clicking the cell still shows what was actually spent — `34.95` —
with the doubling visible as `*2` rather than hidden inside a number nobody can
check. The script does the same, and sets only the background, so the cell keeps its
currency format (the hand-entered one lost it and shows `69.9`).

The script only ever does this when the **email says so** — "a purse for Danielle",
"she asked me to grab this". A receipt cannot tell you who a purchase was for, and
groceries the household eats are not it. Bought for the person who paid is an
ordinary purchase, not a doubling.

## Capacity

160 receipts in a month. August 2026 used five, so this is not a limit anyone is
likely to reach — but the script checks rather than assumes, and says so plainly if a
month ever fills up.

## What the script takes from the tab at run time

Nothing here is hard-coded in `Config.gs`. Every run, from the tab itself:

- **the header row** — found by looking for `Description` in column A within the
  first twelve rows. It is row 4 here; the script does not care which row it is;
- **which column is which** — by header text, so `Paid by Rob` and `Paid by
  Danielle` are located rather than assumed to be B and C. A tab missing either one
  is not treated as a month tab at all;
- **the categories** — read from the header cells to the right of `Card`, skipping
  `Error`. These become the list Claude is allowed to choose from, so the sheet
  decides what a valid category is, not the code;
- **how far the formulas go** — by reading the formulas in column N.

The consequence: renaming a category, adding one, or extending the formulas further
down the sheet all just work, with no code change. Moving the header row or renaming
`Description` would not, and the script would say so rather than write to the wrong
place.

## Two quirks in the sheet, noted not fixed

Neither is this project's to change — the spreadsheet belongs to someone else — but
both are worth knowing:

- **The month total is one row short on his side.** `A2` sums `B5:B163` but
  `C5:C164`. A receipt on row 164 paid by Rob would not reach the monthly total. The
  script stops where the category formulas stop, which is row 164, so this only bites
  at 160 receipts in a month.
- **Rows 9 and below reference another tab.** Their category formulas read
  `'Oct2025 - Var Expenses'!N$4` instead of their own `N$4` — an artefact of the tab
  having been copied. They agree only because both tabs' headers say the same words.
  Renaming a category on one tab and not the other would make those rows quietly
  wrong.

## Recapturing this

Export the spreadsheet as `.xlsx` and read it, rather than reading a text rendering —
that is how the off-by-one crept in the first time. Update
`apps-script/test/fixtures/blank-month-tab.json` and run `node test/logic-test.js`.
The tests read their geometry from the fixture, so they fail exactly where the
script's assumptions no longer hold.
