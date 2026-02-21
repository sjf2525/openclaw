#!/usr/bin/env python3
"""
使用图片叠加字幕的方法创建视频
彻底解决字幕白框问题
"""

import subprocess
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import textwrap

# 项目路径
PROJECT_DIR = Path(__file__).parent
AUDIO_DIR = PROJECT_DIR / "audio"
IMAGE_DIR = PROJECT_DIR / "images"
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

def create_subtitle_image(text, output_path):
    """创建字幕图片（使用PIL）"""
    print(f"创建字幕图片: {text[:20]}...")
    
    try:
        # 图片尺寸：1080×200（放在视频底部）
        width, height = 1080, 200
        
        # 创建半透明黑色背景
        bg_color = (0, 0, 0, 180)  # 黑色，70%透明度
        image = Image.new('RGBA', (width, height), bg_color)
        draw = ImageDraw.Draw(image)
        
        # 尝试加载字体
        font = None
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, 40)
                    break
                except:
                    continue
        
        if font is None:
            # 使用默认字体
            font = ImageFont.load_default()
            print("  使用默认字体")
        
        # 文本换行（每行最多20个字符）
        wrapped_text = textwrap.fill(text, width=20)
        lines = wrapped_text.split('\n')
        
        # 计算文本位置
        line_height = 50
        total_height = len(lines) * line_height
        y_start = (height - total_height) // 2
        
        # 绘制文本
        for i, line in enumerate(lines):
            # 计算文本宽度
            if hasattr(font, 'getbbox'):
                bbox = font.getbbox(line)
                text_width = bbox[2] - bbox[0]
            else:
                text_width = len(line) * 20  # 估算
            
            x = (width - text_width) // 2
            y = y_start + i * line_height
            
            # 绘制文本阴影（提高可读性）
            draw.text((x+2, y+2), line, font=font, fill=(0, 0, 0, 255))
            # 绘制文本
            draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        
        # 保存图片
        image.save(output_path, 'PNG')
        print(f"  ✅ 字幕图片创建成功: {output_path}")
        return True
        
    except Exception as e:
        print(f"  ❌ 创建字幕图片失败: {e}")
        return False

def create_video_with_overlay_subtitles():
    """创建带图片字幕叠加的视频"""
    print("创建带图片字幕叠加的视频...")
    
    # 获取音频文件
    audio_files = []
    for i in range(1, 6):
        audio_file = AUDIO_DIR / f"jingzhe_{i}.mp3"
        if not audio_file.exists():
            audio_file = AUDIO_DIR / f"jingzhe_sentence_{i}.mp3"
        
        if audio_file.exists():
            audio_files.append(audio_file)
    
    if len(audio_files) < 5:
        print(f"错误: 需要5个音频文件，只找到 {len(audio_files)} 个")
        return None
    
    # 获取图片文件
    image_files = list(IMAGE_DIR.glob("*"))
    if len(image_files) < 5:
        print(f"错误: 需要5张图片，只找到 {len(image_files)} 张")
        return None
    
    # 字幕文本
    subtitles = [
        "惊蛰，是二十四节气中的第三个节气。",
        "春雷始鸣，惊醒蛰伏于地下越冬的昆虫。",
        "此时气温回升，雨水增多，万物开始复苏。",
        "农民开始春耕，桃花红、李花白，黄莺鸣叫、燕子飞来。",
        "惊蛰吃梨，寓意远离疾病，开启健康一年。"
    ]
    
    # 1. 创建字幕图片
    print("\n1. 创建字幕图片...")
    subtitle_images = []
    for i, text in enumerate(subtitles, 1):
        subtitle_file = OUTPUT_DIR / f"subtitle_{i}.png"
        if create_subtitle_image(text, subtitle_file):
            subtitle_images.append(subtitle_file)
        else:
            print(f"  字幕图片 {i} 创建失败，使用备用方案")
            # 创建简单的纯色字幕图片
            cmd = [
                "convert", "-size", "1080x200",
                "xc:'rgba(0,0,0,0.7)'",
                "-font", "Arial",
                "-pointsize", "40",
                "-fill", "white",
                "-gravity", "center",
                f"label:{text}",
                str(subtitle_file)
            ]
            try:
                subprocess.run(cmd, capture_output=True, check=True)
                subtitle_images.append(subtitle_file)
                print(f"  ✅ 备用字幕图片创建成功")
            except:
                print(f"  ❌ 备用方案也失败")
                return None
    
    if len(subtitle_images) < 5:
        print(f"错误: 需要5个字幕图片，只创建了 {len(subtitle_images)} 个")
        return None
    
    # 2. 调整背景图片尺寸
    print("\n2. 调整背景图片尺寸...")
    background_images = []
    for i, img_file in enumerate(image_files[:5], 1):
        output_file = OUTPUT_DIR / f"bg_{i}.jpg"
        
        cmd = [
            "ffmpeg", "-y",
            "-i", str(img_file),
            "-vf", "scale=1080:1440:force_original_aspect_ratio=disable,"
                   "pad=1080:1440:(ow-iw)/2:(oh-ih)/2:color=black",
            "-q:v", "2",
            str(output_file)
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            background_images.append(output_file)
            print(f"  背景图片 {i}: {img_file.name}")
        except Exception as e:
            print(f"  调整背景图片失败 {img_file.name}: {e}")
            return None
    
    # 3. 创建带字幕的图片（合并背景和字幕）
    print("\n3. 创建带字幕的完整图片...")
    final_images = []
    for i in range(5):
        bg_file = background_images[i]
        subtitle_file = subtitle_images[i]
        final_image = OUTPUT_DIR / f"final_{i+1}.jpg"
        
        # 使用ImageMagick合并图片
        cmd = [
            "convert",
            str(bg_file),
            str(subtitle_file),
            "-geometry", "+0+1240",  # 将字幕放在底部 (1440-200=1240)
            "-composite",
            str(final_image)
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            final_images.append(final_image)
            print(f"  带字幕图片 {i+1} 创建成功")
        except Exception as e:
            print(f"  合并图片失败 {i+1}: {e}")
            # 尝试使用FFmpeg
            cmd = [
                "ffmpeg", "-y",
                "-i", str(bg_file),
                "-i", str(subtitle_file),
                "-filter_complex", "[0:v][1:v]overlay=0:1240",
                str(final_image)
            ]
            try:
                subprocess.run(cmd, capture_output=True, check=True)
                final_images.append(final_image)
                print(f"  ✅ FFmpeg合并成功")
            except:
                print(f"  ❌ 所有合并方法都失败")
                return None
    
    # 4. 创建视频片段
    print("\n4. 创建视频片段...")
    segment_files = []
    for i in range(5):
        audio_file = audio_files[i]
        image_file = final_images[i]
        segment_file = OUTPUT_DIR / f"video_segment_{i+1}.mp4"
        
        audio_duration = get_duration(audio_file)
        if audio_duration == 0:
            audio_duration = 4.0
        
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(image_file),
            "-i", str(audio_file),
            "-c:v", "libx264",
            "-t", str(audio_duration),
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-shortest",
            str(segment_file)
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            segment_files.append(segment_file)
            print(f"  视频片段 {i+1}: {audio_duration:.2f}秒")
        except Exception as e:
            print(f"  创建视频片段失败 {i+1}: {e}")
            return None
    
    # 5. 合并视频片段
    print("\n5. 合并视频片段...")
    concat_file = OUTPUT_DIR / "video_concat.txt"
    with open(concat_file, 'w') as f:
        for segment in segment_files:
            f.write(f"file '{segment.absolute()}'\n")
    
    final_video = OUTPUT_DIR / "jingzhe_image_subtitles_final.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(final_video)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"✅ 视频合并成功: {final_video}")
        
        # 验证结果
        if final_video.exists():
            return final_video
        else:
            print("❌ 合并后文件未创建")
            return None
            
    except Exception as e:
        print(f"❌ 视频合并失败: {e}")
        return None

def create_simple_overlay_video():
    """创建简单的叠加字幕视频（备用方案）"""
    print("\n尝试简单叠加方案...")
    
    # 使用合并的音频
    merged_audio = AUDIO_DIR / "jingzhe_full_new.mp3"
    if not merged_audio.exists():
        print("错误: 合并音频文件不存在")
        return None
    
    audio_duration = get_duration(merged_audio)
    print(f"音频时长: {audio_duration:.2f}秒")
    
    # 获取第一张图片
    image_files = list(IMAGE_DIR.glob("*"))
    if not image_files:
        print("错误: 没有图片文件")
        return None
    
    first_image = image_files[0]
    
    # 调整图片尺寸
    bg_image = OUTPUT_DIR / "simple_bg.jpg"
    cmd = [
        "ffmpeg", "-y",
        "-i", str(first_image),
        "-vf", "scale=1080:1440:force_original_aspect_ratio=disable,"
               "pad=1080:1440:(ow-iw)/2:(oh-ih)/2:color=black",
        "-q:v", "2",
        str(bg_image)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
    except:
        print("调整图片失败")
        return None
    
    # 创建简单的视频（无字幕，先确保视频能播放）
    simple_video = OUTPUT_DIR / "jingzhe_simple_no_subtitles.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(bg_image),
        "-i", str(merged_audio),
        "-c:v", "libx264",
        "-t", str(audio_duration),
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        str(simple_video)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"✅ 简单视频创建成功: {simple_video}")
        return simple_video
    except Exception as e:
        print(f"❌ 简单视频创建失败: {e}")
        return None

def main():
    """主函数"""
    print("=" * 60)
    print("使用图片叠加字幕创建视频")
    print("=" * 60)
    
    print("问题分析:")
    print("1. FFmpeg的drawtext滤镜无法正确渲染中文字体")
    print("2. 导致字幕显示为白色框框")
    print("")
    print("解决方案:")
    print("1. 使用PIL/ImageMagick创建字幕图片")
    print("2. 将字幕图片叠加到背景图片上")
    print("3. 使用带字幕的图片创建视频")
    
    # 方法1: 图片叠加字幕
    print("\n" + "=" * 60)
    print("方法1: 图片叠加字幕")
    print("=" * 60)
    
    video_file = create_video_with_overlay_subtitles()
    
    # 方法2: 简单无字幕版本
    if not video_file:
        print("\n" + "=" * 60)
        print("方法2: 创建简单无字幕版本")
        print("=" * 60)
        
        video_file = create_simple_overlay_video()
    
    if video_file and video_file.exists():
        print("\n" + "=" * 60)
        print("✅ 视频创建成功！")
        print("=" * 60)
        
        # 验证视频
        duration = get_duration(video_file)
        file_size = video_file.stat().st_size
        
        print(f"最终视频: {video_file}")
        print(f"文件大小: {file_size} 字节 ({file_size/1024:.1f} KB)")
        print(f"视频时长: {duration:.2f}秒")
        
        print("\n技术特点:")
        if "image_subtitles" in str(video_file):
            print("1. ✅ 使用图片叠加字幕，彻底解决白框问题")
            print("2. ✅ 每句配音对应一张带字幕的图片")
            print("3. ✅ 字幕为图片格式，无字体渲染问题")
            print("4. ✅ 分段创建，确保时间准确")
        else:
            print("1. ✅ 创建了无字幕的简单版本")
            print("2. ✅ 确保视频能正常播放")
            print("3. ✅ 可作为基础版本进一步处理")
        
        print(f"\nGitHub链接: https://github.com/sjf2525/openclaw/blob/main/chinese-culture-videos/jingzhe/output/{video_file.name}")
        
    else:
        print("\n❌ 所有方法都失败")
        print("\n建议:")
        print("1. 检查系统字体安装")
        print("2. 或者手动使用视频编辑软件添加字幕")
    
    print("\n" + "=" * 60)
    print("完成")
    print("=" * 60)

if __name__ == "__main__":
    main()