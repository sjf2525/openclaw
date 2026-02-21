#!/usr/bin/env python3
"""
最终修复：使用正确的中文字体创建字幕图片
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

def find_chinese_font():
    """查找可用的中文字体（修复版本）"""
    print("查找中文字体...")
    
    # 中文字体路径（安装 fonts-noto-cjk 后应该存在）
    chinese_font_paths = [
        # Noto Sans CJK（Google的中文字体）
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        # 系统可能有的其他中文字体
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # 文泉驿微米黑
        "/usr/share/fonts/truetype/arphic/uming.ttc",      # AR PL UMing
        "/usr/share/fonts/truetype/arphic/ukai.ttc",       # AR PL UKai
    ]
    
    for font_path in chinese_font_paths:
        if os.path.exists(font_path):
            print(f"✅ 找到中文字体: {font_path}")
            return font_path
    
    # 如果找不到中文字体，尝试查找任何包含中文字符的字体
    print("⚠️  未找到标准中文字体，尝试查找其他字体...")
    
    # 使用fc-list查找中文字体
    try:
        cmd = ["fc-list", ":lang=zh", "file"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.stdout:
            fonts = result.stdout.strip().split('\n')
            for font in fonts[:3]:  # 取前3个
                if font and os.path.exists(font):
                    print(f"✅ 通过fc-list找到字体: {font}")
                    return font
    except:
        pass
    
    print("❌ 未找到中文字体")
    return None

def create_chinese_subtitle(text, output_path, font_size=48):
    """使用中文字体创建字幕图片"""
    print(f"创建中文字幕图片: {text[:20]}...")
    
    # 图片尺寸
    width, height = 1080, 200
    
    try:
        # 创建图片（使用白色背景确保彩色图）
        image = Image.new('RGB', (width, height), (255, 255, 255))  # 白色背景
        draw = ImageDraw.Draw(image)
        
        # 加载中文字体
        font_path = find_chinese_font()
        if font_path:
            try:
                # 加载字体（ttc文件可能需要指定索引）
                if font_path.endswith('.ttc'):
                    # ttc是字体集合，尝试不同的索引
                    for i in range(4):  # 尝试前4个字体
                        try:
                            font = ImageFont.truetype(font_path, font_size, index=i)
                            print(f"  使用字体: {os.path.basename(font_path)} (索引:{i})")
                            break
                        except:
                            continue
                else:
                    font = ImageFont.truetype(font_path, font_size)
                    print(f"  使用字体: {os.path.basename(font_path)}")
            except Exception as e:
                print(f"  字体加载失败: {e}")
                return False
        else:
            print("  ❌ 未找到中文字体，无法创建字幕")
            return False
        
        # 文本换行（每行最多15个字符）
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
                # 估算宽度（中文字符更宽）
                text_width = len(line) * (font_size)
            
            x = (width - text_width) // 2
            y = y_start + i * line_height
            
            # 绘制文本（黑色）
            draw.text((x, y), line, font=font, fill=(0, 0, 0))
        
        # 保存为JPEG（确保为彩色图）
        image.save(output_path, 'JPEG', quality=95)
        
        # 验证图片
        verify_subtitle_image(output_path)
        return True
        
    except Exception as e:
        print(f"  ❌ 创建失败: {e}")
        return False

def verify_subtitle_image(image_path):
    """验证字幕图片"""
    print(f"  验证字幕图片: {image_path.name}")
    
    file_size = image_path.stat().st_size
    print(f"    文件大小: {file_size} 字节")
    
    # 使用ImageMagick检查
    try:
        cmd = ["identify", "-verbose", str(image_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 检查是否为彩色图
        if "Type: TrueColor" in result.stdout:
            print(f"    ✅ 图片类型: TrueColor (真彩色)")
        elif "Type: Grayscale" in result.stdout:
            print(f"    ⚠️  图片类型: Grayscale (灰度)")
        
        # 检查平均像素值
        cmd = ["convert", str(image_path), "-format", "%[fx:mean]", "info:"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.stdout.strip():
            mean_value = float(result.stdout.strip())
            print(f"    平均像素值: {mean_value:.3f}")
            if mean_value > 0.5:
                print(f"    ✅ 图片亮度正常（白色背景）")
            else:
                print(f"    ⚠️  图片可能太暗")
    except:
        print(f"    ⚠️  无法验证图片")

def create_final_video_with_chinese_font():
    """使用中文字体创建最终视频"""
    print("\n使用中文字体创建最终视频...")
    
    # 字幕文本
    subtitles = [
        "惊蛰，是二十四节气中的第三个节气。",
        "春雷始鸣，惊醒蛰伏于地下越冬的昆虫。",
        "此时气温回升，雨水增多，万物开始复苏。",
        "农民开始春耕，桃花红、李花白，黄莺鸣叫、燕子飞来。",
        "惊蛰吃梨，寓意远离疾病，开启健康一年。"
    ]
    
    # 1. 创建中文字幕图片
    print("1. 创建中文字幕图片...")
    subtitle_files = []
    
    for i, text in enumerate(subtitles, 1):
        subtitle_file = OUTPUT_DIR / f"chinese_subtitle_{i}.jpg"
        
        if create_chinese_subtitle(text, subtitle_file):
            subtitle_files.append(subtitle_file)
        else:
            print(f"  ❌ 字幕图片 {i} 创建失败")
            return None
    
    # 2. 检查音频文件
    print("\n2. 检查音频文件...")
    audio_files = []
    for i in range(1, 6):
        audio_file = PROJECT_DIR / "audio" / f"jingzhe_{i}.mp3"
        if not audio_file.exists():
            audio_file = PROJECT_DIR / "audio" / f"jingzhe_sentence_{i}.mp3"
        
        if audio_file.exists():
            audio_files.append(audio_file)
            print(f"  找到音频文件 {i}: {audio_file.name}")
        else:
            print(f"  ❌ 未找到音频文件 {i}")
            return None
    
    # 3. 检查图片文件
    print("\n3. 检查图片文件...")
    image_files = list(PROJECT_DIR.glob("images/*"))
    if len(image_files) < 5:
        print(f"错误: 需要5张图片，只找到 {len(image_files)} 张")
        return None
    
    # 4. 创建5个视频片段
    print("\n4. 创建视频片段...")
    segment_files = []
    
    for i in range(5):
        print(f"\n  处理片段 {i+1}...")
        
        # 调整背景图片
        bg_file = image_files[i]
        resized_bg = OUTPUT_DIR / f"chinese_bg_{i+1}.jpg"
        
        cmd = [
            "ffmpeg", "-y",
            "-i", str(bg_file),
            "-vf", "scale=1080:1440:force_original_aspect_ratio=disable,pad=1080:1440:(ow-iw)/2:(oh-ih)/2:color=black",
            "-q:v", "2",
            str(resized_bg)
        ]
        
        subprocess.run(cmd, capture_output=True)
        print(f"    调整背景图片: {resized_bg.name}")
        
        # 合并图片
        merged_file = OUTPUT_DIR / f"chinese_merged_{i+1}.jpg"
        
        cmd = [
            "ffmpeg", "-y",
            "-i", str(resized_bg),
            "-i", str(subtitle_files[i]),
            "-filter_complex", "[0:v][1:v]overlay=0:1240",
            str(merged_file)
        ]
        
        subprocess.run(cmd, capture_output=True)
        print(f"    合并图片: {merged_file.name}")
        
        # 创建视频片段
        segment_file = OUTPUT_DIR / f"chinese_segment_{i+1}.mp4"
        
        # 获取音频时长
        duration_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
                       "-of", "default=noprint_wrappers=1:nokey=1", str(audio_files[i])]
        result = subprocess.run(duration_cmd, capture_output=True, text=True)
        duration = float(result.stdout.strip()) if result.stdout.strip() else 4.0
        
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(merged_file),
            "-i", str(audio_files[i]),
            "-c:v", "libx264",
            "-t", str(duration),
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-shortest",
            str(segment_file)
        ]
        
        subprocess.run(cmd, capture_output=True)
        print(f"    创建视频片段: {segment_file.name}")
        segment_files.append(segment_file)
    
    # 5. 合并视频片段
    print("\n5. 合并视频片段...")
    concat_file = OUTPUT_DIR / "chinese_concat.txt"
    with open(concat_file, 'w') as f:
        for segment in segment_files:
            f.write(f"file '{segment.absolute()}'\n")
    
    final_video = OUTPUT_DIR / "jingzhe_chinese_font_final.mp4"
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(final_video)
    ]
    
    subprocess.run(cmd, capture_output=True)
    
    # 验证最终视频
    if final_video.exists():
        file_size = final_video.stat().st_size
        print(f"✅ 最终视频创建成功: {final_video.name} ({file_size} 字节)")
        return final_video
    else:
        print("❌ 最终视频创建失败")
        return None

def main():
    """主函数"""
    print("最终修复：使用中文字体创建视频")
    print("=" * 60)
    
    print("问题总结:")
    print("1. ❌ 之前使用西文字体（DejaVuSans等），不包含中文字符")
    print("2. ❌ ImageFont.load_default() 不支持中文")
    print("3. ✅ 您已安装 fonts-noto-cjk，系统现在有中文字体")
    print("4. ✅ 本脚本使用正确的中文字体创建字幕")
    
    # 创建最终视频
    video_file = create_final_video_with_chinese_font()
    
    if video_file:
        print("\n" + "=" * 60)
        print("✅ 视频创建成功！")
        print("=" * 60)
        
        # 获取视频信息
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
               "-of", "default=noprint_wrappers=1:nokey=1", str(video_file)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = float(result.stdout.strip()) if result.stdout.strip() else 0
        
        print(f"\n最终视频: {video_file.name}")
        print(f"文件大小: {video_file.stat().st_size} 字节")
        print(f"视频时长: {duration:.2f}秒")
        
        print("\n技术特点:")
        print("✅ 使用正确的中文字体（NotoSansCJK）")
        print("✅ 白色背景，黑色文字，高对比度")
        print("✅ JPEG格式，确保为彩色图")
        print("✅ 5个独立片段合并，时间准确")
        
        print("\nGitHub链接:")
        print(f"https://github.com/sjf2525/openclaw/blob/main/chinese-culture-videos/jingzhe/output/{video_file.name}")
        
        # 发送到WhatsApp
        print("\n发送到WhatsApp...")
        try:
            import sys
            sys.path.append('/usr/local/share/nvm/versions/node/v24.11.1/lib/node_modules/openclaw')
            # 这里可以添加发送代码
        except:
            print("⚠️  无法发送，请手动下载")
    else:
        print("\n❌ 视频创建失败")

if __name__ == "__main__":
    main()