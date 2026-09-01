/**
 * Tests for the parts of this script that are plain logic: finding the month tab,
 * finding the row to write into, parsing dates, and deciding what is safe to file.
 *
 * Apps Script itself cannot be run here, so the Google globals the tested functions
 * touch are stubbed below, and the sheet is a fake built to the real shape of a
 * month tab in DNR finances 2024. Anything that talks to Gmail or the Claude API is
 * out of scope — that gets tested by mailing yourself a receipt.
 *
 *   node test/logic-test.js        (run from apps-script/)
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');

// --- stubs for the Google globals the tested code touches ----------------------
const properties = {};
const sandbox = {
  Logger: { log: function () {} },
  PropertiesService: {
    getScriptProperties: function () {
      return {
        getProperty: function (k) { return properties[k] || null; },
        setProperty: function (k, v) { properties[k] = v; },
      };
    },
  },
  Utilities: { sleep: function () {} },
  SpreadsheetApp: { openById: function () { throw new Error('not used in these tests'); } },
  console: console,
};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);

['Config.gs', 'Sheet.gs', 'Main.gs'].forEach(function (file) {
  const source = fs.readFileSync(path.join(__dirname, '..', file), 'utf8');
  vm.runInContext(source, sandbox, { filename: file });
});

// --- a fake month tab, built from the real one ---------------------------------
// The geometry comes from test/fixtures/blank-month-tab.json, captured from
// "Sept2026 - Var Expenses" the day it was created: row 5 is the header, rows 6–125
// are entry rows, and columns N–T carry the per-row category formulas. Nothing here
// is invented — change the sheet, recapture the fixture, and these tests follow.
const FIXTURE = require('./fixtures/blank-month-tab.json');

const HEADER_ROW = FIXTURE.headerRow;
const FIRST_ENTRY_ROW = FIXTURE.firstEntryRow;
const FORMULA_LAST_ROW = FIXTURE.lastFormulaRow;
const CATEGORIES = FIXTURE.categories;
const FIRST_CATEGORY_COL = colNumber(FIXTURE.columns.firstCategory);
const LAST_CATEGORY_COL = colNumber(FIXTURE.columns.lastCategory);
const ERROR_COL = colNumber(FIXTURE.columns.error);

function colNumber(letters) {
  return letters.split('').reduce(function (n, ch) {
    return n * 26 + (ch.charCodeAt(0) - 64);
  }, 0);
}

function makeTab(name, entries) {
  const maxRows = FORMULA_LAST_ROW + 75, maxCols = LAST_CATEGORY_COL;
  const values = [];
  for (let r = 0; r < maxRows; r++) values.push(new Array(maxCols).fill(''));

  // The rows above the header, so the header search has to step over real content.
  Object.keys(FIXTURE.topRows).forEach(function (rowNumber) {
    const cells = FIXTURE.topRows[rowNumber];
    Object.keys(cells).forEach(function (letter) {
      values[Number(rowNumber) - 1][colNumber(letter) - 1] = cells[letter];
    });
  });
  CATEGORIES.forEach(function (category, i) {
    values[1][FIRST_CATEGORY_COL - 1 + i] = '$' + FIXTURE.budgets[category] + '.00';
  });

  const header = values[HEADER_ROW - 1];
  header[0] = 'Description';
  header[colNumber(FIXTURE.columns.paidByRob) - 1] = 'Paid by Rob';
  header[colNumber(FIXTURE.columns.paidByDanielle) - 1] = 'Paid by Danielle';
  header[colNumber(FIXTURE.columns.date) - 1] = 'Date';
  header[colNumber(FIXTURE.columns.category) - 1] = 'Category';
  header[colNumber(FIXTURE.columns.card) - 1] = 'Card';
  header[ERROR_COL - 1] = 'Error';
  CATEGORIES.forEach(function (category, i) {
    header[FIRST_CATEGORY_COL - 1 + i] = category;
  });

  entries.forEach(function (entry, i) {
    const row = values[HEADER_ROW + i];
    row[0] = entry.description;
    row[1] = entry.rob || '';
    row[2] = entry.danielle || '';
    row[3] = entry.date;
    row[4] = entry.category;
  });

  return {
    getName: function () { return name; },
    getMaxRows: function () { return maxRows; },
    getLastColumn: function () { return maxCols; },
    getLastRow: function () { return HEADER_ROW + entries.length; },
    getRange: function (row, col, numRows, numCols) {
      numRows = numRows || 1;
      numCols = numCols || 1;
      const slice = [];
      for (let r = 0; r < numRows; r++) {
        const out = [];
        for (let c = 0; c < numCols; c++) out.push(values[row - 1 + r][col - 1 + c]);
        slice.push(out);
      }
      return {
        getValues: function () { return slice; },
        getDisplayValues: function () {
          return slice.map(function (r) {
            return r.map(function (v) { return v instanceof Date ? v.toDateString() : String(v); });
          });
        },
        // A category column holds a formula on every pre-filled row, and nothing after.
        getFormulas: function () {
          const out = [];
          for (let r = 0; r < numRows; r++) {
            const sheetRow = row + r;
            const isCategoryCol = col >= FIRST_CATEGORY_COL && col <= LAST_CATEGORY_COL;
            out.push([isCategoryCol && sheetRow >= FIRST_ENTRY_ROW && sheetRow <= FORMULA_LAST_ROW
              ? '=IF($E' + sheetRow + '=N$' + HEADER_ROW + ',$B' + sheetRow +
                '+$C' + sheetRow + ',0)' : '']);
          }
          return out;
        },
        setValue: function (value) { values[row - 1][col - 1] = value; },
      };
    },
    _values: values,
  };
}

/** A tab that is not an expense month: no Description header anywhere near the top. */
function makeNotesTab() {
  const rows = [['SUBJECT HOME:', ''], ['Mortgage statement', ''], ['Property tax', '']];
  return {
    getName: function () { return 'Notes'; },
    getMaxRows: function () { return 3; },
    getLastRow: function () { return 3; },
    getLastColumn: function () { return 2; },
    getRange: function (row, col, numRows, numCols) {
      return {
        getDisplayValues: function () {
          return rows.slice(row - 1, row - 1 + numRows)
                     .map(function (r) { return r.slice(col - 1, col - 1 + numCols); });
        },
      };
    },
  };
}

/** A brand-new blank tab. */
function makeEmptyTab() {
  return {
    getName: function () { return 'Sheet1'; },
    getMaxRows: function () { return 1000; },
    getLastRow: function () { return 0; },
    getLastColumn: function () { return 0; },
    getRange: function () { throw new Error('should not read an empty tab'); },
  };
}

function makeSpreadsheet(tabs) {
  return { getSheets: function () { return tabs; } };
}

// CONFIG is declared with const, so it lives in the context's lexical scope rather
// than on the sandbox object — reach it by evaluating inside the context.
function setOverrides(map) {
  vm.runInContext('CONFIG.TAB_OVERRIDES = ' + JSON.stringify(map) + ';', sandbox);
}

// --- the tiniest test runner ---------------------------------------------------
let failures = 0;
function check(name, actual, expected) {
  const a = JSON.stringify(actual), e = JSON.stringify(expected);
  if (a === e) {
    console.log('  ok   ' + name);
  } else {
    failures++;
    console.log('  FAIL ' + name + '\n         expected ' + e + '\n         got      ' + a);
  }
}
function throws(name, fn, fragment) {
  try {
    fn();
    failures++;
    console.log('  FAIL ' + name + '\n         expected a throw containing "' + fragment + '"');
  } catch (err) {
    if (err.message.indexOf(fragment) === -1) {
      failures++;
      console.log('  FAIL ' + name + '\n         expected "' + fragment + '" in: ' + err.message);
    } else {
      console.log('  ok   ' + name);
    }
  }
}

// --- reading a tab's layout ----------------------------------------------------
console.log('readLayout_');
const august = makeTab('Aug2026 - Var Expenses', [
  { description: 'Car gas', danielle: 47.86, date: new Date(2026, 7, 8), category: 'Transportation' },
  { description: 'Atco', rob: 110.56, date: new Date(2026, 7, 18), category: 'Home' },
]);
const layout = sandbox.readLayout_(august);
check('finds the header row', layout.headerRow, HEADER_ROW);
check('finds a column per payer', layout.payerCols, { Rob: 2, Danielle: 3 });
check('finds the date column', layout.dateCol, 4);
check('finds the category column', layout.categoryCol, 5);
check('reads the categories off the sheet', layout.categories, CATEGORIES);
check('skips the Error column', layout.categoryFirstCol, 14);
check('ignores non-month tabs', sandbox.readLayout_(makeNotesTab()), null);
check('ignores an empty tab', sandbox.readLayout_(makeEmptyTab()), null);

// --- finding the row to write into ---------------------------------------------
console.log('firstBlankFormulaRow_');
check('first blank row after the entries', sandbox.firstBlankFormulaRow_(august, layout),
      HEADER_ROW + 2 + 1);

const full = makeTab('Full', []);
for (let r = FIRST_ENTRY_ROW; r <= FORMULA_LAST_ROW; r++) full._values[r - 1][0] = 'taken';
check('returns 0 when the formula block is full',
      sandbox.firstBlankFormulaRow_(full, sandbox.readLayout_(full)), 0);

// --- matching a tab name to a month --------------------------------------------
console.log('tabNameMatchesMonth_');
[// the sheet's own convention
 ['Aug2026 - Var Expenses', true], ['Aug2025 - Var Expenses', false],
 ['Jul2026 - Var Expenses', false], ['Sept2026 - Var Expenses', false],
 // and the other ways a month tab might reasonably be named
 ['Aug', true], ['August', true], ['Aug 2026', true], ['August 2026', true],
 ['2026-08', true], ['8/2026', true], ['Aug 2025', false], ['Sept', false],
 ['Jul', false], ['Budget', false],
 // the static tab, which is not a month at all
 ['85K salary shared exp new', false]].forEach(function (pair) {
  check('"' + pair[0] + '" is August 2026: ' + pair[1],
        sandbox.tabNameMatchesMonth_(pair[0], 2026, 7), pair[1]);
});
check('"Mar" is not May', sandbox.tabNameMatchesMonth_('Mar', 2026, 4), false);
check('"Sept" is September', sandbox.tabNameMatchesMonth_('Sept', 2026, 8), true);
check('"Sept2026 - Var Expenses" is September',
      sandbox.tabNameMatchesMonth_('Sept2026 - Var Expenses', 2026, 8), true);
check('a glued year is still read', sandbox.yearsIn_('aug2026 - var expenses'), ['2026']);
check('a spaced year is still read', sandbox.yearsIn_('august 2026'), ['2026']);
check('adjacent years are both read', sandbox.yearsIn_('2025-2026'), ['2025', '2026']);
check('no year is no constraint', sandbox.yearsIn_('85k salary shared exp new'), []);

// --- finding the month tab -----------------------------------------------------
console.log('findMonthTab_');
const july = makeTab('Jul2026 - Var Expenses', [
  { description: 'Co-op', rob: 82.11, date: new Date(2026, 6, 3), category: 'Groceries' },
]);
const unnamed = makeTab('Copy of Jun', [
  { description: 'Sushi', rob: 61.00, date: new Date(2026, 5, 12), category: 'Restaurant' },
]);
const book = makeSpreadsheet([august, july, unnamed]);

check('by name', sandbox.findMonthTab_(book, new Date(2026, 7, 15)).sheet.getName(),
      'Aug2026 - Var Expenses');
check('answers again from the per-run cache without re-reading the tabs',
      sandbox.findMonthTab_(makeSpreadsheet([]), new Date(2026, 7, 2)).sheet.getName(),
      'Aug2026 - Var Expenses');
sandbox.resetTabCache_();
check('by the dates already in the tab',
      sandbox.findMonthTab_(book, new Date(2026, 5, 2)).sheet.getName(), 'Copy of Jun');
check('null when there is no tab for the month',
      sandbox.findMonthTab_(book, new Date(2026, 0, 5)), null);

setOverrides({ '2026-01': 'Copy of Jun' });
sandbox.resetTabCache_();
check('override wins',
      sandbox.findMonthTab_(book, new Date(2026, 0, 5)).sheet.getName(), 'Copy of Jun');
setOverrides({ '2026-01': 'nope' });
sandbox.resetTabCache_();
throws('override naming a missing tab', function () {
  sandbox.findMonthTab_(book, new Date(2026, 0, 5));
}, 'no month tab by that name');
setOverrides({});

// --- writing -------------------------------------------------------------------
console.log('writeExpense_');
const target = sandbox.writeExpense_(august, layout, {
  description: 'No Frills', total: 51.24, date: new Date(2026, 7, 24),
  category: 'Groceries', payer: 'Rob',
});
check('writes to the first blank row', target, HEADER_ROW + 3);
check('description in A', august._values[target - 1][0], 'No Frills');
check('total in the Rob column', august._values[target - 1][1], 51.24);
check('leaves the other payer alone', august._values[target - 1][2], '');
check('category in E', august._values[target - 1][4], 'Groceries');
check('leaves the Card note alone', august._values[target - 1][5], '');

const danielleRow = sandbox.writeExpense_(august, layout, {
  description: 'Car gas', total: 47.86, date: new Date(2026, 7, 25),
  category: 'Transportation', payer: 'Danielle',
});
check('a Danielle receipt goes in her column', august._values[danielleRow - 1][2], 47.86);
check('and not in his', august._values[danielleRow - 1][1], '');

throws('refuses a payer with no column', function () {
  sandbox.writeExpense_(august, layout, {
    description: 'x', total: 1, date: new Date(), category: 'Home', payer: 'Nobody',
  });
}, 'No column');

throws('refuses when there is no room', function () {
  sandbox.writeExpense_(full, sandbox.readLayout_(full), {
    description: 'x', total: 1, date: new Date(), category: 'Home', payer: 'Rob',
  });
}, 'No blank pre-formulated row');

// --- dates ---------------------------------------------------------------------
console.log('parseDate_');
check('a real date', sandbox.parseDate_('2026-08-24').getDate(), 24);
check('rejects a day that does not exist', sandbox.parseDate_('2026-02-31'), null);
check('rejects a non-date', sandbox.parseDate_('24 August'), null);
check('rejects empty', sandbox.parseDate_(''), null);

// --- what is safe to file ------------------------------------------------------
console.log('validate_');
function reading(overrides) {
  const today = new Date();
  const iso = today.getFullYear() + '-' + ('0' + (today.getMonth() + 1)).slice(-2) +
              '-' + ('0' + today.getDate()).slice(-2);
  return Object.assign({
    is_receipt: true, description: 'Co-op', total: 43.19, currency: 'CAD',
    date: iso, category: 'Groceries', paid_by: '', paid_by_reason: '',
    confidence: 'high', notes: '',
  }, overrides);
}

const FROM_ROB = { from: 'rob.sinclair.bb@gmail.com', text: 'Subject: receipt' };
const FROM_DANIELLE = { from: 'danielle.lucas5@gmail.com', text: 'Subject: receipt' };
check('a clean receipt', sandbox.validate_(reading(), FROM_ROB).description, 'Co-op');
check('rounds to cents', sandbox.validate_(reading({ total: 43.194999 }), FROM_ROB).total, 43.19);
check('an unstated currency is CAD',
      sandbox.validate_(reading({ currency: '' }), FROM_ROB).total, 43.19);
throws('not a receipt', function () { sandbox.validate_(reading({ is_receipt: false }), FROM_ROB); }, 'not a receipt');
throws('low confidence', function () { sandbox.validate_(reading({ confidence: 'low' }), FROM_ROB); }, 'low confidence');
throws('no total', function () { sandbox.validate_(reading({ total: null }), FROM_ROB); }, 'read the total');
throws('zero total', function () { sandbox.validate_(reading({ total: 0 }), FROM_ROB); }, 'read the total');
throws('foreign currency', function () { sandbox.validate_(reading({ currency: 'USD' }), FROM_ROB); }, 'not CAD');
throws('no category', function () { sandbox.validate_(reading({ category: '' }), FROM_ROB); }, 'no category fits');
throws('no merchant', function () { sandbox.validate_(reading({ description: '' }), FROM_ROB); }, 'read the merchant');
throws('unreadable date', function () { sandbox.validate_(reading({ date: '' }), FROM_ROB); }, 'read the date');
throws('future date', function () { sandbox.validate_(reading({ date: '2099-01-01' }), FROM_ROB); }, 'in the future');
throws('ancient date', function () { sandbox.validate_(reading({ date: '2001-01-01' }), FROM_ROB); }, 'two years old');

// --- who paid ------------------------------------------------------------------
console.log('payerForSender_');
check('his address', sandbox.payerForSender_('rob.sinclair.bb@gmail.com'), 'Rob');
check('her gmail', sandbox.payerForSender_('danielle.lucas5@gmail.com'), 'Danielle');
check('her hotmail', sandbox.payerForSender_('chickami@hotmail.com'), 'Danielle');
check('case and spacing do not matter',
      sandbox.payerForSender_('  Danielle.Lucas5@Gmail.com '), 'Danielle');
check('a stranger', sandbox.payerForSender_('someone@example.com'), '');
check('nothing at all', sandbox.payerForSender_(''), '');

console.log('resolvePayer_');
function resolve(overrides, mail) {
  return sandbox.resolvePayer_(reading(overrides), mail);
}
check('the sender decides by default', resolve({}, FROM_ROB).payer, 'Rob');
check('and for her too', resolve({}, FROM_DANIELLE).payer, 'Danielle');
check('a note overrides the sender',
      resolve({ paid_by: 'Danielle', paid_by_reason: '"Danielle paid this one"' },
              { from: 'rob.sinclair.bb@gmail.com', text: 'Danielle paid this one' }).payer,
      'Danielle');
check('the reason is carried through for the log',
      resolve({ paid_by: 'Danielle', paid_by_reason: '"she got this one"' },
              { from: 'rob.sinclair.bb@gmail.com', text: 'she got this one, receipt attached' }).payerSource,
      'the email: "she got this one"');
check('a paraphrase is honoured — no exact match required',
      resolve({ paid_by: 'Danielle', paid_by_reason: '"hers" refers to Danielle' },
              { from: 'rob.sinclair.bb@gmail.com', text: 'this one was hers' }).payer,
      'Danielle');
check('and so is a first-person one resolved against the sender',
      resolve({ paid_by: 'Danielle', paid_by_reason: 'the sender says she paid' },
              { from: 'chickami@hotmail.com', text: 'put this on mine' }).payer,
      'Danielle');
check('a note stands in for an unknown sender',
      resolve({ paid_by: 'Rob', paid_by_reason: 'Rob paid' },
              { from: 'someone@example.com', text: 'Rob paid, forwarding this on' }).payer,
      'Rob');
check('a payer read out of an empty email is ignored',
      resolve({ paid_by: 'Danielle', paid_by_reason: 'no idea really' },
              { from: 'rob.sinclair.bb@gmail.com', text: '' }).payer,
      'Rob');
throws('an unknown sender and no note', function () {
  resolve({}, { from: 'someone@example.com', text: 'receipt attached' });
}, 'not one of the payers');
throws('an unknown sender and an empty email', function () {
  resolve({ paid_by: 'Danielle', paid_by_reason: 'guessing' },
          { from: 'someone@example.com', text: '' });
}, 'not one of the payers');

console.log('validate_ carries the payer through');
check('from the sender', sandbox.validate_(reading(), FROM_DANIELLE).payer, 'Danielle');
check('from the note',
      sandbox.validate_(reading({ paid_by: 'Danielle', paid_by_reason: '"hers"' }),
                        { from: 'rob.sinclair.bb@gmail.com', text: 'this one is hers' }).payer,
      'Danielle');

// --- a brand-new month, exactly as the sheet makes one --------------------------
console.log('the blank month template (' + FIXTURE.tab + ', captured ' + FIXTURE.captured + ')');
const sept = makeTab(FIXTURE.tab, []);
const septLayout = sandbox.readLayout_(sept);
check('is recognised as a month tab', septLayout !== null, true);
check('the header row is where the fixture says', septLayout.headerRow, FIXTURE.headerRow);
check('the categories are read off it', septLayout.categories, FIXTURE.categories);
check('the first receipt of the month goes to the first entry row',
      sandbox.firstBlankFormulaRow_(sept, septLayout), FIXTURE.firstEntryRow);

sandbox.resetTabCache_();
check('found by name for September 2026',
      sandbox.findMonthTab_(makeSpreadsheet([sept]), new Date(2026, 8, 4)).sheet.getName(),
      FIXTURE.tab);
sandbox.resetTabCache_();
check('and not for August', sandbox.findMonthTab_(makeSpreadsheet([sept]), new Date(2026, 7, 4)), null);
sandbox.resetTabCache_();

// Fill it the way a month actually would, and check it holds what it claims to.
let written = 0;
for (let i = 0; i < FIXTURE.entryRowCapacity; i++) {
  written = sandbox.writeExpense_(sept, septLayout, {
    description: 'Co-op', total: 10, date: new Date(2026, 8, 4),
    category: 'Groceries', payer: i % 2 ? 'Danielle' : 'Rob',
  });
}
check('holds a month of receipts', FIXTURE.entryRowCapacity, 120);
check('the last one lands on the last formula row', written, FIXTURE.lastFormulaRow);
throws('and refuses the one after that', function () {
  sandbox.writeExpense_(sept, septLayout, {
    description: 'Co-op', total: 10, date: new Date(2026, 8, 4),
    category: 'Groceries', payer: 'Rob',
  });
}, 'No blank pre-formulated row');

console.log(failures ? '\n' + failures + ' failure(s)' : '\nall passing');
process.exit(failures ? 1 : 0);
