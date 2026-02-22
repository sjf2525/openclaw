const fs = require('fs');

const content = fs.readFileSync('trending.md', 'utf8');
const lines = content.split('\n');

const projects = [];
let current = null;
let state = 'outside'; // outside, inTitle, inDesc, inMeta

function finalizeProject() {
  if (current) {
    projects.push(current);
    current = null;
  }
}

for (let i = 0; i < lines.length; i++) {
  const line = lines[i].trim();
  
  // 检测新项目标题
  if (line.startsWith('## [')) {
    finalizeProject();
    current = { owner: '', repo: '', url: '', description: '', language: '', stars: '', starsToday: '', builtBy: [] };
    // 提取owner和repo，可能跨行
    let titleLine = line;
    // 如果owner和repo跨行，合并后续行直到']'
    while (!titleLine.includes('](') && i + 1 < lines.length) {
      i++;
      titleLine += ' ' + lines[i].trim();
    }
    // 现在匹配模式
    const match = titleLine.match(/## \[([^\/]+) \/\s*([^\]]+)\]\((\/[^)]+)\)/);
    if (match) {
      current.owner = match[1].trim();
      current.repo = match[2].trim();
      current.url = 'https://github.com' + match[3];
    }
    state = 'inDesc';
    continue;
  }
  
  if (current) {
    // 描述：标题后的第一个非空行
    if (state === 'inDesc' && line) {
      current.description = line;
      state = 'inMeta';
      continue;
    }
    
    // 语言：可能单独一行，如 "C++"
    if (state === 'inMeta' && /^[A-Za-z+#]+$/.test(line)) {
      current.language = line;
      continue;
    }
    
    // 星标数
    const starsMatch = line.match(/\[([\d,]+)\]\([^)]+stargazers\)/);
    if (starsMatch) {
      current.stars = starsMatch[1].replace(/,/g, '');
      continue;
    }
    
    // 今日星标
    const todayMatch = line.match(/(\d+) stars today/);
    if (todayMatch) {
      current.starsToday = todayMatch[1];
      continue;
    }
    
    // Built by
    if (line.includes('Built by')) {
      i++;
      while (i < lines.length && lines[i].trim().startsWith('/')) {
        current.builtBy.push(lines[i].trim().substring(1));
        i++;
      }
      i--; // 调整索引
      continue;
    }
    
    // 如果遇到空行且已有描述，可能忽略
    // 如果遇到下一个标题，将在下一轮处理
  }
}

finalizeProject();

console.log(JSON.stringify(projects, null, 2));

// 生成简报
console.log('\n=== GitHub Trending 热点项目简报（中文）===\n');
projects.forEach((p, idx) => {
  console.log(`${idx + 1}. ${p.owner}/${p.repo}`);
  console.log(`   描述: ${p.description}`);
  console.log(`   语言: ${p.language || '未指定'}`);
  console.log(`   星标数: ${p.stars || 'N/A'}`);
  console.log(`   今日新增: ${p.starsToday || 'N/A'} stars`);
  if (p.builtBy.length) console.log(`   主要贡献者: ${p.builtBy.join(', ')}`);
  console.log(`   链接: ${p.url}\n`);
});