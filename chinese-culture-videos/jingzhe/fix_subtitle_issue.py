#!/usr/bin/env python3
"""
修复字幕问题 - 确保创建彩色字幕图片
"""

import subprocess
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import textwrap

# 项目路径
PROJECT_DIR = Path(__file__).parent
OUTPUT_DIR = PROJECT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def create_color_subtitle(text, output_path, font_size=48):
    """创建彩色字幕图片（修复版本）"""
    print(f"创建彩色字幕图片: {text[:20]}...")
    
    # 图片尺寸
    width, height = 1080, 200
    
    try:
        # 创建彩色图片（RGBA模式）
        image = Image.new('RGBA', (width, height), (0, 0, 0, 180))  # 黑色半透明背景
        draw = ImageDraw.Draw(image)
        
        # 加载字体
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]
        
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    print(f"  使用字体: {os.path.basename(font_path)}")
                    break
                except:
                    continue
        
        if font is None:
            font = ImageFont.load_default()
            print("  使用默认字体")
        
        # 文本换行
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
                text_width = len(line) * (font_size // 2)
            
            x = (width - text_width) // 2
            y = y_start + i * line_height
            
            # 绘制文本阴影（黑色）
            draw.text((x+2, y+2), line, font=font, fill=(0, 0, 0, 255))
            # 绘制文本（白色）
            draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        
        # 保存为PNG
        image.save(output_path, 'PNG')
        
        # 验证图片
        verify_image(output_path)
        return True
        
    except Exception as e:
        print(f"  ❌ 创建失败: {e}")
        return False

def verify_image(image_path):
    """验证图片"""
    print(f"  验证图片: {image_path.name}")
    
    file_size = image_path.stat().st_size
    print(f"    文件大小: {file_size} 字节")
    
    # 使用ImageMagick检查
    cmd = ["identify", "-verbose", str(image_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # 检查是否为彩色图
    if "Type: TrueColorAlpha" in result.stdout:
        print(f"    ✅ 图片类型: TrueColorAlpha (真彩色带透明度)")
    elif "Type: GrayscaleAlpha" in result.stdout:
        print(f"    ⚠️  图片类型: GrayscaleAlpha (灰度带透明度)")
    else:
        print(f"    ⚠️  图片类型: 未知")
    
    # 检查平均像素值
    cmd = ["convert", str(image_path), "-format", "%[fx:mean]", "info:"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout.strip():
        mean_value = float(result.stdout.strip())
        print(f"    平均像素值: {mean_value:.3f}")
        if mean_value < 0.1:
            print(f"    ⚠️  图片非常暗")
        elif mean_value > 0.9:
            print(f"    ⚠️  图片非常亮")
        else:
            print(f"    ✅ 图片亮度正常")

def create_simple_color_subtitle(text, output_path):
    """创建简单的彩色字幕图片（备用方案）"""
    print(f"创建简单彩色字幕图片: {text[:20]}...")
    
    # 使用ImageMagick创建彩色字幕图片
    cmd = [
        "convert",
        "-size", "1080x200",
        "xc:'rgba(0,0,0,0.7)'",  # 黑色70%透明度
        "-fill", "white",
        "-font", "DejaVu-Sans",
        "-pointsize", "44",
        "-gravity", "center",
        f"caption:{text}",
        "-colorspace", "sRGB",  # 确保为彩色图
        str(output_path)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"  ✅ 简单彩色字幕图片创建成功")
        verify_image(output_path)
        return True
    except Exception as e:
        print(f"  ❌ 创建失败: {e}")
        return False

def create_final_video():
    """创建最终视频（使用修复后的字幕）"""
    print("\n创建最终视频...")
    
    # 字幕文本
    subtitles = [
        "惊蛰，是二十四节气中的第三个节气。",
        "春雷始鸣，惊醒蛰伏于地下越冬的昆虫。",
        "此时气温回升，雨水增多，万物开始复苏。",
        "农民开始春耕，桃花红、李花白，黄莺鸣叫、燕子飞来。",
        "惊蛰吃梨，寓意远离疾病，开启健康一年。"
    ]
    
    # 1. 创建彩色字幕图片
    print("1. 创建彩色字幕图片...")
    subtitle_files = []
    
    for i, text in enumerate(subtitles, 1):
        subtitle_file = OUTPUT_DIR / f"color_subtitle_{i}.png"
        
        # 尝试方法1
        if not create_color_subtitle(text, subtitle_file):
            # 尝试方法2
            print(f"  方法1失败，尝试方法2...")
            if not create_simple_color_subtitle(text, subtitle_file):
                print(f"  ❌ 所有方法都失败")
                return None
        
        subtitle_files.append(subtitle_file)
    
    # 2. 使用第一张背景图片
    print("\n2. 准备背景图片...")
    image_files = list(PROJECT_DIR.glob("images/*"))
    if not image_files:
        print("错误: 没有背景图片")
        return None
    
    bg_file = image_files[0]
    resized_bg = OUTPUT_DIR / "color_bg.jpg"
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(bg_file),
        "-vf", "scale=1080:1440:force_original_aspect_ratio=disable,pad=1080:1440:(ow-iw)/2:(oh-ih)/2:color=black",
        "-q:v", "2",
        str(resized_bg)
    ]
    
    subprocess.run(cmd, capture_output=True)
    print(f"  调整背景图片: {resized_bg.name}")
    
    # 3. 合并图片（只使用第一张字幕图片测试）
    print("\n3. 合并图片...")
    merged_file = OUTPUT_DIR / "color_merged.jpg"
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(resized_bg),
        "-i", str(subtitle_files[0]),
        "-filter_complex", "[0:v][1:v]overlay=0:1240",
        str(merged_file)
    ]
    
    subprocess.run(cmd, capture_output=True)
    print(f"  合并图片: {merged_file.name}")
    
    # 4. 创建测试视频
    print("\n4. 创建测试视频...")
    
    # 使用第一个音频文件
    audio_files = list(PROJECT_DIR.glob("audio/*.mp3"))
    if not audio_files:
        print("错误: 没有音频文件")
        return None
    
    audio_file = audio_files[0]
    test_video = OUTPUT_DIR / "color_test_video.mp4"
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(merged_file),
        "-i", str(audio_file),
        "-c:v", "libx264",
        "-t", "5",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        str(test_video)
    ]
    
    subprocess.run(cmd, capture_output=True)
    print(f"  创建测试视频: {test_video.name}")
    
    # 验证视频
    file_size = test_video.stat().st_size
    print(f"  测试视频大小: {file_size} 字节")
    
    return test_video

def main():
    """主函数"""
    print("修复字幕问题脚本")
    print("=" * 60)
    
    print("问题分析:")
    print("1. 之前的字幕图片是 GrayscaleAlpha (灰度带透明度)")
    print("2. 平均像素值很低，图片非常暗")
    print("3. 可能导致字幕显示为白色框框或无显示")
    print("\n解决方案:")
    print("1. 确保创建 TrueColorAlpha (真彩色带透明度) 图片")
    print("2. 使用白色文字，确保足够的对比度")
    print("3. 验证图片类型和亮度")
    
    # 创建测试视频
    video_file = create_final_video()
    
    if video_file:
        print("\n" + "=" * 60)
        print("✅ 测试视频创建成功！")
        print("=" * 60)
        
        print(f"\n测试视频: {video_file}")
        print(f"文件大小: {video_file.stat().st_size} 字节")
        
        print("\n请检查以下文件:")
        print("1. color_subtitle_1.png - 彩色字幕图片")
        print("2. color_merged.jpg - 合并后的图片")
        print("3. color_test_video.mp4 - 测试视频")
        
        print("\nGitHub链接:")
        print(f"https://github.com/sjf2525/openclaw/blob/main/chinese-culture-videos/jingzhe/output/{video_file.name}")
    else:
        print("\n❌ 测试视频创建失败")

if __name__ == "__main__":
    main()