#!/usr/bin/env python3
"""
创建惊蛰视频字幕文件
"""

from pathlib import Path

# 项目路径
PROJECT_DIR = Path(__file__).parent
OUTPUT_DIR = PROJECT_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# 惊蛰脚本和对应时间（估算）
subtitles = [
    {
        "text": "惊蛰，是二十四节气中的第三个节气。",
        "start": "00:00:00,000",
        "end": "00:00:03,500"
    },
    {
        "text": "春雷始鸣，惊醒蛰伏于地下越冬的昆虫。",
        "start": "00:00:03,500",
        "end": "00:00:07,000"
    },
    {
        "text": "此时气温回升，雨水增多，万物开始复苏。",
        "start": "00:00:07,000",
        "end": "00:00:10,500"
    },
    {
        "text": "农民开始春耕，桃花红、李花白，黄莺鸣叫、燕子飞来。",
        "start": "00:00:10,500",
        "end": "00:00:14,500"
    },
    {
        "text": "惊蛰吃梨，寓意远离疾病，开启健康一年。",
        "start": "00:00:14,500",
        "end": "00:00:18,000"
    }
]

def create_srt_file():
    """创建SRT字幕文件"""
    print("创建SRT字幕文件...")
    
    srt_content = ""
    
    for i, subtitle in enumerate(subtitles, 1):
        srt_content += f"{i}\n"
        srt_content += f"{subtitle['start']} --> {subtitle['end']}\n"
        srt_content += f"{subtitle['text']}\n\n"
    
    srt_file = OUTPUT_DIR / "jingzhe_subtitles.srt"
    srt_file.write_text(srt_content, encoding='utf-8')
    
    print(f"SRT字幕文件已保存: {srt_file}")
    print(f"文件大小: {srt_file.stat().st_size} 字节")
    
    return srt_file

def create_ass_file():
    """创建ASS字幕文件（更丰富的格式）"""
    print("\n创建ASS字幕文件...")
    
    ass_content = """[Script Info]
ScriptType: v4.00+
Collisions: Normal
PlayDepth: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Microsoft YaHei,36,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,1,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    for subtitle in subtitles:
        # 转换时间格式: 00:00:00,000 -> 0:00:00.00
        start_time = subtitle['start'].replace(',', '.')
        end_time = subtitle['end'].replace(',', '.')
        
        ass_content += f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{subtitle['text']}\n"
    
    ass_file = OUTPUT_DIR / "jingzhe_subtitles.ass"
    ass_file.write_text(ass_content, encoding='utf-8')
    
    print(f"ASS字幕文件已保存: {ass_file}")
    print(f"文件大小: {ass_file.stat().st_size} 字节")
    
    return ass_file

def create_burn_subtitles_script():
    """创建烧录字幕的FFmpeg脚本"""
    print("\n创建烧录字幕脚本...")
    
    script_content = """#!/bin/bash
# 烧录字幕到视频的FFmpeg脚本

INPUT_VIDEO="output/jingzhe_video.mp4"
INPUT_SUBTITLES="output/jingzhe_subtitles.ass"
OUTPUT_VIDEO="output/jingzhe_video_with_subtitles.mp4"

echo "烧录字幕到视频..."

# 检查输入文件
if [ ! -f "$INPUT_VIDEO" ]; then
    echo "错误: 未找到输入视频 $INPUT_VIDEO"
    exit 1
fi

if [ ! -f "$INPUT_SUBTITLES" ]; then
    echo "错误: 未找到字幕文件 $INPUT_SUBTITLES"
    exit 1
fi

# 烧录字幕
ffmpeg -i "$INPUT_VIDEO" -vf "ass=$INPUT_SUBTITLES" -c:a copy "$OUTPUT_VIDEO"

if [ $? -eq 0 ]; then
    echo "成功: 字幕已烧录到 $OUTPUT_VIDEO"
    echo "文件信息:"
    ffmpeg -i "$OUTPUT_VIDEO" 2>&1 | grep -E "Duration|Stream"
else
    echo "失败: 烧录字幕失败"
fi
"""
    
    script_file = OUTPUT_DIR / "burn_subtitles.sh"
    script_file.write_text(script_content)
    script_file.chmod(0o755)
    
    print(f"烧录脚本已保存: {script_file}")
    print(f"运行命令: bash {script_file}")

def main():
    """主函数"""
    print("=" * 50)
    print("创建惊蛰视频字幕文件")
    print("=" * 50)
    
    # 创建SRT字幕
    srt_file = create_srt_file()
    
    # 创建ASS字幕
    ass_file = create_ass_file()
    
    # 创建烧录脚本
    create_burn_subtitles_script()
    
    print("\n" + "=" * 50)
    print("字幕创建完成！")
    print("=" * 50)
    
    print("\n生成的文件:")
    print(f"1. SRT字幕: {srt_file}")
    print(f"2. ASS字幕: {ass_file}")
    print(f"3. 烧录脚本: output/burn_subtitles.sh")
    
    print("\n字幕预览:")
    for i, subtitle in enumerate(subtitles, 1):
        print(f"{i}. {subtitle['start']} - {subtitle['end']}: {subtitle['text']}")

if __name__ == "__main__":
    main()