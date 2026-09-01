/**
 * Everything tunable lives here. The API key does not — it goes in Script
 * Properties as ANTHROPIC_API_KEY, so it never ends up in source control.
 */
const CONFIG = {
  // "DNR finances 2024". From the sheet's URL:
  // docs.google.com/spreadsheets/d/<THIS PART>/edit
  SPREADSHEET_ID: '1LqSywjtOAsjJDqXkh9Bk0tU3n7U54DWv8D5Jyq4v-i0',

  // Gmail labels. INBOX_LABEL is the only mail the script ever looks at.
  INBOX_LABEL: 'receipts',
  FILED_LABEL: 'receipts/filed',
  REVIEW_LABEL: 'receipts/needs-review',

  // Who paid. The sending address decides, unless the email says otherwise in
  // words — "Danielle paid this", "put it on mine". Mail from an address that is
  // not listed here goes to needs-review rather than into a guessed column.
  // `header` is matched against the tab's header row, so the columns are located
  // rather than assumed.
  PAYERS: [
    {
      name: 'Rob',
      header: 'Paid by Rob',
      senders: ['rob.sinclair.bb@gmail.com'],
    },
    {
      name: 'Danielle',
      header: 'Paid by Danielle',
      senders: ['danielle.lucas5@gmail.com', 'chickami@hotmail.com'],
    },
  ],

  // Receipts in any other currency go to needs-review rather than being converted.
  CURRENCY: 'CAD',

  // Something one of them bought for the other, at their request, is not a shared
  // expense. The sheet's convention for that — the legend in D1 — is to enter the
  // amount doubled, as a formula, so the 50/50 split nets out to the other person
  // owing the whole of it, and to highlight the cell. Clicking it still shows what
  // was actually spent.
  NOT_SHARED_BACKGROUND: '#ffff00',

  MODEL: 'claude-opus-5',
  // Reading a receipt is a simple extraction; raise to 'medium' or 'high' if the
  // model starts fumbling faded or crumpled receipts.
  EFFORT: 'low',

  // Ceilings, so one bad run can't blow the Apps Script quota.
  MAX_THREADS_PER_RUN: 10,
  MAX_ATTACHMENT_BYTES: 5 * 1024 * 1024,

  // Only needed if a month tab can't be found by name. Key is YYYY-MM.
  // The sheet's convention — "Aug2026 - Var Expenses" — is matched without this.
  //   TAB_OVERRIDES: { '2026-09': 'Sept 2026 variable' }
  TAB_OVERRIDES: {},

  // Email address for a digest of anything sent to needs-review. '' = no digest.
  DIGEST_TO: '',
};

/** MIME types the Messages API can read, mapped to how we send them. */
const SUPPORTED_TYPES = {
  'image/jpeg': 'image',
  'image/jpg': 'image',
  'image/png': 'image',
  'image/gif': 'image',
  'image/webp': 'image',
  'application/pdf': 'document',
};
