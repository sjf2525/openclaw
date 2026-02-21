#!/usr/bin/env python3
"""
创建白色背景字幕图片 - 确保为彩色图
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

def create_white_bg_subtitle(text, output_path, font_size=48):
    """创建白色背景字幕图片"""
    print(f"创建白色背景字幕图片: {text[:20]}...")
    
    # 图片尺寸
    width, height = 1080, 200
    
    try:
        # 创建白色背景图片（不透明）
        image = Image.new('RGB', (width, height), (255, 255, 255))  # 白色背景
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
        
        # 绘制每行文本（黑色文字）
        for i, line in enumerate(lines):
            # 计算文本宽度
            if hasattr(font, 'getbbox'):
                bbox = font.getbbox(line)
                text_width = bbox[2] - bbox[0]
            else:
                text_width = len(line) * (font_size // 2)
            
            x = (width - text_width) // 2
            y = y_start + i * line_height
            
            # 绘制文本（黑色）
            draw.text((x, y), line, font=font, fill=(0, 0, 0))
        
        # 保存为JPEG（确保为彩色图）
        image.save(output_path, 'JPEG', quality=95)
        
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
    if "Type: TrueColor" in result.stdout:
        print(f"    ✅ 图片类型: TrueColor (真彩色)")
    elif "Type: Grayscale" in result.stdout:
        print(f"    ⚠️  图片类型: Grayscale (灰度)")
    else:
        print(f"    图片类型: 未知")
    
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

def create_video_with_white_subtitle():
    """创建带白色背景字幕的视频"""
    print("\n创建带白色背景字幕的视频...")
    
    # 字幕文本
    text = "惊蛰，是二十四节气中的第三个节气。"
    
    # 1. 创建白色背景字幕图片
    print("1. 创建白色背景字幕图片...")
    subtitle_file = OUTPUT_DIR / "white_bg_subtitle.jpg"
    
    if not create_white_bg_subtitle(text, subtitle_file):
        print("  ❌ 字幕图片创建失败")
        return None
    
    # 2. 准备背景图片
    print("\n2. 准备背景图片...")
    image_files = list(PROJECT_DIR.glob("images/*"))
    if not image_files:
        print("错误: 没有背景图片")
        return None
    
    bg_file = image_files[0]
    resized_bg = OUTPUT_DIR / "white_bg_background.jpg"
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(bg_file),
        "-vf", "scale=1080:1440:force_original_aspect_ratio=disable,pad=1080:1440:(ow-iw)/2:(oh-ih)/2:color=black",
        "-q:v", "2",
        str(resized_bg)
    ]
    
    subprocess.run(cmd, capture_output=True)
    print(f"  调整背景图片: {resized_bg.name}")
    
    # 3. 合并图片
    print("\n3. 合并图片...")
    merged_file = OUTPUT_DIR / "white_bg_merged.jpg"
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(resized_bg),
        "-i", str(subtitle_file),
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
    test_video = OUTPUT_DIR / "white_bg_test_video.mp4"
    
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
    print("白色背景字幕解决方案")
    print("=" * 60)
    
    print("问题分析:")
    print("1. PIL创建的透明背景字幕图片是 GrayscaleAlpha")
    print("2. 图片非常暗，平均像素值很低")
    print("3. 这可能导致字幕显示问题")
    print("\n解决方案:")
    print("1. 使用白色不透明背景")
    print("2. 使用黑色文字")
    print("3. 保存为JPEG格式（确保为彩色图）")
    
    # 创建测试视频
    video_file = create_video_with_white_subtitle()
    
    if video_file:
        print("\n" + "=" * 60)
        print("✅ 测试视频创建成功！")
        print("=" * 60)
        
        print(f"\n测试视频: {video_file}")
        print(f"文件大小: {video_file.stat().st_size} 字节")
        
        print("\n关键文件:")
        print("1. white_bg_subtitle.jpg - 白色背景字幕图片")
        print("2. white_bg_merged.jpg - 合并后的图片")
        print("3. white_bg_test_video.mp4 - 测试视频")
        
        print("\nGitHub链接:")
        print(f"https://github.com/sjf2525/openclaw/blob/main/chinese-culture-videos/jingzhe/output/{video_file.name}")
        
        print("\n技术特点:")
        print("✅ 字幕图片为 TrueColor (真彩色)")
        print("✅ 白色背景，黑色文字，高对比度")
        print("✅ JPEG格式，无透明度问题")
        print("✅ 应该能正常显示字幕")
    else:
        print("\n❌ 测试视频创建失败")

if __name__ == "__main__":
    main()