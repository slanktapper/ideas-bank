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

  // Which "Paid by" column a receipt lands in, matched against the header text.
  PAYER_HEADER: 'Paid by Rob',

  // Receipts in any other currency go to needs-review rather than being converted.
  CURRENCY: 'CAD',

  MODEL: 'claude-opus-5',
  // Reading a receipt is a simple extraction; raise to 'medium' or 'high' if the
  // model starts fumbling faded or crumpled receipts.
  EFFORT: 'low',

  // Ceilings, so one bad run can't blow the Apps Script quota.
  MAX_THREADS_PER_RUN: 10,
  MAX_ATTACHMENT_BYTES: 5 * 1024 * 1024,

  // Only needed if the month tab can't be found by name. Key is YYYY-MM.
  //   TAB_OVERRIDES: { '2026-08': 'Aug', '2026-09': 'Sept' }
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
