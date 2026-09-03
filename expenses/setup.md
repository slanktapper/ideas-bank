# expenses — setup

One-time install, in order. Everything happens in Rob's Google account; nothing runs
on a laptop. Allow about twenty minutes.

## 1. Gmail: the label and the filter

The script reads exactly one label and nothing else, so this step is what decides
what it can see.

1. Gmail → Settings (gear) → **See all settings** → **Filters and Blocked Addresses**
   → **Create a new filter**.
2. In **To**, put `rob.sinclair.bb+receipt@gmail.com`. Click **Create filter**.
3. Tick **Apply the label** → **Choose label…** → **New label…** → name it `receipts`
   → **Create** → **Create filter**.

Gmail delivers anything addressed to `you+anything@gmail.com` to your normal inbox,
so there is no second account to set up.

**The address is the real boundary, not the label.** The script re-checks the To and
Cc lines of every message and reads only the ones actually sent to
`rob.sinclair.bb+receipt@gmail.com`. Labelling something by hand will not get it
scanned; nor will a reply arriving in a thread you already filed. Dots don't matter
(`robsinclairbb+receipt@gmail.com` is the same address), but the `+receipt` tag
does. To change or add an address, edit `CONFIG.RECEIPT_ADDRESSES`.

One consequence worth knowing: **Bcc is invisible** on a received message, so a
receipt blind-copied to the address cannot be recognised and is left alone. Put the
address in To or Cc. The `receipts/filed` and
`receipts/needs-review` labels are created for you in step 5.

**Danielle uses the same address.** Anything she sends to
`rob.sinclair.bb+receipt@gmail.com` from `danielle.lucas5@gmail.com` or
`chickami@hotmail.com` lands in the same label and is filed under her column — the
From line is what separates the two of them. Mail from any other address goes to
`needs-review`; adding an address is one line in `CONFIG.PAYERS`.

## 2. An Anthropic API key

1. Go to <https://console.anthropic.com/> → **API Keys** → **Create Key**.
2. Copy it. It is shown once.

Keep it out of this repository. It goes into Script Properties in step 4, which is
the only place it should ever be typed.

## 3. The Apps Script project

1. Go to <https://script.google.com/> → **New project**.
2. Rename it (top left) to `expenses — receipt filer`.
3. **Project Settings** (gear, left) → tick **Show "appsscript.json" manifest file in
   editor**.
4. Back in **Editor**, create one file per file in `apps-script/` and paste the
   contents in:
   - `appsscript.json` already exists — replace its contents.
   - `Config.gs`, `Claude.gs`, `Sheet.gs`, `Gmail.gs`, `Main.gs` — **+** → **Script**
     for each, named without the `.gs` (the editor adds it).
   - `test/logic-test.js` is **not** pasted in — it runs on a laptop, not in Apps
     Script. See the end of this file.
5. Save (⌘S / Ctrl+S).

Prefer the command line? `npm i -g @google/clasp`, `clasp login`,
`clasp create --type standalone --rootDir apps-script`, `clasp push`.

## 4. The API key goes in Script Properties

**Project Settings** → **Script Properties** → **Add script property**:

| Property | Value |
| --- | --- |
| `ANTHROPIC_API_KEY` | the key from step 2 |

## 5. Check it, and authorize

In the editor, choose **checkSetup** from the function dropdown and click **Run**.

The first run asks for permission. Google will warn that the app is not verified —
that is expected for a script you wrote yourself: **Advanced** → **Go to expenses —
receipt filer (unsafe)** → **Allow**. It is asking for Gmail, Sheets, and outbound
network access, which is what the script does.

Then read the **Execution log**. It should say something like:

```
API key: set (sk-ant-a…)
Spreadsheet: "DNR finances 2024"
Tab for 2026-09: "Sept2026 - Var Expenses"
  categories: Transportation, Groceries, Restaurant, Entertainment, Camping, Dog, Home
  Rob: column 2 ("Paid by Rob"), mail from rob.sinclair.bb@gmail.com
  Danielle: column 3 ("Paid by Danielle"), mail from danielle.lucas5@gmail.com, chickami@hotmail.com
  next receipt would go to row 11
Label "receipts": present
Label "receipts/filed": created
Label "receipts/needs-review": created
Timer: not installed — run installTrigger()
```

Anything that says MISSING or NOT FOUND, fix before going on — see Troubleshooting.

## 6. If the month tab was not found

The sheet's own naming — `Aug2026 - Var Expenses` — is understood as it is, so this
step is usually not needed. Two things will trip it:

- **The month's tab doesn't exist yet.** Nothing to configure; the tab has to be made
  (see step 6a).
- **A tab is named something the pattern can't read.** Run **listTabs** — it prints
  every tab and whether the script recognises it as a month tab — then put the exact
  name in `Config.gs`:

  ```js
  TAB_OVERRIDES: { '2026-09': 'Sept 2026 variable' },
  ```

  The key is `YYYY-MM`. Or rename the tab to match the convention, which needs no
  code change at all. Either way, run `checkSetup` again.

### 6a. Each new month

The script never creates a tab. Until the month's tab exists, its receipts pile up in
`receipts/needs-review` — they are not lost, and they file themselves on the next run
once the tab is there. `Sept2026 - Var Expenses` was made on 2026-08-31 and is ready.

A new tab needs two things, both belonging to whoever maintains the sheet — this
project deliberately doesn't reshape someone else's spreadsheet:

- the category formulas in columns N–T carried down the rows, or there is nowhere
  valid to write;
- last month's entries cleared out, if it was made by copying.

`../month-tab-template.md` describes exactly what a correct blank month looks like.

## 7. Start the timer

Run **installTrigger** once. From then on `processReceipts` runs every fifteen
minutes. To stop it, run **removeTriggers**.

## 8. Try it

Photograph a receipt, share it into Gmail, send it to
`rob.sinclair.bb+receipt@gmail.com`. Then either wait fifteen minutes or run
**processReceipts** by hand and read the log.

What should happen: a row appears on the current month's tab — description, amount in
the sender's column, date, category — and the mail is relabelled `receipts/filed`. The
log names who it filed it under and why:

```
Filed No Frills $51.24 under Rob (sent by rob.sinclair.bb@gmail.com) to Sept2026 - Var Expenses row 10
```

Send one with a note in the body — "Danielle paid this one", or just "hers" — and the
log should say `under Danielle (the email: …)` instead. It does not have to be a set
phrase: the whole message goes to the model, which is told who sent it, so "put it on
mine" resolves to the sender and "she got this one" resolves to her.

Say instead that it was **bought for** the other person — "a purse for Danielle, she
asked me to grab it" — and the amount goes in doubled as `=34.95*2` on a yellow
cell, the way the sheet marks an expense that is not shared. The log says
`doubled — bought for Danielle (…)`. See `../month-tab-template.md` for why doubling
is the right answer there.

What happens when it is not sure: the mail is relabelled `receipts/needs-review` and
nothing is written. The log says why. This is the normal outcome for a blurry total,
a receipt in USD, a photo of something that is not a receipt, or a purchase that
doesn't fit any of the sheet's categories.

Optional: set `DIGEST_TO: 'rob.sinclair.bb@gmail.com'` in `Config.gs` to get a short
email listing anything that needed a look. It stays quiet when everything files
cleanly.

## Bills with nothing attached

Forward a bill or payment notice to the same address and it files the same way — the
email body is the record when there is no photo:

> Hi ROBERT, your ATCO Energy bill for CAD 119.82 on acct 7808483721016, is due 15
> Sep, 2026 …

files `Atco  $119.82  15/09/2026  Home`, and the log says
`not yet paid — due 2026-09-15`. It is dated the due date because that is the day the
money leaves on a preauthorized plan, and that is what decides which month tab it
lands on.

It must be **forwarded**, not auto-labelled: the notice comes from the biller, and the
From line is what tells the script whose column it belongs in. If you would rather
have a Gmail filter label ATCO's mail directly, add ATCO's sending address to Rob's
`senders` list in `Config.gs` — which is the same as saying anything from ATCO is his.

Forwarding the same notice twice is safe: a row with the same description, amount,
date and column already on the tab sends the second one to `needs-review` instead.

## Day to day

Photo → share to Gmail → send to `rob.sinclair.bb+receipt@gmail.com`. That is the
whole ritual. Glance at `receipts/needs-review` now and then.

## Troubleshooting

| What the log says | What it means |
| --- | --- |
| `ANTHROPIC_API_KEY is not set` | Step 4 — the property name has to match exactly. |
| `Could not open the spreadsheet` | Either the ID in `Config.gs` is wrong, or this account has view-only access to the sheet. The sheet is owned by Danielle; edit access has to come from her. |
| `no month tab found for 2026-09` | Step 6. |
| `No blank pre-formulated row left` | That month's tab has used up the rows carrying the category formulas. Copy the formulas in columns N–T further down the tab — that is a change to the shared sheet, so it is a conversation, not a code change. |
| `HTTP 401` from the API | The key is wrong or revoked. |
| `HTTP 429` | Rate limited; it retries twice on its own, then leaves the mail for the next run. |
| `looks like it is already on … row N` | The same description, amount and date is already on the tab — a notice forwarded twice, or a re-run. Nothing was written. |
| `not sent to rob.sinclair.bb+receipt@gmail.com` | The thread carries the label but nothing in it was addressed to the receipts address, so nothing was read. Usually a hand-applied label, or the address was in Bcc. |
| `nothing to read: no attachment and no message` | An empty email. Nothing to work from. |
| `date … is N days off and is not a due date` | A receipt or payment dated in the future. Only a bill's due date may be. |
| `mail is from … which is not one of the payers in Config.gs` | The receipt came from an address not listed under `CONFIG.PAYERS`, and nothing in the email said who paid. Add the address, or reply to yourself with a note naming the payer. |
| `Unsupported attachment type: image/heic` | An iPhone sent the original HEIC rather than a JPEG. Re-send it from Photos with "Most Compatible", or take a screenshot of it. |
| Nothing in the log at all | The label is empty — check the filter in step 1 is actually catching the mail. |

## Running the tests

The Google services can't run outside Apps Script, but the logic that decides *which
tab*, *which row*, and *what is safe to file* is plain JavaScript and is tested:

```bash
cd expenses/apps-script
node test/logic-test.js
```

No dependencies, no package manager — just node. Change anything in `Sheet.gs` or the
validation in `Main.gs` and run it before pasting into the editor.

## Asking "what would this email do?"

There is a dry run for exactly that question. It executes the real script — the same
five files you pasted into the editor, unmodified — against a fake Gmail label and a
fake month tab built to the sheet's real geometry, and prints the prompt it would
send, the row it would write, the log, and where the mail would end up:

```bash
node test/dry-run.js                                   # the ATCO bill notice
node test/dry-run.js test/cases/atco-bill-twice.json   # the same notice sent twice
node test/dry-run.js test/cases/labelled-but-not-addressed.json   # labelled, wrong address
```

The one thing it cannot do is call Claude, so each case file carries the reading the
model is assumed to return. Editing that is how you ask "and what if it read it
differently?". Copy a file in `test/cases/` to try your own.
