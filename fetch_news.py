#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

def fetch_page(page_num):
    """抓取东方财富网热点扫描第 N 页"""
    if page_num == 1:
        url = 'https://finance.eastmoney.com/a/crdsm.html'
    else:
        url = f'https://finance.eastmoney.com/a/crdsm_{page_num}.html'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.encoding = 'utf-8'
        return resp.text
    except Exception as e:
        print(f'Error fetching page {page_num}: {e}')
        return None

def parse_news(html):
    """解析 HTML 提取新闻列表"""
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    news_list = []
    
    # 查找新闻列表容器
    # 东方财富网的新闻通常在 .newslist 或类似的容器中
    news_containers = soup.find_all('div', class_='newslist') or soup.find_all('ul', class_='newslist')
    
    if not news_containers:
        # 尝试其他可能的选择器
        news_containers = soup.find_all('div', {'class': lambda x: x and 'news' in x.lower()})
    
    for container in news_containers:
        links = container.find_all('a', href=True)
        for link in links:
            title = link.get_text(strip=True)
            href = link['href']
            # 过滤掉非新闻链接
            if title and len(title) > 5 and 'eastmoney' in href:
                # 提取时间（如果有）
                time_elem = link.find_parent('li').find('span', class_='time') if link.find_parent('li') else None
                pub_time = time_elem.get_text(strip=True) if time_elem else ''
                
                news_list.append({
                    'title': title,
                    'url': href,
                    'time': pub_time
                })
    
    return news_list

def main():
    all_news = []
    
    print("正在抓取东方财富网热点扫描前 5 页...\n")
    
    for page in range(1, 6):
        print(f"抓取第 {page} 页...")
        html = fetch_page(page)
        if html:
            news = parse_news(html)
            print(f"  找到 {len(news)} 条新闻")
            all_news.extend(news)
        else:
            print(f"  第 {page} 页抓取失败")
    
    print(f"\n总共抓取到 {len(all_news)} 条新闻\n")
    
    # 去重
    seen = set()
    unique_news = []
    for n in all_news:
        if n['url'] not in seen:
            seen.add(n['url'])
            unique_news.append(n)
    
    print(f"去重后 {len(unique_news)} 条新闻\n")
    
    # 输出简报
    print("=" * 80)
    print("财经热点新闻简报")
    print("=" * 80)
    print(f"来源：东方财富网 - 热点扫描")
    print(f"抓取时间：2026-02-19")
    print(f"页数：前 5 页")
    print(f"新闻数量：{len(unique_news)} 条")
    print("=" * 80)
    
    for i, news in enumerate(unique_news, 1):
        print(f"\n{i}. {news['title']}")
        print(f"   链接：{news['url']}")
        if news['time']:
            print(f"   时间：{news['time']}")
    
    print("\n" + "=" * 80)
    
    return unique_news

if __name__ == '__main__':
    main()
