#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

def fetch_baidu_hotsearch():
    """抓取百度热搜"""
    urls = [
        'https://www.baidu.com',
        'https://top.baidu.com/board?tab=realtime',
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }
    
    for url in urls:
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.encoding = 'utf-8'
            if resp.status_code == 200:
                return resp.text, url
        except:
            continue
    return None, None

def fetch_weibo_hotsearch():
    """抓取微博热搜（备选）"""
    url = 'https://s.weibo.com/top/summary'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.encoding = 'utf-8'
        return resp.text, url
    except Exception as e:
        print(f'Weibo error: {e}')
        return None, None

def parse_baidu(html):
    """解析百度热搜"""
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    hot_list = []
    
    # 百度热搜通常在特定的容器中
    # 尝试多种选择器
    containers = soup.find_all('div', {'class': lambda x: x and ('hot' in x.lower() or 'top' in x.lower())})
    
    for container in containers:
        links = container.find_all('a', href=True)
        for link in links:
            title = link.get_text(strip=True)
            if title and len(title) > 1:
                hot_list.append(title)
    
    return hot_list[:20]

def parse_weibo(html):
    """解析微博热搜"""
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    hot_list = []
    
    # 微博热搜在 .tablist 容器中
    table = soup.find('table', class_='tab-list')
    if table:
        rows = table.find_all('tr')
        for row in rows:
            td = row.find('td', class_='td-02')
            if td:
                link = td.find('a')
                if link:
                    title = link.get_text(strip=True)
                    hotspot = row.find('span', class_='icon-wrap')
                    hotspot_text = hotspot.get_text(strip=True) if hotspot else ''
                    hot_list.append({
                        'title': title,
                        'hotspot': hotspot_text
                    })
    
    return hot_list

def main():
    print("=" * 80)
    print("🔥 全网热搜热点简报")
    print("=" * 80)
    print(f"抓取时间：2026-02-19 08:49 UTC")
    print("=" * 80)
    
    # 尝试微博热搜（更可靠）
    print("\n正在抓取微博热搜...")
    html, url = fetch_weibo_hotsearch()
    
    if html:
        hot_list = parse_weibo(html)
        if hot_list:
            print(f"\n✅ 微博热搜 TOP {len(hot_list)}\n")
            for i, item in enumerate(hot_list[:15], 1):
                hotspot = f" [{item['hotspot']}]" if item['hotspot'] else ""
                print(f"{i}. {item['title']}{hotspot}")
            print("\n" + "=" * 80)
            return
    
    # 备选：百度
    print("\n微博抓取失败，尝试百度...")
    html, url = fetch_baidu_hotsearch()
    
    if html:
        hot_list = parse_baidu(html)
        if hot_list:
            print(f"\n✅ 百度热搜 TOP {len(hot_list)}\n")
            for i, title in enumerate(hot_list, 1):
                print(f"{i}. {title}")
            print("\n" + "=" * 80)
            return
    
    print("\n❌ 无法获取热搜数据")
    print("=" * 80)

if __name__ == '__main__':
    main()
