# expenses

**Status:** prototype

## What it is
Photograph a receipt, email it to yourself, and have the expense show up as a row in
the shared household spreadsheet — vendor, amount, date, category — without any
typing. A Google Apps Script runs on a timer, picks up anything Gmail has labelled
`receipts`, sends the photo to Claude to read, and writes one row into the right
month's tab of **DNR finances 2024**.

## Why
The sheet only works if every purchase gets entered, and entering them is the part
that doesn't happen. A receipt in a pocket is a row that never gets typed. Taking a
photo at the till and forgetting about it is a habit that can actually be kept.

## Scope
What this does:

- Watches one Gmail label for photos of receipts (and PDF receipts).
- Reads each one with Claude's vision API: vendor, total, date, category.
- Appends a row to the correct month tab of the existing spreadsheet, using the
  categories that tab already defines, in the existing column layout.
- Refuses to guess. Anything it is not confident about — unreadable total, missing
  date, non-CAD currency, no matching month tab — is relabelled `receipts/needs-review`
  and left for a human. It never writes a half-read receipt.
- Never edits a row it did not create, never edits a formula, never adds a column.

What this deliberately does not do:

- **It does not own the spreadsheet.** The sheet belongs to Danielle and is shared;
  its layout, its budgets and its formulas are hers. This project writes six cells
  per receipt into the blank rows already ruled and formulated for that purpose, and
  nothing else. If the sheet's shape needs to change, that is a conversation with a
  person, not a change to this code.
- No OCR of its own, no receipt line items, no per-item breakdown — one receipt, one
  row, the way the sheet already works.
- No categorisation model of its own: the allowed categories are read out of the
  month tab's header row at run time, so the sheet stays the source of truth.
- No app, no server, no hosting. If it can't be done from a timer-driven Apps Script,
  it isn't in scope.
- Not a general expense tracker, not a tax tool, not a receipt archive — the labelled
  email thread is the archive.

## Stack
- **Google Apps Script** (V8 runtime), standalone — a project in Rob's own account,
  not bound to the spreadsheet, because the spreadsheet is owned by someone else.
- **Gmail** as the intake: a filter puts the label `receipts` on the mail; the script
  only ever reads mail carrying that label.
- **Claude Messages API** (`claude-opus-5`) over `UrlFetchApp`, with vision image
  input and structured JSON output (`output_config.format`). No SDK — Apps Script has
  no package manager, so it's raw HTTPS.
- **Google Sheets** via `SpreadsheetApp.openById`.
- API key lives in Script Properties. It is never in this repo, and there is no
  `.env` to leak.

Running cost is roughly a cent or two per receipt at Opus 5 rates ($5 / $25 per
million input / output tokens) — a receipt photo is a small image and a ~200-token
answer.

## How to run
Read `month-tab-template.md` first if you are touching the sheet-writing code — it is
the shape everything here is built against.

There is nothing to run on this machine — the code runs in Google's cloud. See
`setup.md` for the one-time install, verbatim. In short:

1. Create a standalone Apps Script project, paste in the files from `apps-script/`.
2. Put the Anthropic API key in Script Properties as `ANTHROPIC_API_KEY`.
3. Run `checkSetup()` once — it reports on the key, the spreadsheet, the labels and
   the tab it would write to today, and creates the labels if they are missing.
4. Run `installTrigger()` once to start the 15-minute timer.
5. Mail a receipt photo to `rob.sinclair.bb+receipt@gmail.com`.

The logic that picks the tab, picks the row, and decides what is safe to file is
plain JavaScript and is tested — `cd expenses/apps-script && node test/logic-test.js`,
no dependencies. The Gmail and Claude halves are only exercised by mailing yourself a
real receipt.

Day to day: photograph the receipt, share it to Gmail, send to
`rob.sinclair.bb+receipt@gmail.com`. Within fifteen minutes the row is in the sheet
and the mail is relabelled `receipts/filed`. Check `receipts/needs-review`
occasionally for the ones it wouldn't guess at.

## The spreadsheet this writes to
`DNR finances 2024`. Two kinds of tab matter here, and the script only ever writes to
one of them:

- **The variable expense tabs**, one per month — `Sept2026 - Var Expenses`,
  `Aug2026 - Var Expenses`, `Jul2026 - Var Expenses`, and so on back through 2024.
  These are the month-by-month record of what was actually spent, and the only thing
  this script touches. `month-tab-template.md` describes exactly what a fresh one
  looks like, captured from the September tab the day it was made.
- **`85K salary shared exp new`** — the standing plan: income, the fixed monthly bills
  (mortgage, insurance, phone, internet), the budget each variable category is
  measured against, and how the two of them split it. Nothing recurring gets a
  receipt photographed, so nothing here is ever written by this script. It is a
  different shape entirely — no `Description` / `Paid by Rob` header row — so it
  cannot be picked as a write target even by accident.

Every variable expense tab has the same shape:

| | A | B | C | D | E | F | … | M | N … T |
|---|---|---|---|---|---|---|---|---|---|
| row 5 | Description | Paid by Rob | Paid by Danielle | Date | Category | Card | | Error | Transportation, Groceries, Restaurant, Entertainment, Camping, Dog, Home |

Rows 6 to 125 are the expense rows — 120 of them, each already carrying the formulas
in columns N–T that fan its amount out into the category totals at the top. **That is
why the script writes into an existing blank row rather than appending one** — an
appended row falls outside the formulas, looks perfectly normal, and counts for
nothing.

The script finds the month tab by name — `Aug2026 - Var Expenses` parses as August
2026, and so do `Aug 2026`, `August 2026` and `2026-08` — and failing that by looking
for a tab that already holds dates in that month. It never creates a tab: a receipt
for a month with no tab yet goes to `needs-review`.

## Open questions
- **Which column does a receipt land in?** Currently always `Paid by Rob` (column B),
  since the receipts come from Rob's phone. Splitting a shared receipt, or filing one
  Danielle paid, is still manual.
- **Who makes next month's tab, and when?** The script never creates one, and until
  the month's tab exists its receipts wait in `needs-review` — they file themselves
  on the next run once it appears. September's was made by hand on 2026-08-31 and is
  a clean template: formulas intact, entries cleared. Whether October's arrives the
  same way, or wants a `newMonthTab()` helper here, is the open part.
- Should a filed row link back to the receipt photo? It would need a new column in
  someone else's sheet — deliberately not done. The `receipts/filed` label is the
  archive for now.
- Does Rob have edit access to the shared sheet, or only view? The Drive API only
  shows the owner from this side. If writes fail with a permission error, that is why.
- HEIC photos: iPhone mail usually converts to JPEG, but if a HEIC arrives the API
  can't read it and the mail goes to `needs-review`. Worth seeing whether it ever
  actually happens before building a conversion step.
