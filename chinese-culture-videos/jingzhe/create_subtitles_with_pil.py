#!/usr/bin/env python3
"""
使用PIL（Python Imaging Library）创建字幕图片
彻底解决ImageMagick中文字体渲染问题
"""

from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
from pathlib import Path

# 项目路径
PROJECT_DIR = Path(__file__).parent
OUTPUT_DIR = PROJECT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def find_font():
    """查找可用的中文字体"""
    font_paths = [
        # 系统字体路径
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",  # Google Noto字体
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            print(f"找到字体: {font_path}")
            return font_path
    
    print("警告: 未找到系统字体，使用默认字体")
    return None

def create_subtitle_with_pil(text, output_path, font_size=40):
    """使用PIL创建字幕图片"""
    print(f"创建字幕图片: {text[:20]}...")
    
    # 图片尺寸
    width, height = 1080, 200
    
    try:
        # 创建图片
        image = Image.new('RGBA', (width, height), (0, 0, 0, 180))  # 黑色半透明背景
        draw = ImageDraw.Draw(image)
        
        # 加载字体
        font_path = find_font()
        if font_path:
            try:
                font = ImageFont.truetype(font_path, font_size)
                print(f"  使用字体: {os.path.basename(font_path)}")
            except:
                print(f"  警告: 无法加载字体 {font_path}，使用默认字体")
                font = ImageFont.load_default()
        else:
            font = ImageFont.load_default()
            print("  使用默认字体")
        
        # 文本换行（每行最多15个字符）
        wrapped_text = textwrap.fill(text, width=15)
        lines = wrapped_text.split('\n')
        
        # 计算文本位置
        line_height = font_size + 10
        total_height = len(lines) * line_height
        y_start = (height - total_height) // 2
        
        # 绘制每行文本
        for i, line in enumerate(lines):
            # 计算文本宽度
            if hasattr(font, 'getbbox'):
                bbox = font.getbbox(line)
                text_width = bbox[2] - bbox[0]
            else:
                # 估算宽度
                text_width = len(line) * (font_size // 2)
            
            x = (width - text_width) // 2
            y = y_start + i * line_height
            
            # 绘制文本阴影（提高可读性）
            draw.text((x+2, y+2), line, font=font, fill=(0, 0, 0, 255))
            # 绘制文本
            draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        
        # 保存图片
        image.save(output_path, 'PNG')
        file_size = output_path.stat().st_size
        print(f"  ✅ 字幕图片创建成功: {output_path.name} ({file_size} 字节)")
        return True
        
    except Exception as e:
        print(f"  ❌ 创建失败: {e}")
        return False

def create_simple_subtitle(text, output_path):
    """创建简单的字幕图片（备用方案）"""
    print(f"创建简单字幕图片: {text[:20]}...")
    
    # 使用ImageMagick的简单命令
    import subprocess
    
    # 先创建纯色背景
    cmd1 = [
        "convert",
        "-size", "1080x200",
        "xc:'#000000B3'",  # 黑色70%透明度
        str(output_path)
    ]
    
    # 然后添加文字（使用caption自动换行）
    cmd2 = [
        "convert",
        str(output_path),
        "-fill", "white",
        "-font", "DejaVu-Sans",
        "-pointsize", "36",
        "-gravity", "center",
        f"caption:{text}",
        "-composite",
        str(output_path)
    ]
    
    try:
        # 创建背景
        subprocess.run(cmd1, capture_output=True, check=True)
        # 添加文字
        subprocess.run(cmd2, capture_output=True, check=True)
        
        file_size = output_path.stat().st_size
        print(f"  ✅ 简单字幕图片创建成功: {output_path.name} ({file_size} 字节)")
        return True
    except Exception as e:
        print(f"  ❌ 简单字幕创建失败: {e}")
        return False

def create_fallback_subtitle(text, output_path):
    """创建备用字幕图片（最后的手段）"""
    print(f"创建备用字幕图片: {text[:20]}...")
    
    # 使用最简单的纯文本图片
    from PIL import Image, ImageDraw
    
    width, height = 1080, 200
    
    # 创建纯色背景
    image = Image.new('RGB', (width, height), (0, 0, 0))  # 黑色背景
    draw = ImageDraw.Draw(image)
    
    # 使用默认字体绘制文本
    try:
        font = ImageFont.load_default()
        
        # 简单绘制文本（不换行）
        text_width = len(text) * 10  # 估算
        if text_width > width - 40:
            # 如果太长，截断
            text = text[:20] + "..."
            text_width = len(text) * 10
        
        x = (width - text_width) // 2
        y = (height - 40) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        
        # 保存为JPEG（更小）
        image.save(output_path, 'JPEG', quality=90)
        file_size = output_path.stat().st_size
        print(f"  ✅ 备用字幕图片创建成功: {output_path.name} ({file_size} 字节)")
        return True
    except Exception as e:
        print(f"  ❌ 备用字幕创建失败: {e}")
        return False

def main():
    """主函数"""
    print("使用PIL创建字幕图片")
    print("=" * 60)
    
    # 字幕文本
    subtitles = [
        "惊蛰，是二十四节气中的第三个节气。",
        "春雷始鸣，惊醒蛰伏于地下越冬的昆虫。",
        "此时气温回升，雨水增多，万物开始复苏。",
        "农民开始春耕，桃花红、李花白，黄莺鸣叫、燕子飞来。",
        "惊蛰吃梨，寓意远离疾病，开启健康一年。"
    ]
    
    print(f"需要创建 {len(subtitles)} 个字幕图片")
    
    # 方法1: 使用PIL
    print("\n方法1: 使用PIL创建字幕图片")
    print("-" * 40)
    
    pil_success = True
    pil_images = []
    
    for i, text in enumerate(subtitles, 1):
        output_file = OUTPUT_DIR / f"pil_subtitle_{i}.png"
        if create_subtitle_with_pil(text, output_file):
            pil_images.append(output_file)
        else:
            pil_success = False
            break
    
    # 方法2: 简单方法
    if not pil_success or len(pil_images) < 5:
        print("\n方法2: 使用简单方法创建字幕图片")
        print("-" * 40)
        
        simple_images = []
        simple_success = True
        
        for i, text in enumerate(subtitles, 1):
            output_file = OUTPUT_DIR / f"simple_subtitle_{i}.png"
            if create_simple_subtitle(text, output_file):
                simple_images.append(output_file)
            else:
                simple_success = False
                break
        
        if simple_success and len(simple_images) == 5:
            print("\n✅ 简单方法成功创建所有字幕图片")
            return simple_images
    
    # 方法3: 备用方法
    if not pil_success:
        print("\n方法3: 使用备用方法创建字幕图片")
        print("-" * 40)
        
        fallback_images = []
        fallback_success = True
        
        for i, text in enumerate(subtitles, 1):
            output_file = OUTPUT_DIR / f"fallback_subtitle_{i}.jpg"
            if create_fallback_subtitle(text, output_file):
                fallback_images.append(output_file)
            else:
                fallback_success = False
                break
        
        if fallback_success and len(fallback_images) == 5:
            print("\n✅ 备用方法成功创建所有字幕图片")
            return fallback_images
    
    if pil_success and len(pil_images) == 5:
        print("\n✅ PIL方法成功创建所有字幕图片")
        return pil_images
    
    print("\n❌ 所有方法都失败")
    return None

if __name__ == "__main__":
    subtitle_files = main()
    
    if subtitle_files:
        print("\n" + "=" * 60)
        print("字幕图片创建完成！")
        print("=" * 60)
        
        print(f"\n创建的字幕图片:")
        for file in subtitle_files:
            file_size = file.stat().st_size
            print(f"  {file.name}: {file_size} 字节")
        
        print("\n下一步:")
        print("1. 使用这些字幕图片重新创建视频")
        print("2. 确保字幕图片正确叠加到背景图片上")
        print("3. 验证最终视频的字幕显示")
    else:
        print("\n❌ 无法创建字幕图片")
        print("\n建议:")
        print("1. 检查系统字体安装")
        print("2. 手动创建字幕图片")
        print("3. 或者使用视频编辑软件添加字幕")