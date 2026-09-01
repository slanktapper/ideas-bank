/**
 * Finding the right month tab, and writing one row into it.
 *
 * The spreadsheet belongs to someone else and is full of formulas. Two rules follow
 * from that, and the whole file is shaped by them:
 *
 *   1. Never append. Columns M–T of every month tab carry per-row formulas that feed
 *      the category totals at the top; they are pre-filled down a fixed block of
 *      rows. A row appended past that block is invisible to the totals. So: find the
 *      first blank row *inside* the formula block, and write into it.
 *   2. Never invent structure. The columns and the category names are read out of
 *      the tab's own header row every run. If the sheet changes, this follows.
 */

const MONTH_NAMES = ['january', 'february', 'march', 'april', 'may', 'june',
                     'july', 'august', 'september', 'october', 'november', 'december'];

function openSpreadsheet_() {
  try {
    return SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID);
  } catch (err) {
    throw new Error(
      'Could not open the spreadsheet. Check CONFIG.SPREADSHEET_ID, and that this ' +
      'account has edit access to it. (' + err.message + ')');
  }
}

/**
 * Read a month tab's layout: where the header row is, which column is what, and
 * which categories it offers. Returns null for tabs that are not month tabs.
 */
function readLayout_(sheet) {
  const searchDepth = Math.min(12, sheet.getLastRow());
  if (searchDepth < 1 || sheet.getLastColumn() < 1) return null;
  const top = sheet.getRange(1, 1, searchDepth, sheet.getLastColumn()).getDisplayValues();

  for (let r = 0; r < top.length; r++) {
    const row = top[r].map(function (cell) { return String(cell).trim(); });
    if (row[0] !== 'Description') continue;

    const layout = {
      headerRow: r + 1,
      descriptionCol: 1,
      payerCol: row.indexOf(CONFIG.PAYER_HEADER) + 1,
      dateCol: row.indexOf('Date') + 1,
      categoryCol: row.indexOf('Category') + 1,
      categories: [],
      categoryFirstCol: 0,
    };
    if (!layout.payerCol || !layout.dateCol || !layout.categoryCol) continue;

    // The category matrix sits to the right of the entry columns: every remaining
    // header cell except the "Error" catch-all column.
    for (let c = layout.categoryCol; c < row.length; c++) {
      const name = row[c];
      if (!name || name === 'Error' || name === 'Card') continue;
      if (!layout.categoryFirstCol) layout.categoryFirstCol = c + 1;
      layout.categories.push(name);
    }
    if (!layout.categories.length) continue;

    return layout;
  }
  return null;
}

/**
 * The month tab for a given date: by name first, then by the dates already in it.
 * Returns {sheet, layout} or null — it never creates a tab.
 */
function findMonthTab_(spreadsheet, date) {
  const year = date.getFullYear();
  const month = date.getMonth(); // 0-based
  const key = year + '-' + ('0' + (month + 1)).slice(-2);

  // Scanning every tab means a Sheets read per tab, and a run can file several
  // receipts into the same month. Remember the answer for the length of the run.
  if (Object.prototype.hasOwnProperty.call(MONTH_TAB_CACHE, key)) return MONTH_TAB_CACHE[key];

  const candidates = [];
  spreadsheet.getSheets().forEach(function (sheet) {
    const layout = readLayout_(sheet);
    if (layout) candidates.push({ sheet: sheet, layout: layout });
  });

  const override = CONFIG.TAB_OVERRIDES[key];
  if (override) {
    const match = candidates.filter(function (c) { return c.sheet.getName() === override; })[0];
    if (match) return remember_(key, match);
    throw new Error('TAB_OVERRIDES has "' + override + '" for ' + key +
                    ', but no month tab by that name exists.');
  }

  const byName = candidates.filter(function (c) {
    return tabNameMatchesMonth_(c.sheet.getName(), year, month);
  });
  if (byName.length === 1) return remember_(key, byName[0]);
  if (byName.length > 1) {
    throw new Error('Ambiguous month tab for ' + key + ': ' +
                    byName.map(function (c) { return c.sheet.getName(); }).join(', ') +
                    '. Set CONFIG.TAB_OVERRIDES.');
  }

  // No name match — fall back to the tab that already holds dates in this month.
  const byContent = candidates.filter(function (c) {
    return tabHoldsMonth_(c.sheet, c.layout, year, month);
  });
  if (byContent.length === 1) return remember_(key, byContent[0]);

  return remember_(key, null);
}

/** Per-run memo for findMonthTab_. Cleared at the top of every processReceipts(). */
let MONTH_TAB_CACHE = {};

function resetTabCache_() {
  MONTH_TAB_CACHE = {};
}

function remember_(key, value) {
  MONTH_TAB_CACHE[key] = value;
  return value;
}

/** Does a tab name denote this month? Handles "Aug", "August", "Aug 2026", "2026-08". */
function tabNameMatchesMonth_(name, year, month) {
  const lower = name.toLowerCase();
  const full = MONTH_NAMES[month];

  // Numeric forms: 2026-08, 2026/8, 08-2026.
  const numeric = new RegExp('(^|\\D)' + year + '\\D0?' + (month + 1) + '(\\D|$)|' +
                             '(^|\\D)0?' + (month + 1) + '\\D' + year + '(\\D|$)');
  if (numeric.test(lower)) return true;

  // Named forms. Match the month name as a prefix ("sept" for September) but not
  // across months ("mar" must not match "may").
  const words = lower.split(/[^a-z]+/).filter(Boolean);
  const namesMonth = words.some(function (word) {
    return word.length >= 3 && (full.indexOf(word) === 0 || word.indexOf(full) === 0);
  });
  if (!namesMonth) return false;

  // If the name carries a year, it has to be the right one.
  const years = lower.match(/\b(19|20)\d{2}\b/g);
  if (years && years.indexOf(String(year)) === -1) return false;
  return true;
}

/** Does this tab already contain entries dated in the given month? */
function tabHoldsMonth_(sheet, layout, year, month) {
  const lastRow = sheet.getLastRow();
  if (lastRow <= layout.headerRow) return false;
  const dates = sheet
    .getRange(layout.headerRow + 1, layout.dateCol, lastRow - layout.headerRow, 1)
    .getValues();
  return dates.some(function (row) {
    const value = row[0];
    return isDate_(value) && value.getFullYear() === year && value.getMonth() === month;
  });
}

/** Cell values come back from the Sheets service, so check the shape, not the constructor. */
function isDate_(value) {
  return Object.prototype.toString.call(value) === '[object Date]' && !isNaN(value.getTime());
}

/**
 * Write one expense into the first blank row inside the tab's formula block.
 * Returns the row number written.
 */
function writeExpense_(sheet, layout, expense) {
  const row = firstBlankFormulaRow_(sheet, layout);
  if (!row) {
    throw new Error('No blank pre-formulated row left on "' + sheet.getName() +
                    '". Someone needs to extend the formulas down the sheet.');
  }

  // Written cell by cell: everything else on the row, including the other payer's
  // column and the Card note, is left exactly as it was.
  sheet.getRange(row, layout.descriptionCol).setValue(expense.description);
  sheet.getRange(row, layout.payerCol).setValue(expense.total);
  sheet.getRange(row, layout.dateCol).setValue(expense.date);
  sheet.getRange(row, layout.categoryCol).setValue(expense.category);
  return row;
}

/**
 * The first row that is blank across the entry columns AND still inside the block
 * of rows carrying the category formulas. Both halves matter: past the formulas,
 * a row does not reach the monthly totals.
 */
function firstBlankFormulaRow_(sheet, layout) {
  const start = layout.headerRow + 1;
  const depth = sheet.getMaxRows() - layout.headerRow;
  if (depth < 1) return 0;

  const entries = sheet.getRange(start, 1, depth, layout.categoryCol).getValues();
  const formulas = sheet.getRange(start, layout.categoryFirstCol, depth, 1).getFormulas();

  for (let i = 0; i < entries.length; i++) {
    if (!formulas[i][0]) return 0; // past the formula block, and nothing blank before it
    const blank = entries[i].every(function (cell) { return cell === '' || cell === null; });
    if (blank) return start + i;
  }
  return 0;
}
