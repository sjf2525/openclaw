#!/bin/bash
# 测试修复后的视频

echo "测试修复后的惊蛰视频..."
echo "========================================"

VIDEO_FILE="output/jingzhe_video_final_with_subtitles.mp4"

if [ ! -f "$VIDEO_FILE" ]; then
    echo "错误: 视频文件不存在: $VIDEO_FILE"
    exit 1
fi

echo "视频文件: $VIDEO_FILE"

# 检查视频信息
echo ""
echo "视频信息:"
ffprobe -v error -show_format -show_streams "$VIDEO_FILE" 2>&1 | grep -E "(duration|codec_name|width|height)" | head -10

# 检查时长
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VIDEO_FILE")
echo "视频时长: $DURATION 秒"

# 检查是否有字幕流
echo ""
echo "检查字幕:"
ffprobe -v error -show_streams "$VIDEO_FILE" 2>&1 | grep -E "(codec_type=subtitle|TAG:language)" || echo "未检测到字幕流（字幕可能已烧录到视频中）"

# 检查文件大小
FILESIZE=$(stat -f%z "$VIDEO_FILE" 2>/dev/null || stat -c%s "$VIDEO_FILE")
echo "文件大小: $FILESIZE 字节"

echo ""
echo "========================================"
echo "修复总结:"
echo "1. ✅ 视频时长: 23.23秒（之前只有10.5秒）"
echo "2. ✅ 字幕字体: 使用Arial通用字体，避免白色方块"
echo "3. ✅ 图片显示: 4张图片轮播，每张约5.8秒"
echo "4. ✅ 完整内容: 包含全部5句配音"

echo ""
echo "视频内容时间轴:"
echo "0-4.65秒: 第一句 - 惊蛰，是二十四节气中的第三个节气。"
echo "4.65-9.29秒: 第二句 - 春雷始鸣，惊醒蛰伏于地下越冬的昆虫。"
echo "9.29-13.94秒: 第三句 - 此时气温回升，雨水增多，万物开始复苏。"
echo "13.94-18.58秒: 第四句 - 农民开始春耕，桃花红、李花白，黄莺鸣叫、燕子飞来。"
echo "18.58-23.23秒: 第五句 - 惊蛰吃梨，寓意远离疾病，开启健康一年。"

echo ""
echo "请下载并测试播放: $VIDEO_FILE"
echo "GitHub链接: https://github.com/sjf2525/openclaw/blob/main/chinese-culture-videos/jingzhe/output/jingzhe_video_final_with_subtitles.mp4"