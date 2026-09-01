/**
 * The Gmail side: labels, attachments, and the record of what has already been done.
 *
 * The script reads exactly one label. Nothing else in the mailbox is touched, and
 * nothing is ever deleted — filing a receipt moves a label, that is all.
 */

function getLabel_(name) {
  return GmailApp.getUserLabelByName(name) || GmailApp.createLabel(name);
}

/** Threads waiting to be filed, oldest first so receipts land in the order they arrived. */
function pendingThreads_() {
  const threads = getLabel_(CONFIG.INBOX_LABEL).getThreads(0, CONFIG.MAX_THREADS_PER_RUN);
  return threads.reverse();
}

/** Attachments worth sending to the model: images and PDFs, inline ones included. */
function receiptAttachments_(message) {
  return message
    .getAttachments({ includeInlineImages: true, includeAttachments: true })
    .filter(function (attachment) {
      return Object.prototype.hasOwnProperty.call(
        SUPPORTED_TYPES, normaliseType_(attachment.getContentType()));
    });
}

/**
 * What the script knows about the mail carrying a receipt: who sent it, and what
 * it said. The address decides who paid; the text can override that in words.
 */
function mailContext_(message) {
  return {
    from: senderAddress_(message),
    text: emailText_(message),
  };
}

/** The bare address out of 'Rob Sinclair <rob@example.com>', lowercased. */
function senderAddress_(message) {
  const from = String(message.getFrom() || '');
  const angled = /<([^>]+)>/.exec(from);
  return (angled ? angled[1] : from).trim().toLowerCase();
}

/**
 * Subject and body, trimmed to something worth sending. Long bodies are almost
 * always a quoted thread underneath a one-line note, and the note is at the top.
 */
function emailText_(message) {
  const subject = String(message.getSubject() || '').trim();
  const body = String(message.getPlainBody() || '').trim();
  const text = (subject ? 'Subject: ' + subject + '\n\n' : '') + body;
  return text.length > 2000 ? text.slice(0, 2000) + '\n…' : text;
}

/** Content types arrive as 'image/jpeg; name="x.jpg"' often enough to be worth stripping. */
function normaliseType_(contentType) {
  return String(contentType).split(';')[0].trim().toLowerCase();
}

/**
 * Has this message already been handled? The label move is the main guard; this is
 * the second one, for a run that dies halfway through a thread.
 */
function alreadyProcessed_(messageId) {
  return processedIds_().indexOf(messageId) !== -1;
}

function markProcessed_(messageId) {
  const ids = processedIds_();
  if (ids.indexOf(messageId) !== -1) return;
  ids.push(messageId);
  // Keep the list bounded — Script Properties are not a database.
  const trimmed = ids.slice(Math.max(0, ids.length - 500));
  PropertiesService.getScriptProperties()
    .setProperty('PROCESSED_MESSAGE_IDS', JSON.stringify(trimmed));
}

function processedIds_() {
  const raw = PropertiesService.getScriptProperties().getProperty('PROCESSED_MESSAGE_IDS');
  if (!raw) return [];
  try {
    return JSON.parse(raw);
  } catch (err) {
    return [];
  }
}

/** Move a thread out of the intake label and into its outcome. */
function fileThread_(thread, labelName) {
  getLabel_(labelName).addToThread(thread);
  getLabel_(CONFIG.INBOX_LABEL).removeFromThread(thread);
}

/** A short note about anything that needs a human. Silent when everything filed cleanly. */
function sendDigest_(problems) {
  if (!CONFIG.DIGEST_TO || !problems.length) return;
  const lines = problems.map(function (problem) {
    return '• ' + problem.subject + ' — ' + problem.reason;
  });
  GmailApp.sendEmail(
    CONFIG.DIGEST_TO,
    problems.length + ' receipt' + (problems.length === 1 ? '' : 's') + ' need a look',
    ['These are labelled ' + CONFIG.REVIEW_LABEL + ' in Gmail:', ''].concat(lines).join('\n'));
}
