/**
 * A fake month tab, built to the real geometry of DNR finances 2024.
 *
 * The numbers come from fixtures/blank-month-tab.json, captured out of the workbook
 * itself, so both the unit tests and the dry run exercise the script against the
 * real shape of the sheet rather than one invented to suit it.
 */

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
  const values = [], formulas = [], backgrounds = [];
  for (let r = 0; r < maxRows; r++) {
    values.push(new Array(maxCols).fill(''));
    formulas.push(new Array(maxCols).fill(''));
    backgrounds.push(new Array(maxCols).fill(''));
  }

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
        setFormula: function (formula) { formulas[row - 1][col - 1] = '=' + formula; },
        setBackground: function (colour) { backgrounds[row - 1][col - 1] = colour; },
      };
    },
    _values: values,
    _formulas: formulas,
    _backgrounds: backgrounds,
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

module.exports = {
  FIXTURE: FIXTURE,
  HEADER_ROW: HEADER_ROW,
  FIRST_ENTRY_ROW: FIRST_ENTRY_ROW,
  FORMULA_LAST_ROW: FORMULA_LAST_ROW,
  CATEGORIES: CATEGORIES,
  colNumber: colNumber,
  makeTab: makeTab,
  makeNotesTab: makeNotesTab,
  makeEmptyTab: makeEmptyTab,
  makeSpreadsheet: makeSpreadsheet,
};
