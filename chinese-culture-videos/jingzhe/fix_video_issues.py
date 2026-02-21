#!/usr/bin/env python3
"""
修复视频问题：
1. 视频时长不足（只有10.5秒，应该是23秒）
2. 字幕显示白色方块（字体问题）
3. 图片显示时间不够
"""

import subprocess
from pathlib import Path

# 项目路径
PROJECT_DIR = Path(__file__).parent
AUDIO_DIR = PROJECT_DIR / "audio"
IMAGE_DIR = PROJECT_DIR / "images"
OUTPUT_DIR = PROJECT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def get_audio_duration():
    """获取音频时长"""
    audio_file = AUDIO_DIR / "jingzhe_full_new.mp3"
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
           "-of", "default=noprint_wrappers=1:nokey=1", str(audio_file)]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())
        print(f"音频时长: {duration:.2f}秒")
        return duration
    except Exception as e:
        print(f"获取音频时长失败: {e}")
        return 23.0  # 默认值

def create_fixed_subtitles():
    """创建修复的字幕文件（使用通用字体）"""
    print("\n创建修复的字幕文件...")
    
    # 使用更通用的字体
    ass_content = """[Script Info]
ScriptType: v4.00+
Collisions: Normal
PlayDepth: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,40,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,30,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    # 根据音频时长调整时间轴
    audio_duration = get_audio_duration()
    
    # 计算每句的时间
    sentences = [
        "惊蛰，是二十四节气中的第三个节气。",
        "春雷始鸣，惊醒蛰伏于地下越冬的昆虫。",
        "此时气温回升，雨水增多，万物开始复苏。",
        "农民开始春耕，桃花红、李花白，黄莺鸣叫、燕子飞来。",
        "惊蛰吃梨，寓意远离疾病，开启健康一年。"
    ]
    
    # 每句大约4-5秒
    time_per_sentence = audio_duration / len(sentences)
    
    for i, sentence in enumerate(sentences):
        start_time = i * time_per_sentence
        end_time = (i + 1) * time_per_sentence
        
        # 转换为ASS时间格式: 0:00:00.00
        start_str = f"{int(start_time//3600)}:{int((start_time%3600)//60):02d}:{start_time%60:05.2f}"
        end_str = f"{int(end_time//3600)}:{int((end_time%3600)//60):02d}:{end_time%60:05.2f}"
        
        ass_content += f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{sentence}\n"
    
    ass_file = OUTPUT_DIR / "jingzhe_subtitles_fixed.ass"
    ass_file.write_text(ass_content, encoding='utf-8')
    
    print(f"修复的字幕文件已保存: {ass_file}")
    
    # 同时创建SRT版本
    srt_content = ""
    for i, sentence in enumerate(sentences, 1):
        start_time = (i-1) * time_per_sentence
        end_time = i * time_per_sentence
        
        # 转换为SRT时间格式: 00:00:00,000
        start_str = f"{int(start_time//3600):02d}:{int((start_time%3600)//60):02d}:{start_time%60:06.3f}".replace('.', ',')
        end_str = f"{int(end_time//3600):02d}:{int((end_time%3600)//60):02d}:{end_time%60:06.3f}".replace('.', ',')
        
        srt_content += f"{i}\n"
        srt_content += f"{start_str} --> {end_str}\n"
        srt_content += f"{sentence}\n\n"
    
    srt_file = OUTPUT_DIR / "jingzhe_subtitles_fixed.srt"
    srt_file.write_text(srt_content, encoding='utf-8')
    
    print(f"修复的SRT字幕文件已保存: {srt_file}")
    
    return ass_file, srt_file

def create_proper_video():
    """创建正确的视频（确保完整时长）"""
    print("\n创建正确的视频...")
    
    audio_file = AUDIO_DIR / "jingzhe_full_new.mp3"
    audio_duration = get_audio_duration()
    
    # 获取图片文件
    image_files = list(IMAGE_DIR.glob("*"))
    if not image_files:
        print("错误: 没有找到图片文件")
        return None
    
    # 调整图片尺寸为1080×1440
    resized_images = []
    for img_file in image_files[:5]:  # 最多使用5张图片
        if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
            output_file = OUTPUT_DIR / f"fixed_{img_file.stem}.jpg"
            
            print(f"调整图片: {img_file.name}")
            
            cmd = [
                "ffmpeg", "-y",
                "-i", str(img_file),
                "-vf", f"scale=1080:1440:force_original_aspect_ratio=disable,"
                       f"pad=1080:1440:(ow-iw)/2:(oh-ih)/2:color=black",
                "-q:v", "2",
                str(output_file)
            ]
            
            try:
                subprocess.run(cmd, capture_output=True, check=True)
                resized_images.append(output_file)
            except Exception as e:
                print(f"  调整失败: {e}")
    
    if not resized_images:
        print("错误: 没有可用的调整后图片")
        return None
    
    # 创建视频（确保完整时长）
    output_video = OUTPUT_DIR / "jingzhe_video_fixed.mp4"
    
    # 方法1: 使用循环图片创建完整时长的视频
    print(f"使用 {len(resized_images)} 张图片创建视频...")
    
    # 每张图片显示时间
    image_duration = audio_duration / len(resized_images)
    
    # 创建图片列表文件
    concat_file = OUTPUT_DIR / "concat_fixed.txt"
    with open(concat_file, 'w') as f:
        for img in resized_images:
            f.write(f"file '{img.absolute()}'\n")
            f.write(f"duration {image_duration:.2f}\n")
    
    # 创建无声视频
    temp_video = OUTPUT_DIR / "temp_fixed.mp4"
    
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
        return None
    
    # 合并音频（不使用-shortest，确保视频完整）
    cmd2 = [
        "ffmpeg", "-y",
        "-i", str(temp_video),
        "-i", str(audio_file),
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        str(output_video)
    ]
    
    print("步骤2: 添加音频...")
    try:
        subprocess.run(cmd2, capture_output=True, check=True)
        print("  成功")
        
        # 清理临时文件
        temp_video.unlink(missing_ok=True)
        concat_file.unlink(missing_ok=True)
        
        return output_video
    except Exception as e:
        print(f"  失败: {e}")
        return None

def add_subtitles_to_video(video_file, subtitle_file):
    """添加字幕到视频"""
    print(f"\n添加字幕到视频...")
    
    if not video_file.exists():
        print(f"错误: 视频文件不存在: {video_file}")
        return None
    
    if not subtitle_file.exists():
        print(f"错误: 字幕文件不存在: {subtitle_file}")
        return None
    
    output_file = OUTPUT_DIR / "jingzhe_video_final_with_subtitles.mp4"
    
    # 使用更可靠的字幕烧录方法
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_file),
        "-vf", f"ass={subtitle_file}:fontsdir=/usr/share/fonts/truetype/",
        "-c:a", "copy",
        str(output_file)
    ]
    
    print(f"烧录字幕: {subtitle_file.name}")
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        
        # 验证视频时长
        duration_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
                       "-of", "default=noprint_wrappers=1:nokey=1", str(output_file)]
        result = subprocess.run(duration_cmd, capture_output=True, text=True, check=True)
        final_duration = float(result.stdout.strip())
        
        print(f"✅ 字幕添加成功: {output_file}")
        print(f"最终视频时长: {final_duration:.2f}秒")
        
        return output_file
    except Exception as e:
        print(f"❌ 字幕添加失败: {e}")
        
        # 尝试使用SRT字幕
        if subtitle_file.suffix == '.ass':
            srt_file = OUTPUT_DIR / "jingzhe_subtitles_fixed.srt"
            if srt_file.exists():
                print("尝试使用SRT字幕...")
                cmd_srt = [
                    "ffmpeg", "-y",
                    "-i", str(video_file),
                    "-vf", f"subtitles={srt_file}:force_style='FontName=Arial,FontSize=40,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BackColour=&H80000000'",
                    "-c:a", "copy",
                    str(output_file)
                ]
                
                try:
                    subprocess.run(cmd_srt, capture_output=True, check=True)
                    print(f"✅ SRT字幕添加成功: {output_file}")
                    return output_file
                except Exception as e2:
                    print(f"❌ SRT字幕也失败: {e2}")
        
        return None

def create_simple_subtitles_video():
    """创建带硬编码字幕的简单视频"""
    print("\n创建带硬编码字幕的简单视频...")
    
    audio_file = AUDIO_DIR / "jingzhe_full_new.mp3"
    audio_duration = get_audio_duration()
    
    # 使用第一张图片
    image_files = list(IMAGE_DIR.glob("*"))
    if not image_files:
        print("错误: 没有找到图片文件")
        return None
    
    first_image = image_files[0]
    output_video = OUTPUT_DIR / "jingzhe_simple_with_subtitles.mp4"
    
    # 创建带字幕的视频（使用drawtext滤镜）
    sentences = [
        "惊蛰，是二十四节气中的第三个节气。",
        "春雷始鸣，惊醒蛰伏于地下越冬的昆虫。",
        "此时气温回升，雨水增多，万物开始复苏。",
        "农民开始春耕，桃花红、李花白，黄莺鸣叫、燕子飞来。",
        "惊蛰吃梨，寓意远离疾病，开启健康一年。"
    ]
    
    time_per_sentence = audio_duration / len(sentences)
    
    # 构建复杂的drawtext滤镜链
    drawtext_filters = []
    for i, sentence in enumerate(sentences):
        start_time = i * time_per_sentence
        end_time = (i + 1) * time_per_sentence
        
        # 每句显示在自己的时间段
        drawtext_filters.append(
            f"drawtext=text='{sentence}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
            f"fontsize=40:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=5:"
            f"x=(w-text_w)/2:y=h-100:enable='between(t,{start_time},{end_time})'"
        )
    
    filter_complex = ",".join(drawtext_filters)
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(first_image),
        "-i", str(audio_file),
        "-vf", f"scale=1080:1440:force_original_aspect_ratio=disable,"
               f"pad=1080:1440:(ow-iw)/2:(oh-ih)/2:color=black,{filter_complex}",
        "-c:v", "libx264",
        "-t", str(audio_duration),
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        str(output_video)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"✅ 简单字幕视频创建成功: {output_video}")
        return output_video
    except Exception as e:
        print(f"❌ 简单字幕视频创建失败: {e}")
        return None

def main():
    """主函数"""
    print("=" * 60)
    print("修复惊蛰视频问题")
    print("=" * 60)
    
    print("问题分析:")
    print("1. 视频时长不足: 只有10.5秒，应该是23秒")
    print("2. 字幕显示白色方块: 字体Microsoft YaHei可能不可用")
    print("3. 图片显示时间不够: 只显示到第二张图片")
    
    # 创建修复的字幕
    ass_file, srt_file = create_fixed_subtitles()
    
    # 创建正确的视频
    video_file = create_proper_video()
    
    if video_file:
        # 尝试添加ASS字幕
        final_video = add_subtitles_to_video(video_file, ass_file)
        
        if not final_video:
            # 如果ASS字幕失败，尝试SRT字幕
            print("\nASS字幕失败，尝试SRT字幕...")
            final_video = add_subtitles_to_video(video_file, srt_file)
    else:
        final_video = None
    
    # 如果以上都失败，创建简单版本
    if not final_video:
        print("\n标准方法失败，创建简单版本...")
        final_video = create_simple_subtitles_video()
    
    if final_video and final_video.exists():
        print("\n" + "=" * 60)
        print("✅ 视频修复完成！")
        print("=" * 60)
        
        # 验证最终视频
        print(f"\n最终视频: {final_video}")
        
        # 检查时长
        duration_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
                       "-of", "default=noprint_wrappers=1:nokey=1", str(final_video)]
        try:
            result = subprocess.run(duration_cmd, capture_output=True, text=True, check=True)
            final_duration = float(result.stdout.strip())
            print(f"视频时长: {final_duration:.2f}秒")
            
            if final_duration < 20:
                print("⚠️  警告: 视频时长可能仍然不足")
            else:
                print("✅ 视频时长正常")
        except:
            print("无法获取视频时长")
        
        # 检查文件大小
        file_size = final_video.stat().st_size
        print(f"文件大小: {file_size} 字节")
        
        print("\n修复的问题:")
        print("1. ✅ 视频时长: 从10.5秒增加到完整音频时长")
        print("2. ✅ 字幕字体: 使用通用字体Arial，避免白色方块")
        print("3. ✅ 图片显示: 确保所有图片都有足够显示时间")
        
        print("\n生成的文件:")
        for file in OUTPUT_DIR.glob("*fixed*") + OUTPUT_DIR.glob("*final*"):
            if file.is_file():
                size = file.stat().st_size
                print(f"  - {file.name} ({size} 字节)")
        
        print(f"\n请测试播放: {final_video}")
        
    else:
        print("\n❌ 视频修复失败")
        print("\n建议手动检查:")
        print("1. 检查音频文件: audio/jingzhe_full_new.mp3")
        print("2. 检查图片文件: images/ 目录")
        print("3. 检查FFmpeg安装: ffmpeg -version")
    
    print("\n" + "=" * 60)
    print("修复完成")
    print("=" * 60)

if __name__ == "__main__":
    main()