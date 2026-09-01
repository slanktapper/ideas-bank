/**
 * expenses — receipt photo in Gmail, expense row in the spreadsheet.
 *
 * Entry points, in the order you need them:
 *   checkSetup()      run once; reports on the key, the sheet, the labels, today's tab
 *   listTabs()        prints the real tab names, for CONFIG.TAB_OVERRIDES
 *   installTrigger()  run once; starts the 15-minute timer
 *   processReceipts() what the timer calls, and what you call to run it by hand
 *   removeTriggers()  stop the timer
 */

/** Every run of the timer. Safe to call by hand at any time. */
function processReceipts() {
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(30000)) {
    Logger.log('Another run is still going; skipping this one.');
    return;
  }

  try {
    const threads = pendingThreads_();
    if (!threads.length) {
      Logger.log('Nothing labelled "' + CONFIG.INBOX_LABEL + '".');
      return;
    }

    resetTabCache_();
    const spreadsheet = openSpreadsheet_();
    const problems = [];
    let filed = 0;

    threads.forEach(function (thread) {
      const outcome = processThread_(thread, spreadsheet);
      filed += outcome.filed;
      outcome.problems.forEach(function (reason) {
        problems.push({ subject: thread.getFirstMessageSubject(), reason: reason });
      });
      fileThread_(thread, outcome.problems.length ? CONFIG.REVIEW_LABEL : CONFIG.FILED_LABEL);
    });

    Logger.log('Filed ' + filed + ' receipt(s); ' + problems.length + ' need a look.');
    sendDigest_(problems);
  } finally {
    lock.releaseLock();
  }
}

/** One mail thread. Returns what got filed and what didn't. */
function processThread_(thread, spreadsheet) {
  const result = { filed: 0, problems: [] };

  thread.getMessages().forEach(function (message) {
    const messageId = message.getId();
    if (alreadyProcessed_(messageId)) return;

    const attachments = receiptAttachments_(message);
    if (!attachments.length) {
      result.problems.push('no image or PDF attached');
      return;
    }

    const mail = mailContext_(message);
    attachments.forEach(function (attachment) {
      try {
        result.filed += fileAttachment_(attachment, mail, spreadsheet) ? 1 : 0;
      } catch (err) {
        result.problems.push(attachment.getName() + ': ' + err.message);
        Logger.log('Failed on ' + attachment.getName() + ': ' + err.stack);
      }
    });

    markProcessed_(messageId);
  });

  return result;
}

/**
 * One attachment: read it, check it, write it. Throws with a human-readable reason
 * for anything that should go to needs-review instead of into the sheet.
 */
function fileAttachment_(attachment, mail, spreadsheet) {
  const size = attachment.getSize();
  if (size > CONFIG.MAX_ATTACHMENT_BYTES) {
    throw new Error('attachment is ' + Math.round(size / 1024 / 1024) + 'MB, over the ' +
                    Math.round(CONFIG.MAX_ATTACHMENT_BYTES / 1024 / 1024) + 'MB limit');
  }

  // The month tab has to be known before the model runs: its header row is where
  // the list of valid categories comes from. Today's tab is the right guess, and
  // the receipt's own date is checked against it afterwards.
  const today = new Date();
  let tab = findMonthTab_(spreadsheet, today);
  if (!tab) {
    throw new Error('no month tab found for ' + monthKey_(today) +
                    ' — run listTabs() and set CONFIG.TAB_OVERRIDES');
  }

  const base64 = Utilities.base64Encode(attachment.getBytes());
  const mimeType = normaliseType_(attachment.getContentType());
  const reading = readReceipt_(base64, mimeType, tab.layout.categories, mail);

  const expense = validate_(reading, mail);

  // A receipt from a previous month belongs on that month's tab.
  if (expense.date.getMonth() !== today.getMonth() ||
      expense.date.getFullYear() !== today.getFullYear()) {
    const older = findMonthTab_(spreadsheet, expense.date);
    if (!older) {
      throw new Error('receipt is dated ' + monthKey_(expense.date) +
                      ' but there is no tab for that month');
    }
    tab = older;
    if (tab.layout.categories.indexOf(expense.category) === -1) {
      throw new Error('"' + expense.category + '" is not a category on ' +
                      tab.sheet.getName());
    }
  }

  const row = writeExpense_(tab.sheet, tab.layout, expense);
  Logger.log('Filed ' + expense.description + ' $' + expense.total + ' under ' +
             expense.payer + ' (' + expense.payerSource + ')' +
             (expense.notShared
               ? ', doubled — bought for ' + expense.boughtFor + ' (' +
                 expense.sharingSource + ')'
               : '') +
             ' to ' + tab.sheet.getName() + ' row ' + row);
  return true;
}

/**
 * Was this bought for the other person, at their request, rather than shared?
 *
 * A narrow claim, and only ever made by the email — a receipt cannot tell you who
 * a purchase was for. Bought for the person who paid is just an ordinary purchase,
 * so that reads as shared, not as a doubling.
 */
function resolveSharing_(reading, mail, payer) {
  const boughtFor = reading.bought_for;
  if (!boughtFor || !mail.text) return { notShared: false, boughtFor: '', sharingSource: '' };
  if (boughtFor === payer) return { notShared: false, boughtFor: '', sharingSource: '' };
  if (!payerForName_(boughtFor)) return { notShared: false, boughtFor: '', sharingSource: '' };

  return {
    notShared: true,
    boughtFor: boughtFor,
    sharingSource: 'the email: ' + (reading.bought_for_reason || 'it says so'),
  };
}

/** Is this one of the people in Config.gs? */
function payerForName_(name) {
  return CONFIG.PAYERS.some(function (payer) { return payer.name === name; });
}

/**
 * Who paid. The sending address settles it, unless the email says otherwise.
 *
 * The model reads the whole message and decides for itself whether it names a
 * payer — "she got this one" and "on my card" count, not just a set phrase — and
 * says in paid_by_reason what it read that from. That reason is for the log and
 * the digest, so a wrong call is visible afterwards rather than silent; it is not
 * checked against the text, because requiring an exact match is what stopped the
 * ordinary way people write from working.
 *
 * The one thing still refused is a payer read out of an email with nothing in it.
 */
function resolvePayer_(reading, mail) {
  const fromSender = payerForSender_(mail.from);

  if (reading.paid_by) {
    if (mail.text) {
      return {
        payer: reading.paid_by,
        payerSource: 'the email: ' + (reading.paid_by_reason || 'it names them'),
      };
    }
    Logger.log('Ignoring paid_by "' + reading.paid_by + '" — the email had no message in it.');
  }

  if (fromSender) return { payer: fromSender, payerSource: 'sent by ' + mail.from };

  throw new Error('mail is from ' + (mail.from || 'an unknown address') +
                  ', which is not one of the payers in Config.gs, and nothing in it ' +
                  'says who paid');
}

/** The payer an address belongs to, or '' for an address nobody claims. */
function payerForSender_(address) {
  const from = String(address || '').trim().toLowerCase();
  if (!from) return '';
  const match = CONFIG.PAYERS.filter(function (payer) {
    return payer.senders.some(function (sender) {
      return sender.trim().toLowerCase() === from;
    });
  })[0];
  return match ? match.name : '';
}

/**
 * Turn a model reading into something writable, or throw. Everything here is a
 * reason to leave the receipt for a human rather than write a number that might
 * be wrong.
 */
function validate_(reading, mail) {
  if (!reading.is_receipt) {
    throw new Error('not a receipt' + (reading.notes ? ' (' + reading.notes + ')' : ''));
  }
  if (reading.confidence === 'low') {
    throw new Error('low confidence' + (reading.notes ? ': ' + reading.notes : ''));
  }
  if (reading.total === null || !(reading.total > 0)) {
    throw new Error('could not read the total');
  }
  // A receipt that does not name its currency, in an Alberta household, is CAD.
  if (reading.currency && reading.currency.toUpperCase() !== CONFIG.CURRENCY) {
    throw new Error('receipt is in ' + reading.currency + ', not ' + CONFIG.CURRENCY);
  }
  if (!reading.category) {
    throw new Error('no category fits' + (reading.notes ? ' (' + reading.notes + ')' : ''));
  }
  if (!reading.description) {
    throw new Error('could not read the merchant');
  }

  const date = parseDate_(reading.date);
  if (!date) throw new Error('could not read the date');

  const now = new Date();
  const daysAhead = (date.getTime() - now.getTime()) / (1000 * 60 * 60 * 24);
  if (daysAhead > 1) throw new Error('date ' + reading.date + ' is in the future');
  if (daysAhead < -730) throw new Error('date ' + reading.date + ' is over two years old');

  const paid = resolvePayer_(reading, mail || {});
  const sharing = resolveSharing_(reading, mail || {}, paid.payer);

  return {
    description: reading.description,
    total: Math.round(reading.total * 100) / 100,
    date: date,
    category: reading.category,
    payer: paid.payer,
    payerSource: paid.payerSource,
    notShared: sharing.notShared,
    boughtFor: sharing.boughtFor,
    sharingSource: sharing.sharingSource,
  };
}

/** 'YYYY-MM-DD' to a local Date. Null for anything else. */
function parseDate_(text) {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(text || '').trim());
  if (!match) return null;
  const year = Number(match[1]), month = Number(match[2]), day = Number(match[3]);
  const date = new Date(year, month - 1, day);
  if (date.getFullYear() !== year || date.getMonth() !== month - 1 || date.getDate() !== day) {
    return null; // e.g. 2026-02-31
  }
  return date;
}

function monthKey_(date) {
  return date.getFullYear() + '-' + ('0' + (date.getMonth() + 1)).slice(-2);
}

// ---------------------------------------------------------------------------
// Setup helpers — run these by hand from the Apps Script editor.
// ---------------------------------------------------------------------------

/** Check everything the script needs, and create the labels if they are missing. */
function checkSetup() {
  const lines = [];

  const key = PropertiesService.getScriptProperties().getProperty('ANTHROPIC_API_KEY');
  lines.push(key
    ? 'API key: set (' + key.slice(0, 8) + '…)'
    : 'API key: MISSING — add ANTHROPIC_API_KEY under Project Settings › Script Properties');

  try {
    const spreadsheet = openSpreadsheet_();
    lines.push('Spreadsheet: "' + spreadsheet.getName() + '"');

    const today = new Date();
    const tab = findMonthTab_(spreadsheet, today);
    if (tab) {
      const row = firstBlankFormulaRow_(tab.sheet, tab.layout);
      lines.push('Tab for ' + monthKey_(today) + ': "' + tab.sheet.getName() + '"');
      lines.push('  categories: ' + tab.layout.categories.join(', '));
      CONFIG.PAYERS.forEach(function (payer) {
        lines.push('  ' + payer.name + ': column ' + tab.layout.payerCols[payer.name] +
                   ' ("' + payer.header + '"), mail from ' + payer.senders.join(', '));
      });
      lines.push(row
        ? '  next receipt would go to row ' + row
        : '  NO BLANK FORMULA ROW LEFT — the formulas need extending down the tab');
    } else {
      lines.push('Tab for ' + monthKey_(today) + ': NOT FOUND — ' +
                 'run listTabs() and set CONFIG.TAB_OVERRIDES');
    }
  } catch (err) {
    lines.push('Spreadsheet: ' + err.message);
  }

  [CONFIG.INBOX_LABEL, CONFIG.FILED_LABEL, CONFIG.REVIEW_LABEL].forEach(function (name) {
    const existed = !!GmailApp.getUserLabelByName(name);
    getLabel_(name);
    lines.push('Label "' + name + '": ' + (existed ? 'present' : 'created'));
  });

  const triggers = ScriptApp.getProjectTriggers().filter(function (trigger) {
    return trigger.getHandlerFunction() === 'processReceipts';
  });
  lines.push('Timer: ' + (triggers.length ? 'installed' : 'not installed — run installTrigger()'));

  const report = lines.join('\n');
  Logger.log(report);
  return report;
}

/** Print every tab, and whether this script recognises it as a month tab. */
function listTabs() {
  const lines = openSpreadsheet_().getSheets().map(function (sheet) {
    const layout = readLayout_(sheet);
    return (layout ? '[month] ' : '[other] ') + sheet.getName();
  });
  const report = lines.join('\n');
  Logger.log(report);
  return report;
}

function installTrigger() {
  removeTriggers();
  ScriptApp.newTrigger('processReceipts').timeBased().everyMinutes(15).create();
  Logger.log('Timer installed: processReceipts every 15 minutes.');
}

function removeTriggers() {
  ScriptApp.getProjectTriggers().forEach(function (trigger) {
    if (trigger.getHandlerFunction() === 'processReceipts') {
      ScriptApp.deleteTrigger(trigger);
    }
  });
}
