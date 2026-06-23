/**
 * Automated screenshot capture for the Kontekst Chat guide.
 * Requires: .env file in this directory (copy from .env.example)
 * Runs two browser contexts to simulate host + guest.
 *
 * ADJUSTING SELECTORS: If the UI changes, search for "SELECTOR:" comments
 * and update the strings to match the new element text or CSS.
 */

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

require('dotenv').config({ path: path.join(__dirname, '.env') });

const BASE_URL = (process.env.KONTEKST_URL || 'https://staging.fjeldmann.dk').replace(/\/$/, '');
const EMAIL = process.env.KONTEKST_EMAIL;
const PASSWORD = process.env.KONTEKST_PASSWORD;
const IMAGES_DIR = path.join(__dirname, '..', 'images');

// Must match the viewport assumed by annotate_images.py coordinate set
const VIEWPORT = { width: 1280, height: 800 };
const WAIT = 800; // ms to settle after interactions

if (!EMAIL || !PASSWORD) {
  console.error('Missing KONTEKST_EMAIL or KONTEKST_PASSWORD in scripts/.env');
  process.exit(1);
}

async function shot(page, name) {
  await page.waitForTimeout(WAIT);
  const filepath = path.join(IMAGES_DIR, name);
  await page.screenshot({ path: filepath, fullPage: false });
  console.log(`  [screenshot] ${name}`);
}

async function login(page) {
  console.log(`\nLogging in to ${BASE_URL} ...`);
  await page.goto(`${BASE_URL}/login`);
  await page.waitForLoadState('networkidle');

  // SELECTOR: email field — adjust if the form uses a different attribute
  await page.locator('input[type="email"], input[name="email"]').fill(EMAIL);
  // SELECTOR: password field
  await page.locator('input[type="password"]').fill(PASSWORD);
  // SELECTOR: submit button
  await page.locator('button[type="submit"]').click();

  // Wait for redirect away from /login
  await page.waitForURL(url => !url.pathname.includes('login'), { timeout: 15000 });
  console.log('  Logged in.');
}

async function navigateToChat(page) {
  // Production chat URL is /chat — adjust if staging uses a different path
  if (!page.url().includes('/chat')) {
    await page.goto(`${BASE_URL}/chat`);
    await page.waitForLoadState('networkidle');
  }
}

async function run() {
  console.log('Starting Kontekst Chat screenshot automation...\n');

  const browser = await chromium.launch({
    headless: false, // visible so you can intervene if needed
    slowMo: 200,
  });

  // ── HOST context ──────────────────────────────────────────────────────────
  const hostCtx = await browser.newContext({
    viewport: VIEWPORT,
    permissions: ['clipboard-read', 'clipboard-write'],
  });
  const host = await hostCtx.newPage();
  await login(host);
  await navigateToChat(host);
  await host.waitForLoadState('networkidle');

  // Trin 1 — Lobby before adding anyone
  await shot(host, 'chat lobby.png');

  // Click "Tilføj deltager" (Add participant)
  // SELECTOR: the button that opens the invite panel
  await host.locator('button, [role="button"]').filter({ hasText: /tilf.j deltager/i }).first().click();
  await shot(host, 'chat invite.png');

  // Trin 2 — Fill in name; language is pre-selected so we leave it
  // SELECTOR: name input in the invite form
  const nameInput = host.locator('input[placeholder*="Navn" i], input[placeholder*="name" i], input[name*="name" i]').first();
  await nameInput.fill('Mia');
  // SELECTOR: language selector — click it to show the dropdown is interactive
  // (we leave the default language; if you need to change it, add a click here)
  await shot(host, 'chat invite filled name .png');

  // Confirm the invitation (checkmark / flueben)
  // SELECTOR: confirm button next to the name input
  await host.locator('button[aria-label*="Bekr" i], button[aria-label*="confirm" i], [class*="confirm" i], button:has-text("✓")').first().click();
  await shot(host, 'chat qr after invitation.png');

  // ── Grab join URL for guest ───────────────────────────────────────────────
  // Try to find a copy-link button and read from clipboard; fall back to href
  let joinUrl = null;
  try {
    // SELECTOR: the "copy link" button on the QR page
    await host.locator('button, [role="button"]').filter({ hasText: /kopi/i }).first().click();
    joinUrl = await host.evaluate(() => navigator.clipboard.readText());
    console.log(`  Join URL (clipboard): ${joinUrl}`);
  } catch {
    // Fallback: look for an <a> pointing to a join page
    const linkEl = host.locator('a[href*="/join"], a[href*="/chat/join"], a[href*="code="], a[href*="token="]').first();
    joinUrl = await linkEl.getAttribute('href').catch(() => null);
    if (joinUrl && !joinUrl.startsWith('http')) {
      joinUrl = `${BASE_URL}${joinUrl}`;
    }
    console.log(`  Join URL (link): ${joinUrl}`);
  }

  if (!joinUrl) {
    console.error(
      '\n  Could not find the guest join URL automatically.\n' +
      '  Please open scripts/take-screenshots.js and update the join URL extraction (search for "joinUrl").\n'
    );
    await browser.close();
    process.exit(1);
  }

  // ── GUEST context ─────────────────────────────────────────────────────────
  const guestCtx = await browser.newContext({ viewport: VIEWPORT });
  const guest = await guestCtx.newPage();
  await guest.goto(joinUrl);
  await guest.waitForLoadState('networkidle');

  // Trin 4 — Guest join page (name + language pre-filled)
  await shot(guest, 'join page.png');

  // Guest clicks Join / Deltag
  // SELECTOR: the join button on the guest page
  await guest.locator('button, [role="button"]').filter({ hasText: /join|deltag/i }).first().click();

  // ── Back to host ──────────────────────────────────────────────────────────
  await host.bringToFront();
  await host.waitForTimeout(WAIT);

  // Trin 5 — Lobby with pending guest request
  await shot(host, 'chat lobby after join.png');

  // Accept (green checkmark)
  // SELECTOR: accept button in the participant request row
  await host.locator(
    'button[aria-label*="Accepter" i], button[aria-label*="accept" i], [class*="accept" i], button:has-text("✓")'
  ).first().click();

  // Trin 6 — Lobby after accepting
  await shot(host, 'chat lobby after accept.png');

  // Start session
  // SELECTOR: "Start samtale" button
  await host.locator('button, [role="button"]').filter({ hasText: /start samtale/i }).first().click();
  await host.waitForLoadState('networkidle');

  // Trin 7 — Active session (idle)
  await shot(host, 'chat session .png');

  // Trin 8 — Click microphone to start recording
  // SELECTOR: microphone / record button in the session view
  await host.locator(
    '[aria-label*="mikrofon" i], [aria-label*="optag" i], [aria-label*="record" i], [class*="mic" i], [class*="record" i]'
  ).first().click();
  await shot(host, 'chat session recording.png');

  // Stop recording (click same button or a stop button)
  await host.locator(
    '[aria-label*="stop" i], [class*="stop" i], [aria-label*="mikrofon" i], [aria-label*="record" i], [class*="mic" i]'
  ).first().click();

  // Trin 9 — Transcribed text in the send field
  await shot(host, 'chat session send.png');

  // Send the message so guest receives it
  // SELECTOR: send button
  await host.locator(
    'button[aria-label*="send" i], button[aria-label*="afsend" i], [class*="send" i], button:has-text("Send")'
  ).first().click();

  // Switch to guest to receive the message and capture from host perspective
  await host.waitForTimeout(WAIT * 2);
  await host.bringToFront();

  // Trin 10 — Received message view
  await shot(host, 'chat session message recieved.png');

  // ─────────────────────────────────────────────────────────────────────────
  await browser.close();
  console.log('\nAll screenshots saved to images/');
}

run().catch(err => {
  console.error('\nScript failed:', err.message);
  process.exit(1);
});
