#!/usr/bin/env python3
"""
惊蛰节气短视频最终生成脚本
使用FFmpeg合成图片、音频、字幕
"""

import os
import subprocess
from pathlib import Path
import time

# 项目路径
PROJECT_DIR = Path(__file__).parent
AUDIO_DIR = PROJECT_DIR / "audio"
IMAGE_DIR = PROJECT_DIR / "images"
OUTPUT_DIR = PROJECT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def check_dependencies():
    """检查依赖"""
    print("检查依赖...")
    
    # 检查FFmpeg
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg 已安装")
            # 提取版本信息
            for line in result.stdout.split('\n'):
                if "ffmpeg version" in line:
                    print(f"   版本: {line.split('ffmpeg version')[1].split()[0]}")
                    break
        else:
            print("❌ FFmpeg 未安装")
            return False
    except:
        print("❌ FFmpeg 未安装")
        return False
    
    # 检查文件
    print("\n检查文件...")
    
    # 音频文件
    audio_file = AUDIO_DIR / "jingzhe_full_final.mp3"
    if audio_file.exists():
        size = audio_file.stat().st_size
        print(f"✅ 音频文件: {audio_file.name} ({size:,} 字节)")
        
        # 获取音频时长
        cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {audio_file}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            duration = float(result.stdout.strip())
            print(f"   时长: {duration:.2f} 秒")
    else:
        print(f"❌ 音频文件不存在: {audio_file}")
        return False
    
    # 图片文件
    image_files = list(IMAGE_DIR.glob("*.jpg")) + list(IMAGE_DIR.glob("*.webp")) + list(IMAGE_DIR.glob("*.png"))
    if image_files:
        print(f"✅ 找到 {len(image_files)} 张图片")
        for img in image_files[:3]:  # 只显示前3张
            size = img.stat().st_size
            print(f"   - {img.name} ({size:,} 字节)")
        if len(image_files) > 3:
            print(f"   ... 还有 {len(image_files)-3} 张")
    else:
        print("❌ 未找到图片文件")
        return False
    
    # 字幕文件
    subtitle_file = PROJECT_DIR / "subtitles.srt"
    if subtitle_file.exists():
        size = subtitle_file.stat().st_size
        print(f"✅ 字幕文件: {subtitle_file.name} ({size:,} 字节)")
    else:
        print("⚠️  字幕文件不存在，将创建不带字幕的视频")
    
    return True

def resize_images():
    """调整图片尺寸为小红书竖屏比例 3:4 (1080x1440)"""
    print("\n调整图片尺寸...")
    
    image_files = list(IMAGE_DIR.glob("*"))
    resized_dir = IMAGE_DIR / "resized"
    resized_dir.mkdir(exist_ok=True)
    
    resized_files = []
    
    for img_file in image_files:
        if img_file.is_dir():
            continue
            
        output_file = resized_dir / f"resized_{img_file.name}"
        
        # 确定输出格式
        if img_file.suffix.lower() in ['.jpg', '.jpeg']:
            output_file = output_file.with_suffix('.jpg')
        elif img_file.suffix.lower() == '.png':
            output_file = output_file.with_suffix('.png')
        elif img_file.suffix.lower() == '.webp':
            output_file = output_file.with_suffix('.jpg')  # 转换为JPG
        
        print(f"调整: {img_file.name} -> {output_file.name}")
        
        # FFmpeg调整尺寸命令
        # 使用缩放和裁剪来保持3:4比例
        cmd = [
            "ffmpeg", "-i", str(img_file),
            "-vf", "scale=1080:1440:force_original_aspect_ratio=disable,pad=1080:1440:(ow-iw)/2:(oh-ih)/2",
            "-y",  # 覆盖输出文件
            str(output_file)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                size = output_file.stat().st_size
                print(f"  成功: {size:,} 字节")
                resized_files.append(output_file)
            else:
                print(f"  失败: {result.stderr[:100]}")
        except Exception as e:
            print(f"  错误: {e}")
    
    return resized_files

def create_simple_video(images, audio, output_file, duration=15):
    """创建简单视频（图片幻灯片）"""
    print(f"\n创建视频: {output_file.name}")
    
    if not images:
        print("错误: 没有可用的图片")
        return False
    
    # 计算每张图片显示时间
    num_images = len(images)
    image_duration = duration / num_images
    
    # 创建FFmpeg复杂滤镜
    filter_complex = []
    
    # 添加图片输入
    for i, img in enumerate(images):
        filter_complex.append(f"[{i}:v]scale=1080:1440:force_original_aspect_ratio=disable,pad=1080:1440:(ow-iw)/2:(oh-ih)/2,setpts=PTS-STARTPTS[v{i}];")
    
    # 添加淡入淡出和连接
    for i in range(num_images):
        if i == 0:
            filter_complex.append(f"[v{i}]")
        else:
            filter_complex.append(f"[v{i}]")
    
    # 如果是多张图片，添加淡入淡出效果
    if num_images > 1:
        filter_complex.append(f"concat=n={num_images}:v=1:a=0[outv]")
    else:
        filter_complex.append(f"[v0]trim=duration={duration}[outv]")
    
    filter_str = "".join(filter_complex)
    
    # 构建FFmpeg命令
    cmd = ["ffmpeg", "-y"]
    
    # 添加图片输入
    for img in images:
        cmd.extend(["-loop", "1", "-t", str(image_duration), "-i", str(img)])
    
    # 添加音频输入
    cmd.extend(["-i", str(audio)])
    
    # 添加滤镜
    cmd.extend(["-filter_complex", filter_str])
    
    # 输出设置
    cmd.extend([
        "-map", "[outv]",
        "-map", f"{num_images}:a",  # 音频流索引
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",  # 以音频或视频较短者为准
        "-pix_fmt", "yuv420p",
        "-r", "30",  # 帧率
        str(output_file)
    ])
    
    print(f"执行命令: {' '.join(cmd[:10])}...")  # 只显示前10个参数
    
    try:
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        end_time = time.time()
        
        if result.returncode == 0:
            print(f"✅ 视频创建成功!")
            print(f"   耗时: {end_time - start_time:.2f} 秒")
            
            if output_file.exists():
                size = output_file.stat().st_size
                print(f"   文件大小: {size:,} 字节")
                
                # 获取视频信息
                info_cmd = f"ffprobe -v error -select_streams v:0 -show_entries stream=width,height,duration -of csv=p=0 {output_file}"
                info_result = subprocess.run(info_cmd, shell=True, capture_output=True, text=True)
                if info_result.returncode == 0:
                    info = info_result.stdout.strip().split(',')
                    if len(info) >= 3:
                        print(f"   分辨率: {info[0]}x{info[1]}")
                        print(f"   时长: {float(info[2]):.2f} 秒")
            
            return True
        else:
            print(f"❌ 视频创建失败")
            print(f"   错误: {result.stderr[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ 执行错误: {e}")
        return False

def create_video_with_subtitles(video_file, subtitle_file, output_file):
    """为视频添加字幕"""
    print(f"\n添加字幕: {output_file.name}")
    
    if not subtitle_file.exists():
        print("⚠️  字幕文件不存在，跳过字幕添加")
        return video_file
    
    cmd = [
        "ffmpeg", "-i", str(video_file),
        "-vf", f"subtitles={subtitle_file}:force_style='FontName=SimHei,FontSize=24,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=1,BorderStyle=3'",
        "-c:a", "copy",
        "-y",
        str(output_file)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ 字幕添加成功!")
            return output_file
        else:
            print(f"❌ 字幕添加失败: {result.stderr[:200]}")
            return video_file
    except Exception as e:
        print(f"❌ 字幕添加错误: {e}")
        return video_file

def create_quick_video():
    """创建快速测试视频（简单方法）"""
    print("\n创建快速测试视频...")
    
    # 获取第一张图片
    image_files = list(IMAGE_DIR.glob("*"))
    if not image_files:
        print("错误: 没有图片文件")
        return False
    
    first_image = image_files[0]
    
    # 音频文件
    audio_file = AUDIO_DIR / "jingzhe_full_final.mp3"
    
    # 输出文件
    output_file = OUTPUT_DIR / "jingzhe_quick_test.mp4"
    
    print(f"使用图片: {first_image.name}")
    print(f"使用音频: {audio_file.name}")
    print(f"输出文件: {output_file.name}")
    
    # 简单命令：图片+音频
    cmd = [
        "ffmpeg",
        "-loop", "1",
        "-i", str(first_image),
        "-i", str(audio_file),
        "-c:v", "libx264",
        "-t", "15",  # 15秒
        "-c:a", "aac",
        "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-y",
        str(output_file)
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ 快速测试视频创建成功!")
            
            if output_file.exists():
                size = output_file.stat().st_size
                print(f"   文件大小: {size:,} 字节")
                print(f"   文件路径: {output_file}")
            
            return output_file
        else:
            print(f"❌ 快速测试视频创建失败: {result.stderr[:200]}")
            return None
    except Exception as e:
        print(f"❌ 执行错误: {e}")
        return None

def main():
    """主函数"""
    print("=" * 60)
    print("惊蛰节气短视频生成器")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请先解决上述问题")
        return
    
    print("\n" + "=" * 60)
    print("开始视频生成流程")
    print("=" * 60)
    
    # 选项：快速测试或完整生成
    print("\n请选择生成方式:")
    print("1. 快速测试 (15秒简单视频)")
    print("2. 完整生成 (带多张图片和字幕)")
    
    choice = input("请输入选择 (1 或 2, 默认 1): ").strip() or "1"
    
    if choice == "1":
        # 快速测试
        video_file = create_quick_video()
        
        if video_file:
            print(f"\n🎉 快速测试视频已创建: {video_file}")
            print(f"   请下载并测试播放")
            
            # 显示文件信息
            cmd = f"file {video_file}"
            subprocess.run(cmd, shell=True)
            
            cmd = f"ls -lh {video_file}"
            subprocess.run(cmd, shell=True)
    
    elif choice == "2":
        # 完整生成
        print("\n开始完整视频生成...")
        
        # 1. 调整图片尺寸
        resized_images = resize_images()
        if not resized_images:
            print("❌ 图片调整失败")
            return
        
        # 2. 创建视频
        audio_file = AUDIO_DIR / "jingzhe_full_final.mp3"
        video_without_subtitles = OUTPUT_DIR / "jingzhe_no_subtitles.mp4"
        
        print(f"\n使用 {len(resized_images)} 张图片创建视频...")
        success = create_simple_video(
            images=resized_images[:5],  # 最多使用5张图片
            audio=audio_file,
            output_file=video_without_subtitles,
            duration=15  # 15秒视频
        )
        
        if not success:
            print("❌ 视频创建失败")
            return
        
        # 3. 添加字幕
        subtitle_file = PROJECT_DIR / "subtitles.srt"
        final_video = OUTPUT_DIR / "jingzhe_final_with_subtitles.mp4"
        
        if subtitle_file.exists():
            final_video = create_video_with_subtitles(
                video_file=video_without_subtitles,
                subtitle_file=subtitle_file,
                output_file=final_video
            )
        else:
            final_video = video_without_subtitles
        
        print(f"\n🎉 完整视频已创建: {final_video}")
        
        # 显示最终文件信息
        print("\n最终文件信息:")
        cmd = f"ls -lh {OUTPUT_DIR}/jingzhe_*.mp4"
        subprocess.run(cmd, shell=True)
    
    else:
        print("❌ 无效选择")
        return
    
    print("\n" + "=" * 60)
    print("视频生成完成!")
    print("=" * 60)
    print(f"\n输出目录: {OUTPUT_DIR}")
    print("请下载视频文件并在本地播放测试")
    print("\n下一步建议:")
    print("1. 测试视频播放效果")
    print("2. 调整音频音量或语速")
    print("3. 更换更合适的图片素材")
    print("4. 优化字幕样式和位置")
    print("5. 发布到小红书测试效果")

if __name__ == "__main__":
    main()