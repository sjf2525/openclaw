#!/usr/bin/env python3
"""
创建惊蛰节气视频
使用FFmpeg合成图片和音频
"""

import os
import subprocess
from pathlib import Path

# 项目路径
PROJECT_DIR = Path(__file__).parent
IMAGE_DIR = PROJECT_DIR / "images"
AUDIO_DIR = PROJECT_DIR / "audio"
OUTPUT_DIR = PROJECT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def check_dependencies():
    """检查依赖"""
    print("检查依赖...")
    
    # 检查FFmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✅ FFmpeg 已安装")
    except:
        print("❌ FFmpeg 未安装")
        return False
    
    return True

def resize_images():
    """调整图片尺寸为小红书竖屏比例 1080×1440"""
    print("\n调整图片尺寸...")
    
    # 目标尺寸
    target_width = 1080
    target_height = 1440
    
    resized_images = []
    
    for img_file in IMAGE_DIR.glob("*"):
        if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
            output_file = OUTPUT_DIR / f"resized_{img_file.stem}.jpg"
            
            print(f"调整: {img_file.name} -> {output_file.name}")
            
            # 使用FFmpeg调整尺寸并填充为3:4
            cmd = [
                "ffmpeg", "-y",
                "-i", str(img_file),
                "-vf", f"scale={target_width}:{target_height}:force_original_aspect_ratio=disable,"
                       f"pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2:color=black",
                "-q:v", "2",  # 高质量
                str(output_file)
            ]
            
            try:
                subprocess.run(cmd, capture_output=True, check=True)
                resized_images.append(output_file)
                print(f"  成功")
            except Exception as e:
                print(f"  失败: {e}")
    
    return resized_images

def create_video_from_images(images, audio_file, output_video):
    """从图片创建视频"""
    print(f"\n创建视频: {output_video}")
    
    if not images:
        print("错误: 没有可用的图片")
        return False
    
    if not audio_file.exists():
        print(f"错误: 音频文件不存在: {audio_file}")
        return False
    
    # 创建图片列表文件
    concat_file = OUTPUT_DIR / "concat_list.txt"
    with open(concat_file, 'w') as f:
        for img in images:
            # 每张图片显示3-4秒
            f.write(f"file '{img.absolute()}'\n")
            f.write(f"duration 3.5\n")
    
    # 使用FFmpeg创建视频
    # 先创建无声视频
    temp_video = OUTPUT_DIR / "temp_video.mp4"
    
    cmd1 = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-vf", "fps=30",
        "-r", "30",
        str(temp_video)
    ]
    
    print("步骤1: 创建无声视频...")
    try:
        subprocess.run(cmd1, capture_output=True, check=True)
        print("  成功")
    except Exception as e:
        print(f"  失败: {e}")
        return False
    
    # 合并音频
    cmd2 = [
        "ffmpeg", "-y",
        "-i", str(temp_video),
        "-i", str(audio_file),
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(output_video)
    ]
    
    print("步骤2: 添加音频...")
    try:
        subprocess.run(cmd2, capture_output=True, check=True)
        print("  成功")
        
        # 清理临时文件
        temp_video.unlink(missing_ok=True)
        concat_file.unlink(missing_ok=True)
        
        return True
    except Exception as e:
        print(f"  失败: {e}")
        return False

def add_subtitles(video_file, subtitle_file, output_file):
    """添加字幕到视频"""
    print(f"\n添加字幕到视频...")
    
    if not video_file.exists():
        print(f"错误: 视频文件不存在: {video_file}")
        return False
    
    if not subtitle_file.exists():
        print(f"错误: 字幕文件不存在: {subtitle_file}")
        return False
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_file),
        "-vf", f"ass={subtitle_file}",
        "-c:a", "copy",
        str(output_file)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"✅ 字幕添加成功: {output_file}")
        return True
    except Exception as e:
        print(f"❌ 字幕添加失败: {e}")
        return False

def create_simple_video():
    """创建简单版本视频（如果完整版本失败）"""
    print("\n创建简单版本视频...")
    
    # 使用第一张图片和完整音频
    images = list(IMAGE_DIR.glob("*"))
    if not images:
        print("错误: 没有可用的图片")
        return False
    
    first_image = images[0]
    audio_file = AUDIO_DIR / "jingzhe_full_new.mp3"
    
    if not audio_file.exists():
        print(f"错误: 音频文件不存在: {audio_file}")
        return False
    
    output_video = OUTPUT_DIR / "jingzhe_simple.mp4"
    
    # 获取音频时长
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
           "-of", "default=noprint_wrappers=1:nokey=1", str(audio_file)]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())
        print(f"音频时长: {duration:.2f}秒")
    except:
        duration = 15.0  # 默认15秒
    
    # 创建视频
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(first_image),
        "-i", str(audio_file),
        "-c:v", "libx264",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        "-vf", "scale=1080:1440:force_original_aspect_ratio=disable,"
               "pad=1080:1440:(ow-iw)/2:(oh-ih)/2:color=black",
        "-c:a", "aac",
        "-shortest",
        str(output_video)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"✅ 简单视频创建成功: {output_video}")
        return output_video
    except Exception as e:
        print(f"❌ 简单视频创建失败: {e}")
        return None

def main():
    """主函数"""
    print("=" * 50)
    print("创建惊蛰节气视频")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 调整图片尺寸
    resized_images = resize_images()
    
    # 音频文件
    audio_file = AUDIO_DIR / "jingzhe_full_new.mp3"
    
    if not audio_file.exists():
        print(f"\n错误: 未找到合并的音频文件: {audio_file}")
        print("请先运行音频合并脚本")
        return
    
    # 创建视频
    output_video = OUTPUT_DIR / "jingzhe_video.mp4"
    
    if resized_images:
        print(f"\n使用 {len(resized_images)} 张图片创建视频...")
        success = create_video_from_images(resized_images, audio_file, output_video)
        
        if not success:
            print("\n完整视频创建失败，尝试创建简单版本...")
            output_video = create_simple_video()
    else:
        print("\n没有可用的图片，创建简单版本...")
        output_video = create_simple_video()
    
    if output_video and output_video.exists():
        print(f"\n✅ 视频创建成功: {output_video}")
        
        # 添加字幕
        subtitle_file = OUTPUT_DIR / "jingzhe_subtitles.ass"
        if subtitle_file.exists():
            final_video = OUTPUT_DIR / "jingzhe_video_with_subtitles.mp4"
            add_subtitles(output_video, subtitle_file, final_video)
        
        print("\n" + "=" * 50)
        print("视频制作完成！")
        print("=" * 50)
        
        print("\n生成的文件:")
        for file in OUTPUT_DIR.glob("*"):
            if file.is_file():
                size = file.stat().st_size
                print(f"  - {file.name} ({size} 字节)")
        
        print(f"\n主视频文件: {output_video}")
        print(f"视频规格: 1080×1440 (3:4竖屏), 适合小红书")
        print(f"时长: 约15-18秒")
        
    else:
        print("\n❌ 视频创建失败")

if __name__ == "__main__":
    main()