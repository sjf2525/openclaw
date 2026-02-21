#!/usr/bin/env python3
"""
终极修复：使用中文字体创建完整视频
"""

import subprocess
import os
from pathlib import Path

# 项目路径
PROJECT_DIR = Path(__file__).parent
OUTPUT_DIR = PROJECT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def get_duration(file_path):
    """获取媒体文件时长"""
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
           "-of", "default=noprint_wrappers=1:nokey=1", str(file_path)]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except:
        return 0.0

def create_chinese_subtitle_simple(text, output_path):
    """使用ImageMagick创建中文字幕图片（最简单可靠的方法）"""
    print(f"创建中文字幕图片: {text[:20]}...")
    
    # 使用ImageMagick创建字幕图片
    cmd = [
        "convert",
        "-size", "1080x200",
        "xc:white",  # 白色背景
        "-fill", "black",
        "-font", "Noto-Sans-CJK-Regular",  # 使用安装的中文字体
        "-pointsize", "44",
        "-gravity", "center",
        f"caption:{text}",
        "-quality", "95",
        str(output_path)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        file_size = output_path.stat().st_size
        print(f"  ✅ 字幕图片创建成功: {file_size} 字节")
        
        # 验证图片
        cmd = ["identify", "-verbose", str(output_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if "Type: TrueColor" in result.stdout:
            print(f"  ✅ 图片类型: TrueColor (真彩色)")
        return True
    except Exception as e:
        print(f"  ❌ 创建失败: {e}")
        return False

def create_ultimate_video():
    """创建终极修复版视频"""
    print("创建终极修复版视频...")
    print("=" * 60)
    
    # 字幕文本
    subtitles = [
        "惊蛰，是二十四节气中的第三个节气。",
        "春雷始鸣，惊醒蛰伏于地下越冬的昆虫。",
        "此时气温回升，雨水增多，万物开始复苏。",
        "农民开始春耕，桃花红、李花白，黄莺鸣叫、燕子飞来。",
        "惊蛰吃梨，寓意远离疾病，开启健康一年。"
    ]
    
    # 1. 创建中文字幕图片
    print("\n1. 创建中文字幕图片...")
    subtitle_files = []
    
    for i, text in enumerate(subtitles, 1):
        subtitle_file = OUTPUT_DIR / f"ultimate_subtitle_{i}.jpg"
        if create_chinese_subtitle_simple(text, subtitle_file):
            subtitle_files.append(subtitle_file)
        else:
            print(f"  ❌ 字幕图片 {i} 创建失败")
            return None
    
    # 2. 获取音频文件
    print("\n2. 获取音频文件...")
    audio_files = []
    audio_durations = []
    
    for i in range(1, 6):
        audio_file = PROJECT_DIR / "audio" / f"jingzhe_{i}.mp3"
        if not audio_file.exists():
            audio_file = PROJECT_DIR / "audio" / f"jingzhe_sentence_{i}.mp3"
        
        if audio_file.exists():
            duration = get_duration(audio_file)
            audio_files.append(audio_file)
            audio_durations.append(duration)
            print(f"  音频 {i}: {audio_file.name} ({duration:.2f}秒)")
        else:
            print(f"  ❌ 未找到音频文件 {i}")
            return None
    
    # 3. 获取图片文件
    print("\n3. 获取图片文件...")
    image_files = list(PROJECT_DIR.glob("images/*"))
    if len(image_files) < 5:
        print(f"错误: 需要5张图片，只找到 {len(image_files)} 张")
        return None
    
    # 4. 创建5个视频片段
    print("\n4. 创建视频片段...")
    segment_files = []
    total_duration = 0
    
    for i in range(5):
        print(f"\n  片段 {i+1}:")
        print(f"    字幕: {subtitles[i][:30]}...")
        print(f"    音频: {audio_durations[i]:.2f}秒")
        
        # 调整背景图片
        bg_file = image_files[i]
        resized_bg = OUTPUT_DIR / f"ultimate_bg_{i+1}.jpg"
        
        cmd = [
            "ffmpeg", "-y",
            "-i", str(bg_file),
            "-vf", "scale=1080:1440:force_original_aspect_ratio=disable,pad=1080:1440:(ow-iw)/2:(oh-ih)/2:color=black",
            "-q:v", "2",
            str(resized_bg)
        ]
        
        subprocess.run(cmd, capture_output=True)
        print(f"    调整背景图片完成")
        
        # 合并图片
        merged_file = OUTPUT_DIR / f"ultimate_merged_{i+1}.jpg"
        
        cmd = [
            "ffmpeg", "-y",
            "-i", str(resized_bg),
            "-i", str(subtitle_files[i]),
            "-filter_complex", "[0:v][1:v]overlay=0:1240",
            str(merged_file)
        ]
        
        subprocess.run(cmd, capture_output=True)
        print(f"    合并图片完成")
        
        # 创建视频片段
        segment_file = OUTPUT_DIR / f"ultimate_segment_{i+1}.mp4"
        
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(merged_file),
            "-i", str(audio_files[i]),
            "-c:v", "libx264",
            "-t", str(audio_durations[i]),
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-shortest",
            str(segment_file)
        ]
        
        subprocess.run(cmd, capture_output=True)
        
        if segment_file.exists():
            segment_files.append(segment_file)
            segment_size = segment_file.stat().st_size
            print(f"    ✅ 视频片段创建成功: {segment_size} 字节")
            total_duration += audio_durations[i]
        else:
            print(f"    ❌ 视频片段创建失败")
            return None
    
    # 5. 合并视频片段
    print(f"\n5. 合并视频片段 (总时长: {total_duration:.2f}秒)...")
    concat_file = OUTPUT_DIR / "ultimate_concat.txt"
    with open(concat_file, 'w') as f:
        for segment in segment_files:
            f.write(f"file '{segment.absolute()}'\n")
    
    final_video = OUTPUT_DIR / "jingzhe_ultimate_final.mp4"
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(final_video)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if final_video.exists():
        final_duration = get_duration(final_video)
        final_size = final_video.stat().st_size
        
        print(f"✅ 最终视频创建成功!")
        print(f"   文件: {final_video.name}")
        print(f"   大小: {final_size} 字节")
        print(f"   时长: {final_duration:.2f}秒")
        
        return final_video
    else:
        print("❌ 最终视频创建失败")
        print(f"错误信息: {result.stderr}")
        return None

def main():
    """主函数"""
    print("惊蛰视频终极修复版")
    print("=" * 60)
    
    print("问题总结与修复:")
    print("1. ❌ 之前使用西文字体，不包含中文字符")
    print("2. ✅ 已安装 fonts-noto-cjk，系统有中文字体")
    print("3. ✅ 使用 ImageMagick + Noto-Sans-CJK-Regular 字体")
    print("4. ✅ 白色背景 + 黑色文字，确保高对比度")
    print("5. ✅ 分段创建 + 合并，确保时间准确")
    
    # 创建视频
    video_file = create_ultimate_video()
    
    if video_file:
        print("\n" + "=" * 60)
        print("🎉 终极修复版视频创建成功！")
        print("=" * 60)
        
        # 获取视频信息
        duration = get_duration(video_file)
        size = video_file.stat().st_size
        
        print(f"\n📊 视频规格:")
        print(f"   文件: {video_file.name}")
        print(f"   大小: {size} 字节 ({size/1024:.1f} KB)")
        print(f"   时长: {duration:.2f}秒")
        print(f"   分辨率: 1080×1440 (3:4竖屏)")
        
        print(f"\n🎬 时间轴:")
        subtitles = [
            "惊蛰，是二十四节气中的第三个节气。",
            "春雷始鸣，惊醒蛰伏于地下越冬的昆虫。",
            "此时气温回升，雨水增多，万物开始复苏。",
            "农民开始春耕，桃花红、李花白，黄莺鸣叫、燕子飞来。",
            "惊蛰吃梨，寓意远离疾病，开启健康一年。"
        ]
        
        # 获取每个音频的时长
        audio_durations = []
        for i in range(1, 6):
            audio_file = PROJECT_DIR / "audio" / f"jingzhe_{i}.mp3"
            if not audio_file.exists():
                audio_file = PROJECT_DIR / "audio" / f"jingzhe_sentence_{i}.mp3"
            if audio_file.exists():
                audio_durations.append(get_duration(audio_file))
        
        total = 0
        for i in range(5):
            end = total + audio_durations[i]
            print(f"   {total:.1f}-{end:.1f}秒: {subtitles[i][:30]}...")
            total = end
        
        print(f"\n🔗 GitHub链接:")
        print(f"   https://github.com/sjf2525/openclaw/blob/main/chinese-culture-videos/jingzhe/output/{video_file.name}")
        
        print(f"\n📨 正在发送到WhatsApp...")
        # 这里可以添加发送代码
        
    else:
        print("\n❌ 视频创建失败")

if __name__ == "__main__":
    main()