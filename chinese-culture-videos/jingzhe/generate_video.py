#!/usr/bin/env python3
"""
惊蛰节气视频生成脚本
使用OpenClaw TTS生成配音，FFmpeg合成视频
"""

import os
import subprocess
import json
from pathlib import Path

# 项目路径
PROJECT_DIR = Path(__file__).parent
AUDIO_DIR = PROJECT_DIR / "audio"
IMAGE_DIR = PROJECT_DIR / "images"
OUTPUT_DIR = PROJECT_DIR / "output"

# 创建目录
for dir_path in [AUDIO_DIR, IMAGE_DIR, OUTPUT_DIR]:
    dir_path.mkdir(exist_ok=True)

def generate_tts_audio(text, output_file, voice="zh-CN"):
    """
    使用OpenClaw TTS生成音频
    注意：这里需要调用OpenClaw的tts工具
    """
    print(f"生成TTS音频: {output_file}")
    
    # 这里应该调用OpenClaw的tts工具
    # 由于在OpenClaw环境中，我们可以通过其他方式调用
    # 暂时先创建一个占位函数
    
    # 保存文本文件，后续手动处理
    text_file = output_file.with_suffix('.txt')
    text_file.write_text(text)
    
    print(f"已保存文本到: {text_file}")
    print("提示：请使用OpenClaw的tts工具生成音频")
    print(f"命令示例: openclaw tts --text '{text[:50]}...' --channel webchat")
    
    return False  # 表示需要手动处理

def download_images():
    """下载惊蛰相关图片"""
    print("下载惊蛰相关图片...")
    
    # 图片搜索关键词
    keywords = [
        "惊蛰 节气 春雷",
        "春天 昆虫 土壤",
        "春雨 滋润 大地",
        "桃花 李花 绽放",
        "农民 春耕 农业",
        "燕子 黄莺 鸟类",
        "梨子 水果 特写",
        "家庭 温馨 分享"
    ]
    
    print("图片关键词:")
    for kw in keywords:
        print(f"  - {kw}")
    
    print("\n提示：请使用tavily_search工具获取图片")
    print("或从免费图库网站下载相关图片到 images/ 目录")
    
    return False

def create_video():
    """使用FFmpeg创建视频"""
    print("创建视频...")
    
    # 检查必要的文件
    audio_files = list(AUDIO_DIR.glob("*.mp3")) + list(AUDIO_DIR.glob("*.wav"))
    image_files = list(IMAGE_DIR.glob("*.jpg")) + list(IMAGE_DIR.glob("*.png"))
    
    if not audio_files:
        print("错误：未找到音频文件，请先生成TTS音频")
        return False
    
    if not image_files:
        print("错误：未找到图片文件，请先下载图片")
        return False
    
    print(f"找到 {len(audio_files)} 个音频文件")
    print(f"找到 {len(image_files)} 个图片文件")
    
    # 简单的FFmpeg命令示例
    output_video = OUTPUT_DIR / "jingzhe_video.mp4"
    
    # 这里只是一个示例命令，实际需要根据素材调整
    cmd = [
        "ffmpeg",
        "-y",  # 覆盖输出文件
        "-loop", "1",  # 循环图片
        "-i", str(image_files[0]),  # 使用第一张图片
        "-i", str(audio_files[0]),  # 使用第一个音频
        "-c:v", "libx264",  # 视频编码
        "-tune", "stillimage",  # 静态图片优化
        "-c:a", "aac",  # 音频编码
        "-b:a", "192k",  # 音频比特率
        "-pix_fmt", "yuv420p",  # 像素格式
        "-shortest",  # 以音频时长为准
        str(output_video)
    ]
    
    print(f"\nFFmpeg命令示例:")
    print(" ".join(cmd))
    
    try:
        # 实际执行FFmpeg命令
        # subprocess.run(cmd, check=True)
        print(f"视频将保存到: {output_video}")
        print("提示：取消注释上面的subprocess.run()来实际执行")
        return True
    except Exception as e:
        print(f"FFmpeg错误: {e}")
        return False

def generate_subtitles():
    """生成字幕文件"""
    print("生成字幕...")
    
    # 读取脚本
    script_file = PROJECT_DIR / "script.md"
    if not script_file.exists():
        print("错误：未找到脚本文件")
        return False
    
    script_content = script_file.read_text()
    
    # 提取文字脚本部分（简化处理）
    lines = []
    for line in script_content.split('\n'):
        if '配音：' in line:
            text = line.split('配音：')[1].strip().strip('"')
            lines.append(text)
    
    # 生成SRT字幕格式
    srt_content = ""
    for i, line in enumerate(lines, 1):
        # 简单的时间分配，每句3-4秒
        start_time = (i-1) * 3
        end_time = i * 3
        
        srt_content += f"{i}\n"
        srt_content += f"00:00:{start_time:02d},000 --> 00:00:{end_time:02d},000\n"
        srt_content += f"{line}\n\n"
    
    srt_file = OUTPUT_DIR / "subtitles.srt"
    srt_file.write_text(srt_content)
    print(f"字幕文件已保存: {srt_file}")
    
    return True

def main():
    """主函数"""
    print("=" * 50)
    print("惊蛰节气视频生成脚本")
    print("=" * 50)
    
    # 1. 生成TTS音频
    print("\n1. 生成TTS音频")
    script_text = """
    惊蛰，是二十四节气中的第三个节气。
    春雷始鸣，惊醒蛰伏于地下越冬的昆虫。
    此时气温回升，雨水增多，万物开始复苏。
    农民开始春耕，桃花红、李花白，黄莺鸣叫、燕子飞来。
    惊蛰吃梨，寓意远离疾病，开启健康一年。
    """
    
    audio_file = AUDIO_DIR / "jingzhe_audio.mp3"
    generate_tts_audio(script_text, audio_file)
    
    # 2. 下载图片
    print("\n2. 下载图片素材")
    download_images()
    
    # 3. 生成字幕
    print("\n3. 生成字幕")
    generate_subtitles()
    
    # 4. 创建视频
    print("\n4. 创建视频")
    create_video()
    
    print("\n" + "=" * 50)
    print("完成！")
    print("=" * 50)
    print("\n下一步操作：")
    print("1. 使用OpenClaw的tts工具生成音频")
    print("2. 使用tavily_search获取图片素材")
    print("3. 运行FFmpeg命令合成视频")
    print(f"4. 查看输出文件: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()