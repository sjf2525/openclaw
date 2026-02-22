const puppeteer = require('puppeteer-core');
const chromePath = '/usr/bin/google-chrome-stable';

(async () => {
  console.log('Launching browser...');
  const browser = await puppeteer.launch({
    executablePath: chromePath,
    headless: true,
    args: ['--no-sandbox', '--disable-gpu']
  });
  const page = await browser.newPage();
  await page.goto('https://github.com/trending', { waitUntil: 'networkidle2', timeout: 30000 });
  
  // 等待项目加载
  await page.waitForSelector('article.Box-row', { timeout: 10000 });
  
  const projects = await page.evaluate(() => {
    const items = document.querySelectorAll('article.Box-row');
    const data = [];
    items.forEach((item) => {
      const titleEl = item.querySelector('h2 a');
      const title = titleEl ? titleEl.textContent.trim() : '';
      const href = titleEl ? titleEl.getAttribute('href') : '';
      const descEl = item.querySelector('p');
      const description = descEl ? descEl.textContent.trim() : '';
      const langEl = item.querySelector('[itemprop="programmingLanguage"]');
      const language = langEl ? langEl.textContent.trim() : '';
      const starsEl = item.querySelector('a[href$="stargazers"]');
      let stars = '';
      if (starsEl) {
        const starsText = starsEl.textContent.trim();
        stars = starsText.replace(',', '');
      }
      const starsTodayEl = item.querySelector('span.d-inline-block.float-sm-right');
      let starsToday = '';
      if (starsTodayEl) {
        const todayText = starsTodayEl.textContent.trim();
        const match = todayText.match(/(\d+)\s+stars\s+today/);
        if (match) starsToday = match[1];
      }
      const builtBy = [];
      const builtByEls = item.querySelectorAll('a[data-hovercard-type="user"]');
      builtByEls.forEach(el => {
        const user = el.getAttribute('href').substring(1);
        if (user) builtBy.push(user);
      });
      data.push({
        title,
        url: 'https://github.com' + href,
        description,
        language,
        stars,
        starsToday,
        builtBy
      });
    });
    return data;
  });
  
  console.log('Found', projects.length, 'projects');
  console.log(JSON.stringify(projects, null, 2));
  
  // 生成简报
  console.log('\n=== GitHub Trending 热点项目简报（中文）===\n');
  projects.forEach((p, idx) => {
    console.log(`${idx + 1}. ${p.title}`);
    console.log(`   描述: ${p.description}`);
    console.log(`   语言: ${p.language || '未指定'}`);
    console.log(`   星标数: ${p.stars || 'N/A'}`);
    console.log(`   今日新增: ${p.starsToday || 'N/A'} stars`);
    if (p.builtBy.length) console.log(`   主要贡献者: ${p.builtBy.join(', ')}`);
    console.log(`   链接: ${p.url}\n`);
  });
  
  await browser.close();
})().catch(err => {
  console.error('Error:', err);
});