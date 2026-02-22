const puppeteer = require('puppeteer-core');
const chromePath = '/usr/bin/google-chrome-stable';

(async () => {
  console.log('Testing headless Chrome...');
  const browser = await puppeteer.launch({
    executablePath: chromePath,
    headless: true,
    args: ['--no-sandbox', '--disable-gpu']
  });
  const page = await browser.newPage();
  await page.goto('https://example.com');
  const title = await page.title();
  console.log('Title:', title);
  await page.screenshot({ path: 'headless_screenshot.png' });
  await browser.close();
  console.log('Headless test passed.');
})();