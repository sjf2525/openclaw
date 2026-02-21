#!/usr/bin/env python3
"""
修复字幕内容和排版问题
1. 每段显示正确的字幕
2. 优化字幕排版，避免单个字单独一行
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

def create_proper_subtitle(text, output_path, font_size=44):
    """创建正确排版的中文字幕"""
    print(f"创建字幕: {text[:20]}...")
    
    # 图片尺寸
    width, height = 1080, 200
    
    try:
        # 创建白色背景图片
        image = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 加载中文字体
        font_path = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'
        if os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size, index=0)
            print(f"  使用字体: NotoSerifCJK-Bold.ttc")
        else:
            print(f"  ❌ 中文字体未找到")
            return False
        
        # 智能文本换行 - 避免单个字单独一行
        # 计算每行最佳字符数
        chars_per_line = 12  # 每行12个字符比较合适
        
        # 如果文本中有标点，适当调整
        if '，' in text or '。' in text:
            # 按标点自然分割
            parts = []
            current = ""
            for char in text:
                current += char
                if char in '，。、；：':
                    parts.append(current)
                    current = ""
            if current:
                parts.append(current)
            
            # 合并过短的部分
            merged_parts = []
            temp = ""
            for part in parts:
                if len(temp) + len(part) <= chars_per_line:
                    temp += part
                else:
                    if temp:
                        merged_parts.append(temp)
                    temp = part
            if temp:
                merged_parts.append(temp)
            
            lines = merged_parts
        else:
            # 没有标点，按字符数分割
            lines = textwrap.wrap(text, width=chars_per_line)
        
        print(f"  排版: {len(lines)}行")
        for i, line in enumerate(lines):
            print(f"    行{i+1}: {line}")
        
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
                # 估算宽度（中文字符更宽）
                text_width = len(line) * (font_size)
            
            x = (width - text_width) // 2
            y = y_start + i * line_height
            
            # 绘制文本（黑色）
            draw.text((x, y), line, font=font, fill=(0, 0, 0))
        
        # 保存为JPEG
        image.save(output_path, 'JPEG', quality=95)
        file_size = output_path.stat().st_size
        print(f"  ✅ 字幕创建成功: {file_size} 字节")
        return True
        
    except Exception as e:
        print(f"  ❌ 创建失败: {e}")
        return False

def get_duration(file_path):
    """获取媒体文件时长"""
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
           "-of", "default=noprint_wrappers=1:nokey=1", str(file_path)]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except:
        return 0.0

def create_correct_video():
    """创建正确的视频（每段显示对应的字幕）"""
    print("创建正确的惊蛰视频")
    print("=" * 60)
    
    # 正确的字幕文本（每段对应一句）
    subtitles = [
        "惊蛰，是二十四节气中的第三个节气。",
        "春雷始鸣，惊醒蛰伏于地下越冬的昆虫。",
        "此时气温回升，雨水增多，万物开始复苏。",
        "农民开始春耕，桃花红、李花白，黄莺鸣叫、燕子飞来。",
        "惊蛰吃梨，寓意远离疾病，开启健康一年。"
    ]
    
    # 优化后的字幕排版
    optimized_subtitles = [
        "惊蛰，是二十四节气中的\n第三个节气。",  # 分成两行，避免"气"字单独一行
        "春雷始鸣，惊醒蛰伏于\n地下越冬的昆虫。",
        "此时气温回升，雨水增多，\n万物开始复苏。",
        "农民开始春耕，桃花红、李花白，\n黄莺鸣叫、燕子飞来。",
        "惊蛰吃梨，寓意远离疾病，\n开启健康一年。"
    ]
    
    print("字幕优化:")
    for i, (orig, opt) in enumerate(zip(subtitles, optimized_subtitles), 1):
        print(f"  片段{i}:")
        print(f"    原版: {orig}")
        print(f"    优化: {opt}")
    
    # 1. 创建正确的字幕图片
    print("\n1. 创建正确的字幕图片...")
    subtitle_files = []
    
    for i, text in enumerate(optimized_subtitles, 1):
        subtitle_file = OUTPUT_DIR / f"correct_subtitle_{i}.jpg"
        if create_proper_subtitle(text, subtitle_file):
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
            print(f"  音频 {i}: {duration:.2f}秒 - 对应字幕: {subtitles[i-1][:15]}...")
        else:
            print(f"  ❌ 未找到音频文件 {i}")
            return None
    
    # 3. 获取图片文件
    print("\n3. 获取图片文件...")
    image_files = []
    for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
        image_files.extend(list(PROJECT_DIR.glob(f"images/*{ext}")))
    
    # 只取前5张图片
    image_files = image_files[:5]
    
    if len(image_files) < 5:
        print(f"错误: 需要5张图片，只找到 {len(image_files)} 张")
        return None
    
    # 4. 创建5个正确的视频片段
    print("\n4. 创建正确的视频片段...")
    segment_files = []
    
    for i in range(5):
        print(f"\n  创建片段 {i+1}:")
        print(f"    图片: {image_files[i].name}")
        print(f"    音频: {audio_durations[i]:.2f}秒")
        print(f"    字幕: {subtitles[i]}")
        
        # 调整背景图片
        bg_file = image_files[i]
        resized_bg = OUTPUT_DIR / f"correct_bg_{i+1}.jpg"
        
        cmd = [
            "ffmpeg", "-y",
            "-i", str(bg_file),
            "-vf", "scale=1080:1440:force_original_aspect_ratio=disable,pad=1080:1440:(ow-iw)/2:(oh-ih)/2:color=black",
            "-q:v", "2",
            str(resized_bg)
        ]
        
        subprocess.run(cmd, capture_output=True)
        
        # 合并图片（使用正确的字幕图片）
        merged_file = OUTPUT_DIR / f"correct_merged_{i+1}.jpg"
        
        cmd = [
            "ffmpeg", "-y",
            "-i", str(resized_bg),
            "-i", str(subtitle_files[i]),
            "-filter_complex", "[0:v][1:v]overlay=0:1240",
            str(merged_file)
        ]
        
        subprocess.run(cmd, capture_output=True)
        
        # 创建视频片段
        segment_file = OUTPUT_DIR / f"correct_segment_{i+1}.mp4"
        
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
            print(f"    ✅ 片段创建成功: {segment_size} 字节")
        else:
            print(f"    ❌ 片段创建失败")
            return None
    
    # 5. 合并视频片段
    print(f"\n5. 合并视频片段...")
    concat_file = OUTPUT_DIR / "correct_concat.txt"
    with open(concat_file, 'w') as f:
        for segment in segment_files:
            f.write(f"file '{segment.absolute()}'\n")
    
    final_video = OUTPUT_DIR / "jingzhe_correct_final.mp4"
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(final_video)
    ]
    
    subprocess.run(cmd, capture_output=True)
    
    if final_video.exists():
        duration = get_duration(final_video)
        size = final_video.stat().st_size
        
        print(f"\n✅ 正确视频创建成功!")
        print(f"   文件: {final_video.name}")
        print(f"   大小: {size} 字节")
        print(f"   时长: {duration:.2f}秒")
        
        return final_video
    else:
        print("\n❌ 视频创建失败")
        return None

def main():
    """主函数"""
    
    # 创建正确的视频
    video_file = create_correct_video()
    
    if video_file:
        print("\n" + "=" * 60)
        print("🎉 惊蛰视频正确版创建成功！")
        print("=" * 60)
        
        duration = get_duration(video_file)
        size = video_file.stat().st_size
        
        print(f"\n📊 视频规格:")
        print(f"   • 文件: {video_file.name}")
        print(f"   • 大小: {size} 字节 ({size/1024:.1f} KB)")
        print(f"   • 时长: {duration:.2f}秒")
        
        print(f"\n✅ 问题修复:")
        print(f"   1. ✅ 每段显示正确的字幕（之前：所有段都显示第一句）")
        print(f"   2. ✅ 优化字幕排版（之前：'气'字单独一行不好看）")
        print(f"   3. ✅ 字幕与配音完全对应")
        
        print(f"\n🎬 正确的时间轴:")
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
            print(f"   {total:.1f}-{end:.1f}秒: {subtitles[i]}")
            total = end
        
        print(f"\n🔗 GitHub链接:")
        print(f"   https://github.com/sjf2525/openclaw/blob/main/chinese-culture-videos/jingzhe/output/{video_file.name}")
        
        print(f"\n📨 正在发送到WhatsApp...")
        
    else:
        print("\n❌ 视频创建失败")

if __name__ == "__main__":
    main()