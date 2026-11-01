const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

async function main() {
  const screenshotsDir = path.join(__dirname, '..', 'docs', 'screenshots');
  fs.mkdirSync(screenshotsDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 2,
    colorScheme: 'dark'
  });

  const page = await context.newPage();

  const targets = [
    {
      url: 'http://127.0.0.1:3456/',
      file: '01_dashboard.png',
      waitFor: 'h1'
    },
    {
      url: 'http://127.0.0.1:3456/keys.html',
      file: '02_api_keys.png',
      waitFor: 'h1'
    },
    {
      url: 'http://127.0.0.1:3456/providers.html',
      file: '03_providers_models.png',
      waitFor: 'h1'
    },
    {
      url: 'http://127.0.0.1:3456/requests.html',
      file: '04_request_logs.png',
      waitFor: 'h1'
    }
  ];

  for (const t of targets) {
    console.log(`Navigating to ${t.url} -> ${t.file}...`);
    await page.goto(t.url, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForSelector(t.waitFor);
    await page.waitForTimeout(1000); // Wait for Tailwind font & styles rendering

    const outPath = path.join(screenshotsDir, t.file);
    await page.screenshot({ path: outPath, fullPage: false });
    console.log(`Saved screenshot: ${outPath} (${fs.statSync(outPath).size} bytes)`);
  }

  await browser.close();
  console.log('All ModelGate screenshots captured successfully.');
}

main().catch(err => {
  console.error('Error in capture:', err);
  process.exit(1);
});
