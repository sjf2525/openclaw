#!/usr/bin/env python3
"""
下载惊蛰相关图片
"""

import os
import requests
from pathlib import Path
import time

# 项目路径
PROJECT_DIR = Path(__file__).parent
IMAGE_DIR = PROJECT_DIR / "images"
IMAGE_DIR.mkdir(exist_ok=True)

# 从tavily_search结果中获取的图片URL
image_urls = [
    "https://photo.16pic.com/00/94/34/16pic_9434111_b.jpg",  # 惊蛰图片1
    "https://photo.16pic.com/00/94/33/16pic_9433791_b.jpg",  # 惊蛰图片2
    "http://img.daimg.com/uploads/allimg/250304/1-250304114H0.jpg",  # 惊蛰图片3
    "https://p3-pc-sign.douyinpic.com/tos-cn-i-0813c001/oMAAHLUFFjeKGC4A7eMEhLBlAEIJBDAIwPkeER~tplv-dy-aweme-images-v2:3000:3000:q75.webp?biz_tag=aweme_images&from=327834062&lk3s=138a59ce&s=PackSourceEnum_SEARCH&sc=image&se=false&x-expires=1774220400&x-signature=Cc7LFXalfJ4kFYnWXsj3Hm%2Fjr0M%3D",  # 惊蛰图片4
    "https://pic.ibaotu.com/02/42/26/58t888piCCpy.jpg!ww7006",  # 惊蛰图片5
]

# 图片描述（用于文件名）
image_descriptions = [
    "jingzhe_spring_thunder",
    "jingzhe_insects",
    "jingzhe_spring_rain",
    "jingzhe_peach_blossom",
    "jingzhe_farming"
]

def download_image(url, filename, retry=3):
    """下载图片"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(retry):
        try:
            print(f"下载: {filename} (尝试 {attempt + 1}/{retry})")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 保存图片
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            file_size = os.path.getsize(filename)
            print(f"  成功: {filename} ({file_size} 字节)")
            return True
            
        except Exception as e:
            print(f"  错误: {e}")
            if attempt < retry - 1:
                time.sleep(1)
    
    return False

def main():
    """主函数"""
    print("=" * 50)
    print("下载惊蛰节气图片素材")
    print("=" * 50)
    
    successful_downloads = 0
    
    for i, (url, desc) in enumerate(zip(image_urls, image_descriptions), 1):
        # 确定文件扩展名
        if '.webp' in url.lower():
            ext = '.webp'
        elif '.png' in url.lower():
            ext = '.png'
        else:
            ext = '.jpg'
        
        filename = IMAGE_DIR / f"{desc}{ext}"
        
        if download_image(url, filename):
            successful_downloads += 1
        
        # 避免请求过快
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print(f"下载完成: {successful_downloads}/{len(image_urls)} 张图片")
    print("=" * 50)
    
    # 列出下载的图片
    print("\n下载的图片:")
    for img_file in IMAGE_DIR.glob("*"):
        file_size = img_file.stat().st_size
        print(f"  - {img_file.name} ({file_size} 字节)")
    
    # 创建图片使用说明
    create_usage_guide()

def create_usage_guide():
    """创建图片使用说明"""
    guide = """# 惊蛰节气图片使用说明

## 已下载的图片

### 1. jingzhe_spring_thunder.jpg
- **用途**: 春雷闪电动画背景
- **场景**: 视频开头0-3秒
- **内容**: 春雷惊醒万物

### 2. jingzhe_insects.jpg
- **用途**: 昆虫苏醒特写
- **场景**: 镜头1，配合"惊醒蛰伏于地下越冬的昆虫"
- **内容**: 土壤中昆虫爬出

### 3. jingzhe_spring_rain.jpg
- **用途**: 春雨滋润大地
- **场景**: 镜头2，配合"雨水增多，万物复苏"
- **内容**: 春雨场景

### 4. jingzhe_peach_blossom.jpg
- **用途**: 桃花李花绽放
- **场景**: 镜头2-3，配合"桃花红、李花白"
- **内容**: 春季花朵

### 5. jingzhe_farming.jpg
- **用途**: 农民春耕
- **场景**: 镜头3，配合"农民开始春耕"
- **内容**: 春耕场景

## 图片处理建议

### 1. 尺寸调整
所有图片应调整为小红书竖屏比例 3:4 (1080×1440)

```bash
# 使用ImageMagick调整尺寸
mogrify -resize 1080x1440^ -gravity center -extent 1080x1440 images/*.jpg
```

### 2. 添加文字
为每张图片添加相应的文字说明：
- 使用白色字体，黑色描边
- 字体大小适中，不影响画面主体
- 位置：底部或顶部安全区域

### 3. 转场效果
建议使用淡入淡出效果：
- 每张图片显示3-4秒
- 转场时间0.5秒
- 配合音频节奏

## 版权注意事项
1. 这些图片来自网络搜索，请确认版权状态
2. 建议最终使用前替换为有明确授权的图片
3. 可考虑使用免费图库如Pexels、Pixabay的替代图片

## 备用图片关键词
如果图片不合适，可搜索以下关键词：
- "spring thunder china"
- "insects waking up soil"
- "spring rain landscape"
- "peach blossom china"
- "traditional chinese farming"
"""
    
    guide_file = IMAGE_DIR / "USAGE_GUIDE.md"
    guide_file.write_text(guide)
    print(f"\n使用说明已保存: {guide_file}")

if __name__ == "__main__":
    main()