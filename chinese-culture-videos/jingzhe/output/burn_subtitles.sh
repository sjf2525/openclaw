#!/bin/bash
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
