const puppeteer = require('puppeteer-core');
const fs = require('fs');
const chromePath = '/usr/bin/google-chrome-stable';

async function fetchGitHubTrending() {
  console.log('正在抓取 GitHub Trending 项目...');
  const browser = await puppeteer.launch({
    executablePath: chromePath,
    headless: true,
    args: ['--no-sandbox', '--disable-gpu']
  });
  const page = await browser.newPage();
  await page.goto('https://github.com/trending', { waitUntil: 'networkidle2', timeout: 30000 });
  
  await page.waitForSelector('article.Box-row', { timeout: 10000 });
  
  const projects = await page.evaluate(() => {
    const items = document.querySelectorAll('article.Box-row');
    const data = [];
    items.forEach((item) => {
      const titleEl = item.querySelector('h2 a');
      let title = titleEl ? titleEl.textContent.trim() : '';
      // 清理标题中的多余空格和换行
      title = title.replace(/\s+/g, ' ');
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
  
  await browser.close();
  console.log(`抓取完成，共 ${projects.length} 个项目`);
  return projects;
}

function generateMarkdown(projects) {
  let markdown = `# GitHub Trending 热点项目简报\n\n`;
  markdown += `更新时间: ${new Date().toISOString().replace('T', ' ').substring(0, 19)} UTC\n\n`;
  markdown += `> 本简报自动抓取 GitHub Trending 页面，每日更新。\n\n`;
  
  projects.forEach((p, idx) => {
    markdown += `## ${idx + 1}. ${p.title}\n\n`;
    markdown += `- **描述**: ${p.description}\n`;
    markdown += `- **语言**: ${p.language || '未指定'}\n`;
    markdown += `- **星标数**: ${p.stars || 'N/A'}\n`;
    markdown += `- **今日新增**: ${p.starsToday || 'N/A'} stars\n`;
    if (p.builtBy.length) {
      markdown += `- **主要贡献者**: ${p.builtBy.join(', ')}\n`;
    }
    markdown += `- **项目链接**: [${p.url}](${p.url})\n\n`;
  });
  
  markdown += `---\n`;
  markdown += `*简报由 OpenClaw 自动生成，数据来源: [GitHub Trending](https://github.com/trending)*\n`;
  return markdown;
}

async function main() {
  try {
    const projects = await fetchGitHubTrending();
    const markdown = generateMarkdown(projects);
    const filename = 'github_trending_brief.md';
    fs.writeFileSync(filename, markdown, 'utf8');
    console.log(`简报已保存到 ${filename}`);
    console.log(`文件预览:\n`);
    console.log(markdown);
  } catch (error) {
    console.error('生成简报失败:', error);
    process.exit(1);
  }
}

main();