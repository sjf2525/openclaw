#!/usr/bin/env python3
"""
惊蛰视频完整工作流程 - 包含所有步骤的完整Python脚本
用于诊断字幕显示问题
"""

import subprocess
import os
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# ==================== 配置部分 ====================
PROJECT_DIR = Path(__file__).parent
AUDIO_DIR = PROJECT_DIR / "audio"
IMAGE_DIR = PROJECT_DIR / "images"
OUTPUT_DIR = PROJECT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# 字幕文本
SUBTITLES = [
    "惊蛰，是二十四节气中的第三个节气。",
    "春雷始鸣，惊醒蛰伏于地下越冬的昆虫。",
    "此时气温回升，雨水增多，万物开始复苏。",
    "农民开始春耕，桃花红、李花白，黄莺鸣叫、燕子飞来。",
    "惊蛰吃梨，寓意远离疾病，开启健康一年。"
]

# 邮件配置
SMTP_CONFIG = {
    "host": "smtp.gmail.com",
    "port": 465,
    "username": "shenjianfei82@gmail.com",
    "password": "ffojcxxakliwbjgd",
    "use_ssl": True
}

TO_EMAIL = "shenjianfei82@gmail.com"
FROM_EMAIL = "shenjianfei82@gmail.com"

# ==================== 工具函数 ====================
def get_duration(file_path):
    """获取媒体文件时长"""
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
           "-of", "default=noprint_wrappers=1:nokey=1", str(file_path)]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except:
        return 0.0

def find_font():
    """查找可用的中文字体"""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            print(f"找到字体: {font_path}")
            return font_path
    
    print("警告: 未找到系统字体，使用默认字体")
    return None

# ==================== 字幕创建函数 ====================
def create_subtitle_with_pil(text, output_path, font_size=40):
    """使用PIL创建字幕图片"""
    print(f"创建字幕图片: {text[:20]}...")
    
    # 图片尺寸
    width, height = 1080, 200
    
    try:
        # 创建图片
        image = Image.new('RGBA', (width, height), (0, 0, 0, 180))  # 黑色半透明背景
        draw = ImageDraw.Draw(image)
        
        # 加载字体
        font_path = find_font()
        if font_path:
            try:
                font = ImageFont.truetype(font_path, font_size)
                print(f"  使用字体: {os.path.basename(font_path)}")
            except:
                print(f"  警告: 无法加载字体 {font_path}，使用默认字体")
                font = ImageFont.load_default()
        else:
            font = ImageFont.load_default()
            print("  使用默认字体")
        
        # 文本换行（每行最多15个字符）
        wrapped_text = textwrap.fill(text, width=15)
        lines = wrapped_text.split('\n')
        
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
                # 估算宽度
                text_width = len(line) * (font_size // 2)
            
            x = (width - text_width) // 2
            y = y_start + i * line_height
            
            # 绘制文本阴影（提高可读性）
            draw.text((x+2, y+2), line, font=font, fill=(0, 0, 0, 255))
            # 绘制文本
            draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        
        # 保存图片
        image.save(output_path, 'PNG')
        file_size = output_path.stat().st_size
        print(f"  ✅ 字幕图片创建成功: {output_path.name} ({file_size} 字节)")
        
        # 验证图片
        verify_subtitle_image(output_path)
        return True
        
    except Exception as e:
        print(f"  ❌ 创建失败: {e}")
        return False

def verify_subtitle_image(image_path):
    """验证字幕图片是否包含文字"""
    print(f"  验证字幕图片: {image_path.name}")
    
    # 检查文件大小
    file_size = image_path.stat().st_size
    print(f"    文件大小: {file_size} 字节")
    
    if file_size < 1000:
        print(f"    ⚠️  警告: 文件大小太小，可能没有文字内容")
    
    # 使用ImageMagick检查图片信息
    try:
        cmd = ["identify", "-verbose", str(image_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if "Colorspace: Gray" in result.stdout:
            print(f"    ⚠️  警告: 图片为灰度图")
        elif "Colorspace: sRGB" in result.stdout:
            print(f"    ✅ 图片为彩色图")
        
        # 检查平均像素值
        cmd = ["convert", str(image_path), "-format", "%[fx:mean]", "info:"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.stdout.strip():
            mean_value = float(result.stdout.strip())
            print(f"    平均像素值: {mean_value:.3f}")
            if mean_value < 0.1:
                print(f"    ⚠️  警告: 图片非常暗，可能只有背景没有文字")
            elif mean_value > 0.9:
                print(f"    ⚠️  警告: 图片非常亮，可能只有白色背景")
            else:
                print(f"    ✅ 图片有合理的像素分布")
    except:
        print(f"    ⚠️  无法验证图片")

# ==================== 图片处理函数 ====================
def resize_background_image(input_path, output_path):
    """调整背景图片尺寸"""
    print(f"调整背景图片: {input_path.name} -> {output_path.name}")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vf", "scale=1080:1440:force_original_aspect_ratio=disable,pad=1080:1440:(ow-iw)/2:(oh-ih)/2:color=black",
        "-q:v", "2",
        str(output_path)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        file_size = output_path.stat().st_size
        print(f"  ✅ 调整成功: {file_size} 字节")
        return True
    except Exception as e:
        print(f"  ❌ 调整失败: {e}")
        return False

def merge_images(background_path, subtitle_path, output_path):
    """合并背景和字幕图片"""
    print(f"合并图片: {background_path.name} + {subtitle_path.name}")
    
    # 方法1: 使用FFmpeg合并
    cmd = [
        "ffmpeg", "-y",
        "-i", str(background_path),
        "-i", str(subtitle_path),
        "-filter_complex", "[0:v][1:v]overlay=0:1240",
        str(output_path)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        file_size = output_path.stat().st_size
        print(f"  ✅ FFmpeg合并成功: {file_size} 字节")
        
        # 验证合并后的图片
        verify_merged_image(output_path)
        return True
    except Exception as e:
        print(f"  ❌ FFmpeg合并失败: {e}")
        
        # 方法2: 使用ImageMagick合并
        try:
            cmd = [
                "convert",
                str(background_path),
                str(subtitle_path),
                "-geometry", "+0+1240",
                "-composite",
                str(output_path)
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            file_size = output_path.stat().st_size
            print(f"  ✅ ImageMagick合并成功: {file_size} 字节")
            return True
        except Exception as e2:
            print(f"  ❌ ImageMagick合并失败: {e2}")
            return False

def verify_merged_image(image_path):
    """验证合并后的图片"""
    print(f"  验证合并图片: {image_path.name}")
    
    file_size = image_path.stat().st_size
    print(f"    文件大小: {file_size} 字节")
    
    if file_size < 50000:
        print(f"    ⚠️  警告: 合并图片文件大小太小")

# ==================== 视频创建函数 ====================
def create_video_segment(image_path, audio_path, output_path):
    """创建视频片段"""
    print(f"创建视频片段: {image_path.name} + {audio_path.name}")
    
    # 获取音频时长
    duration = get_duration(audio_path)
    if duration == 0:
        duration = 4.0
    
    print(f"  音频时长: {duration:.2f}秒")
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(image_path),
        "-i", str(audio_path),
        "-c:v", "libx264",
        "-t", str(duration),
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        str(output_path)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        file_size = output_path.stat().st_size
        print(f"  ✅ 视频片段创建成功: {file_size} 字节")
        return True
    except Exception as e:
        print(f"  ❌ 视频片段创建失败: {e}")
        return False

def merge_video_segments(segment_files, output_path):
    """合并视频片段"""
    print(f"合并 {len(segment_files)} 个视频片段...")
    
    # 创建合并列表文件
    concat_file = OUTPUT_DIR / "final_concat.txt"
    with open(concat_file, 'w') as f:
        for segment in segment_files:
            f.write(f"file '{segment.absolute()}'\n")
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(output_path)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        file_size = output_path.stat().st_size
        print(f"✅ 视频合并成功: {output_path.name} ({file_size} 字节)")
        
        # 清理临时文件
        concat_file.unlink()
        return True
    except Exception as e:
        print(f"❌ 视频合并失败: {e}")
        return False

# ==================== 邮件发送函数 ====================
def send_video_email(video_path, subject, body):
    """发送视频邮件"""
    print(f"发送视频邮件: {video_path.name}")
    
    if not video_path.exists():
        print(f"错误: 视频文件不存在")
        return False
    
    # 创建邮件
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # 添加视频附件
    try:
        with open(video_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="{video_path.name}"'
        )
        msg.attach(part)
        print(f"  已添加视频附件: {video_path.name}")
    except Exception as e:
        print(f"  添加附件失败: {e}")
        return False
    
    # 发送邮件
    try:
        if SMTP_CONFIG["use_ssl"]:
            server = smtplib.SMTP_SSL(SMTP_CONFIG["host"], SMTP_CONFIG["port"])
        else:
            server = smtplib.SMTP(SMTP_CONFIG["host"], SMTP_CONFIG["port"])
            server.starttls()
        
        server.login(SMTP_CONFIG["username"], SMTP_CONFIG["password"])
        server.send_message(msg)
        server.quit()
        
        print(f"✅ 邮件发送成功")
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False

# ==================== 主工作流程 ====================
def main_workflow():
    """主工作流程"""
    print("=" * 60)
    print("惊蛰视频完整工作流程")
    print("=" * 60)
    
    # 1. 检查音频文件
    print("\n1. 检查音频文件...")
    audio_files = []
    for i in range(1, 6):
        audio_file = AUDIO_DIR / f"jingzhe_{i}.mp3"
        if not audio_file.exists():
            audio_file = AUDIO_DIR / f"jingzhe_sentence_{i}.mp3"
        
        if audio_file.exists():
            audio_files.append(audio_file)
            print(f"  找到音频文件 {i}: {audio_file.name}")
        else:
            print(f"  ❌ 未找到音频文件 {i}")
            return None
    
    if len(audio_files) < 5:
        print(f"错误: 需要5个音频文件，只找到 {len(audio_files)} 个")
        return None
    
    # 2. 检查图片文件
    print("\n2. 检查图片文件...")
    image_files = list(IMAGE_DIR.glob("*"))
    if len(image_files) < 5:
        print(f"错误: 需要5张图片，只找到 {len(image_files)} 张")
        return None
    
    for i, img_file in enumerate(image_files[:5], 1):
        print(f"  找到图片 {i}: {img_file.name}")
    
    # 3. 创建字幕图片
    print("\n3. 创建字幕图片...")
    subtitle_files = []
    for i, text in enumerate(SUBTITLES, 1):
        subtitle_file = OUTPUT_DIR / f"workflow_subtitle_{i}.png"
        if create_subtitle_with_pil(text, subtitle_file):
            subtitle_files.append(subtitle_file)
        else:
            print(f"  ❌ 字幕图片 {i} 创建失败")
            return None
    
    # 4. 调整背景图片尺寸
    print("\n4. 调整背景图片尺寸...")
    background_files = []
    for i, img_file in enumerate(image_files[:5], 1):
        background_file = OUTPUT_DIR / f"workflow_bg_{i}.jpg"
        if resize_background_image(img_file, background_file):
            background_files.append(background_file)
        else:
            print(f"  ❌ 背景图片 {i} 调整失败")
            return None
    
    # 5. 合并背景和字幕图片
    print("\n5. 合并背景和字幕图片...")
    final_images = []
    for i in range(5):
        final_image = OUTPUT_DIR / f"workflow_final_{i+1}.jpg"
        if merge_images(background_files[i], subtitle_files[i], final_image):
            final_images.append(final_image)
        else:
            print(f"  ❌ 图片合并 {i+1} 失败")
            return None
    
    # 6. 创建视频片段
    print("\n6. 创建视频片段...")
    segment_files = []
    for i in range(5):
        segment_file = OUTPUT_DIR / f"workflow_segment_{i+1}.mp4"
        if create_video_segment(final_images[i], audio_files[i], segment_file):
            segment_files.append(segment_file)
        else:
            print(f"  ❌ 视频片段 {i+1} 创建失败")
            return None
    
    # 7. 合并视频片段
    print("\n7. 合并视频片段...")
    final_video = OUTPUT_DIR / "jingzhe_workflow_final.mp4"
    if not merge_video_segments(segment_files, final_video):
        print("  ❌ 视频合并失败")
        return None
    
    # 8. 验证最终视频
    print("\n8. 验证最终视频...")
    duration = get_duration(final_video)
    file_size = final_video.stat().st_size
    
    print(f"  最终视频: {final_video.name}")
    print(f"  文件大小: {file_size} 字节")
    print(f"  视频时长: {duration:.2f}秒")
    
    # 9. 发送邮件
    print("\n9. 发送邮件...")
    subject = "惊蛰视频工作流程测试版 - 完整脚本"
    body = f"""惊蛰视频工作流程测试版已完成！

这是一个完整的Python脚本，包含了所有视频创建步骤：
1. 创建字幕图片（使用PIL）
2. 调整背景图片尺寸
3. 合并背景和字幕图片
4. 创建视频片段
5. 合并视频片段

视频规格：
- 时长: {duration:.2f}秒
- 大小: {file_size} 字节
- 字幕: PIL创建的图片字幕

请检查视频字幕显示情况。

GitHub链接: https://github.com/sjf2525/openclaw/blob/main/chinese-culture-videos/jingzhe/output/{final_video.name}
"""
    
    if send_video_email(final_video, subject, body):
        print("✅ 邮件发送成功")
    else:
        print("⚠️  邮件发送失败，但视频已创建")
    
    return final_video

# ==================== 诊断函数 ====================
def diagnose_subtitle_issue():
    """诊断字幕显示问题"""
    print("=" * 60)
    print("字幕问题诊断")
    print("=" * 60)
    
    print("\n可能的问题原因:")
    print("1. 字幕图片创建失败（PIL无法渲染中文字体）")
    print("2. 字幕图片叠加失败（FFmpeg/ImageMagick问题）")
    print("3. 字幕图片透明度问题（RGBA vs RGB）")
    print("4. 字幕图片位置错误（y坐标计算错误）")
    print("5. 字幕图片尺寸不匹配")
    
    print("\n诊断步骤:")
    
    # 检查PIL安装
    print("1. 检查PIL安装...")
    try:
        from PIL import Image, ImageDraw, ImageFont
        print("  ✅ PIL已安装")
    except:
        print("  ❌ PIL未安装")
    
    # 检查字体
    print("2. 检查系统字体...")
    font_path = find_font()
    if font_path:
        print(f"  ✅ 找到字体: {font_path}")
    else:
        print("  ❌ 未找到系统字体")
    
    # 创建测试字幕图片
    print("3. 创建测试字幕图片...")
    test_subtitle = OUTPUT_DIR / "diagnose_subtitle.png"
    if create_subtitle_with_pil("测试字幕：惊蛰节气", test_subtitle):
        print("  ✅ 测试字幕图片创建成功")
    else:
        print("  ❌ 测试字幕图片创建失败")
    
    # 检查ImageMagick
    print("4. 检查ImageMagick...")
    try:
        subprocess.run(["convert", "--version"], capture_output=True, check=True)
        print("  ✅ ImageMagick已安装")
    except:
        print("  ❌ ImageMagick未安装")
    
    print("\n建议的解决方案:")
    print("1. 检查字幕图片文件大小（应大于1KB）")
    print("2. 检查字幕图片是否为彩色图（不应是灰度图）")
    print("3. 检查字幕图片是否包含文字内容")
    print("4. 检查合并后的图片是否包含字幕")
    print("5. 手动验证每个步骤的输出文件")

# ==================== 主函数 ====================
def main():
    """主函数"""
    print("惊蛰视频完整工作流程脚本")
    print("=" * 60)
    
    print("选项:")
    print("1. 运行完整工作流程")
    print("2. 诊断字幕问题")
    print("3. 清理输出文件")
    
    choice = input("\n请选择 (1/2/3): ").strip()
    
    if choice == "1":
        print("\n运行完整工作流程...")
        video_file = main_workflow()
        
        if video_file:
            print("\n" + "=" * 60)
            print("✅ 工作流程完成！")
            print("=" * 60)
            print(f"\n最终视频: {video_file}")
            print(f"GitHub链接: https://github.com/sjf2525/openclaw/blob/main/chinese-culture-videos/jingzhe/output/{video_file.name}")
        else:
            print("\n❌ 工作流程失败")
    
    elif choice == "2":
        diagnose_subtitle_issue()
    
    elif choice == "3":
        print("\n清理输出文件...")
        for file in OUTPUT_DIR.glob("*"):
            if file.name not in ["jingzhe_pil_final.mp4", "jingzhe_imagemagick_final.mp4", "jingzhe_segmented_merged.mp4"]:
                try:
                    file.unlink()
                    print(f"  删除: {file.name}")
                except:
                    pass
        print("✅ 清理完成")
    
    else:
        print("无效选择")

if __name__ == "__main__":
    main()