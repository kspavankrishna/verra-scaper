import fs from 'node:fs/promises';
import path from 'node:path';
import nodemailer from 'nodemailer';
import { chromium } from 'playwright';

const PAGE_URL = 'https://registry.verra.org/app/projectDetail/VCS/3506';
const SNAPSHOT_DIR = path.resolve('verra-snapshot');
const SNAPSHOT_PATH = path.join(SNAPSHOT_DIR, 'snapshot.txt');
const EMAIL_SUBJECT = 'ALERT: Verra Registry VCS/3506 page has changed';

const VOLATILE_LABEL_PATTERN =
  /^(last updated|updated(?: at| on)?|timestamp|generated(?: at| on)?|printed(?: at| on)?|retrieved(?: at| on)?|downloaded(?: at| on)?|as of)\b/i;
const DATE_TIME_VALUE_PATTERN =
  /\b(?:\d{4}-\d{2}-\d{2}(?:[ t]\d{2}:\d{2}(?::\d{2})?(?:\s?(?:UTC|GMT|Z|[AP]M|[A-Z]{2,5}))?)?|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s+\d{1,2},?\s+\d{4}(?:\s+\d{1,2}:\d{2}(?::\d{2})?\s?(?:am|pm)?)?)\b/i;
const TIME_ONLY_PATTERN = /\b\d{1,2}:\d{2}(?::\d{2})?\s?(?:am|pm|UTC|GMT|[A-Z]{2,5})?\b/i;

async function ensureSnapshotDir() {
  await fs.mkdir(SNAPSHOT_DIR, { recursive: true });
}

function isVolatileLine(line) {
  return VOLATILE_LABEL_PATTERN.test(line) && (DATE_TIME_VALUE_PATTERN.test(line) || TIME_ONLY_PATTERN.test(line));
}

function normalizeContent(content) {
  return content
    .replace(/\r\n/g, '\n')
    .replace(/\u00a0/g, ' ')
    .split('\n')
    .map((line) => line.replace(/[ \t]+/g, ' ').trim())
    .filter((line) => line.length > 0)
    .filter((line) => !isVolatileLine(line))
    .join('\n')
    .trim();
}

async function readPreviousSnapshot() {
  try {
    return await fs.readFile(SNAPSHOT_PATH, 'utf8');
  } catch (error) {
    if (error.code === 'ENOENT') {
      return null;
    }

    throw error;
  }
}

async function writeSnapshot(content) {
  await ensureSnapshotDir();
  await fs.writeFile(SNAPSHOT_PATH, content, 'utf8');
}

async function launchBrowser() {
  try {
    return await chromium.launch({ headless: true });
  } catch (error) {
    console.error('Failed to launch Playwright Chromium.', error);
    throw error;
  }
}

async function sendNotificationEmail(detectedAt) {
  const { GMAIL_USER, GMAIL_APP_PASSWORD, NOTIFY_EMAIL } = process.env;

  if (!GMAIL_USER || !GMAIL_APP_PASSWORD || !NOTIFY_EMAIL) {
    throw new Error(
      'Missing one or more required environment variables: GMAIL_USER, GMAIL_APP_PASSWORD, NOTIFY_EMAIL.'
    );
  }

  const transporter = nodemailer.createTransport({
    host: 'smtp.gmail.com',
    port: 465,
    secure: true,
    auth: {
      user: GMAIL_USER,
      pass: GMAIL_APP_PASSWORD,
    },
  });

  try {
    await transporter.sendMail({
      from: GMAIL_USER,
      to: NOTIFY_EMAIL,
      subject: EMAIL_SUBJECT,
      text: [
        'The monitored Verra Registry VCS/3506 page has changed.',
        `Detected at: ${detectedAt}`,
        `URL: ${PAGE_URL}`,
      ].join('\n'),
    });
  } catch (error) {
    console.error('Failed to send notification email.', error);
    throw error;
  }
}

async function getCurrentPageContent(browser) {
  const page = await browser.newPage();

  await page.goto(PAGE_URL, {
    timeout: 120000,
    waitUntil: 'domcontentloaded',
  });
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(5000);

  const content = await page.evaluate(() => document.body?.innerText ?? '');
  await page.close();

  if (!content.trim()) {
    throw new Error('Rendered page content was empty.');
  }

  return content;
}

async function main() {
  let browser;

  try {
    browser = await launchBrowser();

    const currentContent = await getCurrentPageContent(browser);
    const previousContent = await readPreviousSnapshot();

    if (previousContent === null) {
      await writeSnapshot(currentContent);
      console.log('First run — baseline saved');
      return;
    }

    const normalizedPreviousContent = normalizeContent(previousContent);
    const normalizedCurrentContent = normalizeContent(currentContent);

    if (normalizedCurrentContent === normalizedPreviousContent) {
      await writeSnapshot(currentContent);
      console.log('No change detected');
      return;
    }

    console.log('Change detected');
    await sendNotificationEmail(new Date().toISOString());
    await writeSnapshot(currentContent);
  } catch (error) {
    console.error('Verra monitor failed.', error);
    process.exitCode = 1;
  } finally {
    if (browser) {
      try {
        await browser.close();
      } catch (error) {
        console.error('Failed to close Playwright Chromium cleanly.', error);
      }
    }
  }
}

await main();
