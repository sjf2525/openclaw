#!/usr/bin/env python3
import requests
import json

def fetch_zhihu_hot():
    """抓取知乎热榜"""
    url = 'https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=20&reverse_order=0'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('data', [])
    except Exception as e:
        print(f'知乎错误：{e}')
    return []

def fetch_douyin_hot():
    """抓取抖音热榜"""
    url = 'https://www.douyin.com/aweme/v1/web/hot/search/list/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('data', {}).get('word_list', [])
    except Exception as e:
        print(f'抖音错误：{e}')
    return []

def fetch_36kr_hot():
    """抓取 36 氪热点"""
    url = 'https://36kr.com/api/newsflash?per_page=20'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('data', {}).get('items', [])
    except Exception as e:
        print(f'36 氪错误：{e}')
    return []

def main():
    print("=" * 80)
    print("🔥 全网热点热搜简报")
    print("=" * 80)
    print(f"抓取时间：2026-02-19 08:49 UTC")
    print("=" * 80)
    
    # 知乎热榜
    print("\n【知乎热榜 TOP 10】\n")
    zhihu = fetch_zhihu_hot()
    if zhihu:
        for i, item in enumerate(zhihu[:10], 1):
            target = item.get('target', {})
            title = target.get('title', 'N/A')
            excerpt = target.get('excerpt', '')[:50]
            print(f"{i}. {title}")
            if excerpt:
                print(f"   {excerpt}...")
    else:
        print("无法获取知乎热榜")
    
    # 36 氪快讯
    print("\n" + "=" * 80)
    print("\n【36 氪·24 小时快讯 TOP 10】\n")
    kr = fetch_36kr_hot()
    if kr:
        for i, item in enumerate(kr[:10], 1):
            title = item.get('title', 'N/A')
            print(f"{i}. {title}")
    else:
        print("无法获取 36 氪快讯")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()
