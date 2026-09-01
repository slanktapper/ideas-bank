/**
 * Reading a receipt with the Claude Messages API.
 *
 * Raw HTTPS rather than an SDK: Apps Script has no package manager. The response
 * is constrained with output_config.format, so what comes back is the schema below
 * or nothing — there is no prose to parse around.
 */

const ANTHROPIC_ENDPOINT = 'https://api.anthropic.com/v1/messages';
const ANTHROPIC_VERSION = '2023-06-01';

const RECEIPT_SYSTEM_PROMPT = [
  'You read photographs of retail receipts and report what was spent.',
  '',
  'The description you return is written into a shared household spreadsheet',
  'alongside entries a person typed by hand. Match that: the merchant, as someone',
  'would say it out loud, two or three words at most. "Co-op", "Costco gas",',
  '"No Frills", "Mr Lube". Not the legal entity, not the branch number, not the',
  'slogan on the receipt, and never a list of what was bought.',
  '',
  'The total is the final amount actually charged, tax and tip included — the',
  'bottom line, not the subtotal.',
  '',
  'Report low confidence rather than guessing. A blurred total, a date you inferred',
  'from context rather than read, a photo that is not a receipt at all: say so. A',
  'receipt that is left for a human to enter costs a minute; a wrong number in the',
  'spreadsheet can go unnoticed for months.',
].join('\n');

/**
 * @param {string} base64 the attachment, base64-encoded
 * @param {string} mimeType its content type
 * @param {string[]} categories the category names taken from the month tab
 * @return {Object} the parsed extraction (see RECEIPT_SCHEMA)
 */
function readReceipt_(base64, mimeType, categories) {
  const kind = SUPPORTED_TYPES[mimeType];
  if (!kind) throw new Error('Unsupported attachment type: ' + mimeType);

  const source = { type: 'base64', media_type: mimeType, data: base64 };
  const attachmentBlock = kind === 'image'
    ? { type: 'image', source: source }
    : { type: 'document', source: source };

  const body = {
    model: CONFIG.MODEL,
    max_tokens: 4000,
    system: RECEIPT_SYSTEM_PROMPT,
    output_config: {
      effort: CONFIG.EFFORT,
      format: { type: 'json_schema', schema: receiptSchema_(categories) },
    },
    messages: [{
      role: 'user',
      content: [
        attachmentBlock,
        {
          type: 'text',
          text: [
            'Read this receipt.',
            '',
            'Categorise it as one of: ' + categories.join(', ') + '.',
            'If none of them fits, return an empty category rather than the',
            'closest one — a human will pick.',
            '',
            'Dates are day/month/year or month/day/year depending on the till;',
            'use the merchant and the year to work out which, and if the day and',
            'month are genuinely ambiguous, lower your confidence.',
          ].join('\n'),
        },
      ],
    }],
  };

  const response = callAnthropic_(body);

  if (response.stop_reason === 'refusal') {
    throw new Error('Model declined to read this attachment.');
  }
  if (response.stop_reason === 'max_tokens') {
    throw new Error('Response was cut off before the JSON was complete.');
  }

  const text = (response.content || [])
    .filter(function (block) { return block.type === 'text'; })
    .map(function (block) { return block.text; })
    .join('');
  if (!text) throw new Error('Model returned no text block.');

  return JSON.parse(text);
}

/** The shape the model must answer in. Categories come from the sheet, not from here. */
function receiptSchema_(categories) {
  return {
    type: 'object',
    additionalProperties: false,
    required: ['is_receipt', 'description', 'total', 'currency', 'date', 'category', 'confidence', 'notes'],
    properties: {
      is_receipt: {
        type: 'boolean',
        description: 'False if this is not a purchase receipt at all.',
      },
      description: {
        type: 'string',
        description: 'The merchant, two or three words, in the sheet\'s house style.',
      },
      total: {
        anyOf: [{ type: 'number' }, { type: 'null' }],
        description: 'The final amount charged, tax and tip included. Null if unreadable.',
      },
      currency: {
        type: 'string',
        description: 'ISO code, e.g. CAD or USD. Empty string if the receipt does not say.',
      },
      date: {
        type: 'string',
        description: 'The purchase date as YYYY-MM-DD. Empty string if unreadable.',
      },
      category: {
        type: 'string',
        enum: categories.concat(['']),
        description: 'One of the spreadsheet\'s categories, or empty if none fits.',
      },
      confidence: {
        type: 'string',
        enum: ['high', 'medium', 'low'],
        description: 'Confidence in the total and the date specifically.',
      },
      notes: {
        type: 'string',
        description: 'Anything a human would need to know. Empty if nothing.',
      },
    },
  };
}

/** POST with a short retry on the failures that are worth retrying. */
function callAnthropic_(body) {
  const key = PropertiesService.getScriptProperties().getProperty('ANTHROPIC_API_KEY');
  if (!key) {
    throw new Error('ANTHROPIC_API_KEY is not set in Script Properties. See setup.md.');
  }

  const options = {
    method: 'post',
    contentType: 'application/json',
    headers: { 'x-api-key': key, 'anthropic-version': ANTHROPIC_VERSION },
    payload: JSON.stringify(body),
    muteHttpExceptions: true,
  };

  let lastError = '';
  for (let attempt = 0; attempt < 3; attempt++) {
    if (attempt > 0) Utilities.sleep(2000 * Math.pow(2, attempt - 1));

    const response = UrlFetchApp.fetch(ANTHROPIC_ENDPOINT, options);
    const status = response.getResponseCode();
    const text = response.getContentText();

    if (status === 200) return JSON.parse(text);

    lastError = 'HTTP ' + status + ': ' + text.slice(0, 500);
    // 429 and 5xx are worth another go; 400/401/403 will fail identically forever.
    if (status !== 429 && status < 500) break;
  }
  throw new Error('Anthropic API call failed. ' + lastError);
}
