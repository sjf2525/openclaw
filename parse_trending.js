const fs = require('fs');

const content = fs.readFileSync('trending.md', 'utf8');

// 提取项目块
const lines = content.split('\n');
const projects = [];
let currentProject = null;

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  
  // 匹配项目标题：## [owner / repo](/owner/repo)
  const titleMatch = line.match(/^## \[([^\/]+) \/\s*([^\]]+)\]\((\/[^)]+)\)$/);
  if (titleMatch) {
    if (currentProject) projects.push(currentProject);
    const owner = titleMatch[1].trim();
    const repo = titleMatch[2].trim();
    const url = `https://github.com${titleMatch[3]}`;
    currentProject = { owner, repo, url, description: '', language: '', stars: '', starsToday: '', builtBy: [] };
    continue;
  }
  
  if (currentProject) {
    // 描述行：标题后的非空行
    if (!currentProject.description && line.trim() && !line.startsWith('#')) {
      currentProject.description = line.trim();
      continue;
    }
    
    // 语言行：例如 "C++"
    if (!currentProject.language && line.match(/^[A-Za-z+#]+$/)) {
      currentProject.language = line.trim();
      continue;
    }
    
    // 星标数：例如 "[1,515](/HailToDodongo/pyrite64/stargazers)"
    const starsMatch = line.match(/\[([\d,]+)\]\([^)]+stargazers\)/);
    if (starsMatch && !currentProject.stars) {
      currentProject.stars = starsMatch[1].replace(/,/g, '');
      continue;
    }
    
    // 今日星标数：例如 "605 stars today"
    const todayMatch = line.match(/(\d+) stars today/);
    if (todayMatch && !currentProject.starsToday) {
      currentProject.starsToday = todayMatch[1];
      continue;
    }
    
    // Built by：例如 "Built by\n /owner1\n /owner2"
    if (line.includes('Built by')) {
      i++;
      while (i < lines.length && lines[i].trim().startsWith('/')) {
        currentProject.builtBy.push(lines[i].trim().substring(1));
        i++;
      }
      continue;
    }
    
    // 如果遇到下一个标题，结束当前项目
    if (line.startsWith('## [')) {
      projects.push(currentProject);
      currentProject = null;
      i--; // 重新处理这一行
    }
  }
}

if (currentProject) projects.push(currentProject);

console.log(JSON.stringify(projects, null, 2));

// 生成简报
console.log('\n=== GitHub Trending 热点项目简报 ===\n');
projects.forEach((p, idx) => {
  console.log(`${idx + 1}. ${p.owner}/${p.repo}`);
  console.log(`   描述: ${p.description}`);
  console.log(`   语言: ${p.language || '未指定'}`);
  console.log(`   星标数: ${p.stars || 'N/A'}`);
  console.log(`   今日新增: ${p.starsToday || 'N/A'} stars`);
  if (p.builtBy.length) console.log(`   主要贡献者: ${p.builtBy.join(', ')}`);
  console.log(`   链接: ${p.url}\n`);
});