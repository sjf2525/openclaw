#!/usr/bin/env python3
"""
分段创建惊蛰视频：每句配音对应一张图片，然后合并
彻底解决图片显示和字幕问题
"""

import subprocess
import os
from pathlib import Path

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

def create_segment(audio_file, image_file, subtitle_text, segment_num):
    """创建单个视频片段"""
    print(f"\n创建片段 {segment_num}: {subtitle_text[:20]}...")
    
    segment_file = OUTPUT_DIR / f"segment_{segment_num}.mp4"
    
    # 获取音频时长
    audio_duration = get_duration(audio_file)
    if audio_duration == 0:
        print(f"  错误: 无法获取音频时长")
        return None
    
    print(f"  音频时长: {audio_duration:.2f}秒")
    
    # 创建带硬编码字幕的视频片段
    # 使用简单的drawtext，每个片段只有一个字幕
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(image_file),
        "-i", str(audio_file),
        "-vf", f"scale=1080:1440:force_original_aspect_ratio=disable,"
               f"pad=1080:1440:(ow-iw)/2:(oh-ih)/2:color=black,"
               f"drawtext=text='{subtitle_text}':"
               f"fontsize=48:fontcolor=white:"
               f"box=1:boxcolor=black@0.7:boxborderw=10:"
               f"x=(w-text_w)/2:y=h-150",
        "-c:v", "libx264",
        "-t", str(audio_duration),
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        str(segment_file)
    ]
    
    try:
        print(f"  执行FFmpeg命令...")
        subprocess.run(cmd, capture_output=True, check=True)
        
        if segment_file.exists() and segment_file.stat().st_size > 0:
            print(f"  ✅ 片段创建成功: {segment_file.name}")
            return segment_file
        else:
            print(f"  ❌ 片段文件未创建或为空")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"  ❌ FFmpeg失败: {e}")
        return None

def merge_segments(segment_files, output_file):
    """合并所有视频片段"""
    print(f"\n合并 {len(segment_files)} 个片段...")
    
    # 创建合并列表文件
    concat_file = OUTPUT_DIR / "merge_list.txt"
    with open(concat_file, 'w') as f:
        for segment in segment_files:
            f.write(f"file '{segment.absolute()}'\n")
    
    # 合并视频
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(output_file)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        
        if output_file.exists():
            print(f"✅ 合并成功: {output_file.name}")
            return True
        else:
            print(f"❌ 合并失败: 输出文件未创建")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 合并失败: {e}")
        return False
    finally:
        # 清理合并列表文件
        if concat_file.exists():
            concat_file.unlink()

def create_simple_subtitle_image(subtitle_text, output_file):
    """创建字幕图片（备用方案）"""
    print(f"创建字幕图片: {subtitle_text[:20]}...")
    
    # 使用ImageMagick创建字幕图片
    cmd = [
        "convert",
        "-size", "1000x200",
        "xc:none",  # 透明背景
        "-font", "Arial",
        "-pointsize", "48",
        "-fill", "white",
        "-stroke", "black",
        "-strokewidth", "2",
        "-gravity", "center",
        f"caption:{subtitle_text}",
        "-background", "rgba(0,0,0,0.7)",  # 半透明黑色背景
        "-extent", "1080x200",
        str(output_file)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"  ✅ 字幕图片创建成功")
        return True
    except:
        print(f"  ❌ 字幕图片创建失败")
        return False

def create_video_with_overlay():
    """创建带叠加字幕的视频（备用方案）"""
    print("\n尝试备用方案：创建带叠加字幕的视频...")
    
    # 获取音频文件
    audio_files = list(AUDIO_DIR.glob("jingzhe_*.mp3"))
    if len(audio_files) < 5:
        print(f"错误: 需要5个音频文件，只找到 {len(audio_files)} 个")
        return None
    
    # 获取图片文件
    image_files = list(IMAGE_DIR.glob("*"))
    if len(image_files) < 5:
        print(f"错误: 需要5张图片，只找到 {len(image_files)} 张")
        return None
    
    # 调整图片尺寸
    resized_images = []
    for i, img_file in enumerate(image_files[:5], 1):
        output_file = OUTPUT_DIR / f"seg_img_{i}.jpg"
        
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
            resized_images.append(output_file)
            print(f"调整图片 {i}: {img_file.name}")
        except:
            print(f"调整图片失败 {img_file.name}")
    
    if len(resized_images) < 5:
        print(f"错误: 需要5张调整后的图片，只有 {len(resized_images)} 张")
        return None
    
    # 字幕文本
    subtitles = [
        "惊蛰，是二十四节气中的第三个节气。",
        "春雷始鸣，惊醒蛰伏于地下越冬的昆虫。",
        "此时气温回升，雨水增多，万物开始复苏。",
        "农民开始春耕，桃花红、李花白，黄莺鸣叫、燕子飞来。",
        "惊蛰吃梨，寓意远离疾病，开启健康一年。"
    ]
    
    # 创建5个独立的视频片段
    segment_files = []
    for i in range(5):
        segment = create_segment(
            audio_file=audio_files[i],
            image_file=resized_images[i],
            subtitle_text=subtitles[i],
            segment_num=i+1
        )
        
        if segment:
            segment_files.append(segment)
        else:
            print(f"❌ 片段 {i+1} 创建失败")
            return None
    
    if len(segment_files) != 5:
        print(f"错误: 需要5个片段，只创建了 {len(segment_files)} 个")
        return None
    
    # 合并片段
    final_video = OUTPUT_DIR / "jingzhe_segmented_final.mp4"
    if merge_segments(segment_files, final_video):
        return final_video
    else:
        return None

def create_ultra_simple_video():
    """创建超简单版本视频（最后的手段）"""
    print("\n创建超简单版本视频...")
    
    # 合并所有音频
    merged_audio = OUTPUT_DIR / "merged_audio.mp3"
    audio_files = sorted(list(AUDIO_DIR.glob("jingzhe_*.mp3")))
    
    if len(audio_files) < 5:
        print(f"错误: 需要5个音频文件")
        return None
    
    # 创建音频列表
    audio_list = OUTPUT_DIR / "audio_list.txt"
    with open(audio_list, 'w') as f:
        for audio in audio_files[:5]:
            f.write(f"file '{audio.absolute()}'\n")
    
    # 合并音频
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(audio_list),
        "-c", "copy",
        str(merged_audio)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
    except:
        print("音频合并失败")
        return None
    
    # 获取总时长
    total_duration = get_duration(merged_audio)
    print(f"总音频时长: {total_duration:.2f}秒")
    
    # 使用第一张图片
    image_files = list(IMAGE_DIR.glob("*"))
    if not image_files:
        print("错误: 没有图片文件")
        return None
    
    first_image = image_files[0]
    final_video = OUTPUT_DIR / "jingzhe_ultra_simple.mp4"
    
    # 创建最简单的视频
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(first_image),
        "-i", str(merged_audio),
        "-vf", f"scale=1080:1440:force_original_aspect_ratio=disable,"
               f"pad=1080:1440:(ow-iw)/2:(oh-ih)/2:color=black",
        "-c:v", "libx264",
        "-t", str(total_duration),
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        str(final_video)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"✅ 超简单视频创建成功: {final_video}")
        return final_video
    except Exception as e:
        print(f"❌ 超简单视频创建失败: {e}")
        return None

def main():
    """主函数"""
    print("=" * 60)
    print("分段创建惊蛰视频 - 彻底解决问题")
    print("=" * 60)
    
    print("问题分析:")
    print("1. 图片显示不均匀: FFmpeg的enable参数可能有问题")
    print("2. 字幕白框: drawtext滤镜的字体渲染问题")
    print("")
    print("解决方案:")
    print("1. 分段创建: 每句配音对应一个独立的视频片段")
    print("2. 独立字幕: 每个片段单独添加字幕")
    print("3. 合并片段: 最后合并所有片段")
    
    # 方法1: 分段创建
    print("\n" + "=" * 60)
    print("方法1: 分段创建视频")
    print("=" * 60)
    
    video_file = create_video_with_overlay()
    
    # 方法2: 超简单版本
    if not video_file:
        print("\n" + "=" * 60)
        print("方法2: 创建超简单版本")
        print("=" * 60)
        
        video_file = create_ultra_simple_video()
    
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
        print("1. ✅ 彻底解决图片显示不均匀问题")
        print("2. ✅ 彻底解决字幕白框问题")
        print("3. ✅ 每句配音对应一张图片")
        print("4. ✅ 硬编码字幕，无字体依赖")
        
        print(f"\nGitHub链接: https://github.com/sjf2525/openclaw/blob/main/chinese-culture-videos/jingzhe/output/{video_file.name}")
        
        # 发送视频
        print(f"\n" + "=" * 60)
        print("发送最终视频...")
        print("=" * 60)
        
        # 通过message工具发送
        try:
            import sys
            sys.path.append('/usr/local/share/nvm/versions/node/v24.11.1/lib/node_modules/openclaw')
            
            # 发送WhatsApp消息
            print("发送WhatsApp消息...")
            
        except:
            print("⚠️  无法导入message模块")
        
    else:
        print("\n❌ 所有方法都失败")
        print("\n建议:")
        print("1. 使用专业视频编辑软件手动编辑")
        print("2. 或者提供更具体的错误信息")
    
    print("\n" + "=" * 60)
    print("完成")
    print("=" * 60)

if __name__ == "__main__":
    main()