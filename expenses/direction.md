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

- Watches one Gmail label for photos of receipts, PDF receipts, and — when there is
  nothing attached — bills and payment notices where the email itself is the record.
  An ATCO bill notice with an amount and a due date in the body is filed the same way
  a photograph of a till receipt is.
- Reads each one with Claude's vision API: vendor, total, date, category.
- Dates a bill by **when it comes due** — the day the money leaves on a preauthorized
  plan, and the month tab it therefore belongs on. That is the one case where a date
  in the future is allowed, up to two months out; anything further is treated as a
  misread. A payment already made is dated when it was made, a receipt when it was
  bought.
- **Won't file the same thing twice.** Same description, same amount, same day, same
  column already on the tab means the mail goes to needs-review instead. A forwarded
  bill notice is easy to send twice, and a bill counted twice is money that does not
  exist.
- Works out **who paid** from the sending address — Rob's mail goes in his column,
  Danielle's in hers, from either of her addresses — unless the email says otherwise
  in words ("Danielle paid this one"), which wins. Both of them can mail receipts to
  the same address.
- Appends a row to the correct month tab of the existing spreadsheet, using the
  categories that tab already defines, in the existing column layout.
- Follows the sheet's **not-shared convention**: something bought for the other
  person at their request goes in doubled, written as `=34.95*2` so the real amount
  is still there when you click the cell, and highlighted yellow. Only ever when the
  email says so.
- Refuses to guess. Anything it is not confident about — unreadable total, missing
  date, non-CAD currency, no matching month tab, mail from an address it doesn't
  recognise — is relabelled `receipts/needs-review` and left for a human. It never
  writes a half-read receipt.
- Never edits a row it did not create, never edits a formula, never adds a column.

What this deliberately does not do:

- **It does not own the spreadsheet.** The sheet belongs to Danielle and is shared;
  its layout, its budgets and its formulas are hers. This project writes six cells
  per receipt into the blank rows already ruled and formulated for that purpose, and
  nothing else. If the sheet's shape needs to change, that is a conversation with a
  person, not a change to this code.
- No OCR of its own, no receipt line items, no per-item breakdown — one receipt, one
  row, the way the sheet already works.
- It does not read your mail. It sees one Gmail label and nothing else, so a bill only
  reaches it if it is forwarded there deliberately. Account numbers, card numbers and
  payment links are explicitly kept out of the sheet.
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

`node test/dry-run.js` answers "what would this email do to the sheet?" — it runs the
real script against a fake mailbox and a fake tab and prints the row it would write.
Only the model's answer is canned, in `test/cases/`.

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
| row 4 | Description | Paid by Rob | Paid by Danielle | Date | Category | Card | | Error | Transportation, Groceries, Restaurant, Entertainment, Camping, Dog, Home |

Rows 5 to 164 are the expense rows — 160 of them, each already carrying the formulas
in columns N–T that fan its amount out into the category totals at the top. **That is
why the script writes into an existing blank row rather than appending one** — an
appended row falls outside the formulas, looks perfectly normal, and counts for
nothing. Full detail, including the two quirks in the sheet worth knowing about, is
in `month-tab-template.md`.

## Shared, or bought for the other person
Everything is split 50/50 by default. The exception is something one of them buys
*for* the other at their request — the purse Rob bought Danielle — which is not
shared: she owes the whole of it.

The sheet's way of expressing that, named in the legend at the top of every month
tab, is to enter **twice the amount** and highlight the cell. Half of double is the
whole, so the split arithmetic lands on the right figure with no special case. It
goes in as a formula, `=34.95*2`, not as `69.90`, so clicking the cell still shows
what was actually spent.

The script does this only when the email says so — "a purse for Danielle", "she asked
me to grab this". A photograph of a receipt cannot tell you who a purchase was for,
and most purchases are shared, so silence means shared. Something bought for the
person who paid is an ordinary purchase, not a doubling.

## Who paid
Two columns, `Paid by Rob` and `Paid by Danielle`, and every receipt goes wholly into
one of them. Which one is decided in this order:

1. **What the email says.** The whole message goes to the model along with the
   receipt, and it decides for itself whether the message names a payer. It does not
   have to be a set phrase: "Danielle paid this", "she got this one", "on my card",
   "D covered it" all count, and first-person words are resolved against whoever
   sent it — the model is told who that is. It reports the payer and, in a few
   words, what it read that from, which goes into the log and the digest so a wrong
   call is visible after the fact rather than silent. The reason is not checked
   against the text: requiring the words to match exactly is what stopped the
   ordinary way people write from working. The one thing refused is a payer read out
   of an email with no message in it at all.
2. **The sending address.** `rob.sinclair.bb@gmail.com` is Rob;
   `danielle.lucas5@gmail.com` and `chickami@hotmail.com` are Danielle. Both of them
   mail receipts to the same `+receipt` address; the From line is what separates them.
3. **Neither** — an address nobody claims, and nothing in the email saying who paid.
   That goes to `needs-review`, named in `Config.gs` so adding an address is one line.

The email is shown to the model to be read, not obeyed. It is told so, and its answer
is confined by the schema to the two names — so the worst an email can do is put a
receipt in the wrong column, which the log names and a person can move.

The script finds the month tab by name — `Aug2026 - Var Expenses` parses as August
2026, and so do `Aug 2026`, `August 2026` and `2026-08` — and failing that by looking
for a tab that already holds dates in that month. It never creates a tab: a receipt
for a month with no tab yet goes to `needs-review`.

## Bills and payment notices
Not everything that costs money comes with a photograph. Forwarding a bill notice —

> Hi ROBERT, your ATCO Energy bill for CAD 119.82 on acct …, is due 15 Sep, 2026.

— files `Atco  $119.82  15/09/2026  Home` the same way a receipt photo would. When
nothing is attached, the email body **is** the record, and it goes to the model on its
own; when something is attached, the attachment is the record and the email is only
read for who paid.

The date is the day the bill comes due, because on a preauthorized plan that is the
day the money actually leaves — and it is what decides the month tab. So a notice
arriving on 28 August for a 15 September due date lands in September, where the
payment falls. The row therefore appears before the money has moved, which is
deliberate: a budget wants to know what is coming.

Note that these arrive addressed to Rob from the biller, so they have to be
**forwarded** to the `+receipt` address for the From line to be one the script knows.
Auto-labelling the biller's mail instead would work too, but then the biller's address
has to be added to a payer's `senders` in `Config.gs`, which is the same as saying
"anything from ATCO is Rob's".

## Open questions
- **Splitting one receipt** — half shared, half not — is still manual. A receipt goes
  wholly into one column, either shared or doubled.
- **A bill notice and its payment confirmation are two emails about one expense.**
  The duplicate check catches them only if the description, amount and date all match,
  which they often won't — a bill due the 15th and a confirmation dated the 15th
  would, a confirmation dated the 16th would not. Worth watching before building
  anything cleverer.
- **A bill filed early is a row for money that has not moved yet.** If the amount
  changes, or the payment fails, nothing here notices.
- **How far to trust what the email says.** The model's reading of the message
  overrides the sending address, and its stated reason is recorded but not verified.
  That is the deliberate trade for handling the way people actually write; the cost
  is that a genuinely ambiguous message — "she got this one" in a thread with three
  people in it — is taken at face value. Whether the log is enough of a check, or
  this eventually wants the payer echoed back in a reply, is open.
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
