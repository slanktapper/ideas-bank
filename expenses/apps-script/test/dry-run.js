/**
 * What would this email actually do to the spreadsheet?
 *
 * Runs the real script — Config, Claude, Sheet, Gmail and Main, unmodified — against
 * a fake Gmail label and a fake month tab built to the real geometry of the sheet.
 * Everything is genuine except one thing: there is no API key here, so the Claude
 * call is intercepted and answered from a canned reading. The prompt that would have
 * been sent is printed in full, so you can see exactly what the model is asked.
 *
 *   node test/dry-run.js                        the ATCO bill notice
 *   node test/dry-run.js cases/<name>.json      any other case
 *
 * A case file holds the email and the reading the model is assumed to return.
 * Editing the reading is how you ask "what if it read it differently?".
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const FAKE = require('./fake-sheet');

const casePath = process.argv[2] || path.join(__dirname, 'cases', 'atco-bill.json');
const testCase = JSON.parse(fs.readFileSync(casePath, 'utf8'));

// --- the sheet, as it stands today ---------------------------------------------
const sept = FAKE.makeTab('Sept2026 - Var Expenses', testCase.existingRows.map(function (row) {
  return {
    description: row.description, rob: row.rob, danielle: row.danielle,
    date: new Date(row.date + 'T00:00:00'), category: row.category,
  };
}));
const book = FAKE.makeSpreadsheet([sept]);

// --- the mail ------------------------------------------------------------------
const labels = {};
function fakeLabel(name) {
  if (!labels[name]) labels[name] = { name: name, threads: [] };
  return {
    getName: function () { return name; },
    getThreads: function () { return labels[name].threads.slice(); },
    addToThread: function (t) { labels[name].threads.push(t); },
    removeFromThread: function (t) {
      labels[name].threads = labels[name].threads.filter(function (x) { return x !== t; });
    },
  };
}

const message = {
  getId: function () { return 'msg-1'; },
  getFrom: function () { return testCase.email.from; },
  getTo: function () { return testCase.email.to || ''; },
  getCc: function () { return testCase.email.cc || ''; },
  getSubject: function () { return testCase.email.subject; },
  getPlainBody: function () { return testCase.email.body; },
  getAttachments: function () { return []; },
};
const thread = {
  getFirstMessageSubject: function () { return testCase.email.subject; },
  getMessages: function () { return [message]; },
};

// --- stubs ---------------------------------------------------------------------
const logLines = [];
let sentRequest = null;

const properties = { ANTHROPIC_API_KEY: 'sk-ant-not-a-real-key' };
const sandbox = {
  console: console,
  Logger: { log: function (line) { logLines.push(String(line)); } },
  PropertiesService: {
    getScriptProperties: function () {
      return {
        getProperty: function (k) { return properties[k] || null; },
        setProperty: function (k, v) { properties[k] = v; },
      };
    },
  },
  Utilities: {
    sleep: function () {},
    base64Encode: function (bytes) { return Buffer.from(bytes).toString('base64'); },
  },
  LockService: {
    getScriptLock: function () {
      return { tryLock: function () { return true; }, releaseLock: function () {} };
    },
  },
  SpreadsheetApp: {
    openById: function () { return { getName: function () { return 'DNR finances 2024'; },
                                     getSheets: book.getSheets }; },
  },
  GmailApp: {
    getUserLabelByName: function (n) { return labels[n] ? fakeLabel(n) : null; },
    createLabel: fakeLabel,
    sendEmail: function (to, subject, body) {
      logLines.push('DIGEST to ' + to + ': ' + subject + '\n' + body);
    },
  },
  // The one thing that is not real: no API key here, so the call is answered
  // from the case file instead of from the model.
  UrlFetchApp: {
    fetch: function (url, options) {
      sentRequest = { url: url, body: JSON.parse(options.payload) };
      return {
        getResponseCode: function () { return 200; },
        getContentText: function () {
          return JSON.stringify({
            stop_reason: 'end_turn',
            content: [{ type: 'text', text: JSON.stringify(testCase.reading) }],
          });
        },
      };
    },
  },
};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
['Config.gs', 'Claude.gs', 'Sheet.gs', 'Gmail.gs', 'Main.gs'].forEach(function (file) {
  vm.runInContext(fs.readFileSync(path.join(__dirname, '..', file), 'utf8'), sandbox,
                  { filename: file });
});

// --- run it --------------------------------------------------------------------
labels[sandbox.CONFIG ? 'receipts' : 'receipts'] = { name: 'receipts', threads: [thread] };
vm.runInContext('processReceipts();', sandbox);

// --- report --------------------------------------------------------------------
const rule = '─'.repeat(78);
function heading(text) { console.log('\n' + text + '\n' + rule); }

heading('THE EMAIL');
console.log('From:    ' + testCase.email.from);
console.log('To:      ' + (testCase.email.to || '(nobody)'));
if (testCase.email.cc) console.log('Cc:      ' + testCase.email.cc);
console.log('Subject: ' + testCase.email.subject);
console.log('\n' + testCase.email.body.trim());

heading('WHAT THE SCRIPT ASKS THE MODEL');
if (!sentRequest) {
  console.log('(no API call was made — the script rejected this before reading it)');
} else {
  const body = sentRequest.body;
  console.log('model:  ' + body.model + '   effort: ' + body.output_config.effort +
              '   max_tokens: ' + body.max_tokens);
  console.log('blocks: ' + body.messages[0].content.map(function (b) { return b.type; }).join(', '));
  console.log('\n--- system ---\n' + body.system);
  body.messages[0].content.forEach(function (block) {
    if (block.type === 'text') console.log('\n--- user ---\n' + block.text);
  });
  console.log('\n--- the answer it is allowed to give ---');
  const props = body.output_config.format.schema.properties;
  Object.keys(props).forEach(function (key) {
    console.log('  ' + key.padEnd(18) +
                (props[key].enum ? 'one of: ' + JSON.stringify(props[key].enum) : props[key].type ||
                 JSON.stringify(props[key].anyOf)));
  });
}

if (sentRequest) {
  heading('WHAT THE MODEL IS ASSUMED TO ANSWER  (the only invented part)');
  console.log(JSON.stringify(testCase.reading, null, 2));
}

heading('WHAT LANDS IN THE SPREADSHEET');
const layout = vm.runInContext('readLayout_', sandbox)(sept);
const before = testCase.existingRows.length;
const writtenRow = FAKE.FIRST_ENTRY_ROW + before;
const values = sept._values[writtenRow - 1];
const formulas = sept._formulas[writtenRow - 1];
const backgrounds = sept._backgrounds[writtenRow - 1];

const touched = ['A', 'B', 'C', 'D', 'E', 'F'].map(function (letter) {
  const i = FAKE.colNumber(letter) - 1;
  // Dates come back from the script's own realm, so check the shape, not the class.
  const raw = values[i];
  const isDate = Object.prototype.toString.call(raw) === '[object Date]';
  const shown = formulas[i] || (isDate
    ? (raw.getMonth() + 1) + '/' + raw.getDate() + '/' + raw.getFullYear()
    : raw);
  return { letter: letter, value: shown, background: backgrounds[i] };
});

if (touched.every(function (c) { return c.value === '' || c.value === undefined; })) {
  console.log('Nothing. No row was written.');
} else {
  console.log('Tab:  Sept2026 - Var Expenses');
  console.log('Row:  ' + writtenRow + '\n');
  const header = ['Description', 'Paid by Rob', 'Paid by Danielle', 'Date', 'Category', 'Card'];
  touched.forEach(function (cell, i) {
    console.log('  ' + cell.letter + writtenRow + '  ' + header[i].padEnd(17) +
                (cell.value === '' ? '(left alone)' : String(cell.value)) +
                (cell.background ? '   ← highlighted ' + cell.background : ''));
  });
}

heading('THE LOG');
logLines.forEach(function (line) { console.log('  ' + line); });

heading('WHERE THE EMAIL ENDS UP');
Object.keys(labels).forEach(function (name) {
  console.log('  ' + name.padEnd(24) + (labels[name].threads.length ? 'this thread' : '—'));
});
console.log('');
