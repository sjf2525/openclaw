#!/usr/bin/env python3
"""
测试字幕问题 - 快速验证脚本
"""

import subprocess
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# 项目路径
PROJECT_DIR = Path(__file__).parent
OUTPUT_DIR = PROJECT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def test_pil_subtitle():
    """测试PIL创建字幕图片"""
    print("测试PIL创建字幕图片...")
    
    text = "测试字幕：惊蛰节气"
    output_file = OUTPUT_DIR / "test_pil_subtitle.png"
    
    # 创建图片
    width, height = 1080, 200
    image = Image.new('RGBA', (width, height), (0, 0, 0, 180))
    draw = ImageDraw.Draw(image)
    
    # 尝试加载字体
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    
    font = None
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, 40)
                print(f"使用字体: {os.path.basename(font_path)}")
                break
            except:
                continue
    
    if font is None:
        font = ImageFont.load_default()
        print("使用默认字体")
    
    # 绘制文本
    x, y = 100, 80
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    
    # 保存图片
    image.save(output_file, 'PNG')
    
    # 验证图片
    file_size = output_file.stat().st_size
    print(f"字幕图片创建成功: {output_file.name}")
    print(f"文件大小: {file_size} 字节")
    
    # 检查图片内容
    cmd = ["identify", "-verbose", str(output_file)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("\n图片信息:")
    for line in result.stdout.split('\n')[:10]:
        if line.strip():
            print(f"  {line}")
    
    return output_file

def test_image_merge():
    """测试图片合并"""
    print("\n测试图片合并...")
    
    # 使用现有的背景图片
    bg_files = list(PROJECT_DIR.glob("images/*"))
    if not bg_files:
        print("错误: 没有背景图片")
        return None
    
    bg_file = bg_files[0]
    
    # 调整背景图片尺寸
    resized_bg = OUTPUT_DIR / "test_bg.jpg"
    cmd = [
        "ffmpeg", "-y",
        "-i", str(bg_file),
        "-vf", "scale=1080:1440:force_original_aspect_ratio=disable,pad=1080:1440:(ow-iw)/2:(oh-ih)/2:color=black",
        "-q:v", "2",
        str(resized_bg)
    ]
    
    subprocess.run(cmd, capture_output=True)
    print(f"调整背景图片: {resized_bg.name}")
    
    # 创建测试字幕图片
    subtitle_file = test_pil_subtitle()
    if not subtitle_file:
        return None
    
    # 合并图片
    merged_file = OUTPUT_DIR / "test_merged.jpg"
    cmd = [
        "ffmpeg", "-y",
        "-i", str(resized_bg),
        "-i", str(subtitle_file),
        "-filter_complex", "[0:v][1:v]overlay=0:1240",
        str(merged_file)
    ]
    
    subprocess.run(cmd, capture_output=True)
    print(f"合并图片: {merged_file.name}")
    
    # 检查合并后的图片
    file_size = merged_file.stat().st_size
    print(f"合并图片大小: {file_size} 字节")
    
    return merged_file

def test_video_creation():
    """测试视频创建"""
    print("\n测试视频创建...")
    
    # 使用现有的音频文件
    audio_files = list(PROJECT_DIR.glob("audio/*.mp3"))
    if not audio_files:
        print("错误: 没有音频文件")
        return None
    
    audio_file = audio_files[0]
    
    # 创建测试图片
    merged_file = test_image_merge()
    if not merged_file:
        return None
    
    # 创建视频
    video_file = OUTPUT_DIR / "test_video.mp4"
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
        str(video_file)
    ]
    
    subprocess.run(cmd, capture_output=True)
    print(f"创建测试视频: {video_file.name}")
    
    # 检查视频
    file_size = video_file.stat().st_size
    print(f"测试视频大小: {file_size} 字节")
    
    return video_file

def check_system_fonts():
    """检查系统字体"""
    print("\n检查系统字体...")
    
    font_dirs = [
        "/usr/share/fonts/truetype/",
        "/usr/share/fonts/opentype/",
    ]
    
    for font_dir in font_dirs:
        if os.path.exists(font_dir):
            print(f"字体目录: {font_dir}")
            cmd = ["find", font_dir, "-name", "*.ttf", "-o", "-name", "*.ttc", "-o", "-name", "*.otf"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            fonts = result.stdout.strip().split('\n')
            for font in fonts[:5]:  # 只显示前5个
                if font:
                    print(f"  {os.path.basename(font)}")

def main():
    """主函数"""
    print("字幕问题测试脚本")
    print("=" * 60)
    
    print("测试步骤:")
    print("1. 检查系统字体")
    print("2. 测试PIL创建字幕图片")
    print("3. 测试图片合并")
    print("4. 测试视频创建")
    
    check_system_fonts()
    test_video_creation()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
    
    print("\n请检查以下文件:")
    print("1. test_pil_subtitle.png - PIL创建的字幕图片")
    print("2. test_merged.jpg - 合并后的图片")
    print("3. test_video.mp4 - 测试视频")
    
    print("\n如果字幕显示为白色框框，可能的原因:")
    print("1. PIL无法正确渲染中文字体")
    print("2. 字幕图片透明度问题")
    print("3. 图片合并时字幕位置错误")
    print("4. 字幕图片文件为空或损坏")

if __name__ == "__main__":
    main()