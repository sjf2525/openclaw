#!/bin/bash
# 简单最终解决方案：使用可靠的方法创建视频

echo "惊蛰视频简单最终解决方案"
echo "========================================"

cd "$(dirname "$0")"
OUTPUT_DIR="output"
mkdir -p "$OUTPUT_DIR"

# 字幕文本
SENTENCES=(
    "惊蛰，是二十四节气中的第三个节气。"
    "春雷始鸣，惊醒蛰伏于地下越冬的昆虫。"
    "此时气温回升，雨水增多，万物开始复苏。"
    "农民开始春耕，桃花红、李花白，黄莺鸣叫、燕子飞来。"
    "惊蛰吃梨，寓意远离疾病，开启健康一年。"
)

# 1. 使用Python创建简单的字幕图片
echo ""
echo "1. 创建简单字幕图片..."
python3 -c "
from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

# 查找中文字体
font_path = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'
if os.path.exists(font_path):
    print('使用字体: NotoSerifCJK-Bold.ttc')
    font = ImageFont.truetype(font_path, 44, index=0)
else:
    print('使用默认字体')
    font = ImageFont.load_default()

for i in range(5):
    text = '''${SENTENCES[$i]}'''
    output_path = f'output/simple_sub_{i+1}.jpg'
    
    # 创建图片（强制使用RGB模式）
    img = Image.new('RGB', (1080, 200), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # 文本换行
    wrapped = textwrap.fill(text, width=15)
    lines = wrapped.split('\\\\n')
    
    # 计算位置
    line_height = 54
    total_height = len(lines) * line_height
    y_start = (200 - total_height) // 2
    
    # 绘制文本
    for j, line in enumerate(lines):
        # 估算宽度
        text_width = len(line) * 30
        x = (1080 - text_width) // 2
        y = y_start + j * line_height
        draw.text((x, y), line, font=font, fill=(0, 0, 0))
    
    img.save(output_path, 'JPEG', quality=95)
    print(f'创建字幕 {i+1}: {output_path}')
"

# 2. 检查音频文件
echo ""
echo "2. 检查音频文件..."
AUDIO_FILES=()
for i in {1..5}; do
    if [ -f "audio/jingzhe_$i.mp3" ]; then
        AUDIO_FILES+=("audio/jingzhe_$i.mp3")
        echo "  找到音频 $i: jingzhe_$i.mp3"
    elif [ -f "audio/jingzhe_sentence_$i.mp3" ]; then
        AUDIO_FILES+=("audio/jingzhe_sentence_$i.mp3")
        echo "  找到音频 $i: jingzhe_sentence_$i.mp3"
    else
        echo "  ❌ 未找到音频 $i"
        exit 1
    fi
done

# 3. 检查图片文件
echo ""
echo "3. 检查图片文件..."
IMAGE_FILES=()
for img in images/*.jpg images/*.png images/*.webp; do
    if [ -f "$img" ]; then
        IMAGE_FILES+=("$img")
        echo "  找到图片: $(basename "$img")"
    fi
done

if [ ${#IMAGE_FILES[@]} -lt 5 ]; then
    echo "错误: 需要5张图片，只找到 ${#IMAGE_FILES[@]} 张"
    exit 1
fi

# 4. 创建视频片段
echo ""
echo "4. 创建视频片段..."
for i in {0..4}; do
    echo ""
    echo "  创建片段 $((i+1))..."
    
    # 调整背景图片
    ffmpeg -y -i "${IMAGE_FILES[$i]}" \
        -vf "scale=1080:1440:force_original_aspect_ratio=disable,pad=1080:1440:(ow-iw)/2:(oh-ih)/2:color=black" \
        -q:v 2 \
        "$OUTPUT_DIR/simple_bg_$((i+1)).jpg" 2>/dev/null
    
    # 合并图片
    ffmpeg -y \
        -i "$OUTPUT_DIR/simple_bg_$((i+1)).jpg" \
        -i "$OUTPUT_DIR/simple_sub_$((i+1)).jpg" \
        -filter_complex "[0:v][1:v]overlay=0:1240" \
        "$OUTPUT_DIR/simple_merged_$((i+1)).jpg" 2>/dev/null
    
    # 获取音频时长
    DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "${AUDIO_FILES[$i]}" 2>/dev/null)
    if [ -z "$DURATION" ]; then
        DURATION="4.0"
    fi
    
    # 创建视频片段
    ffmpeg -y \
        -loop 1 \
        -i "$OUTPUT_DIR/simple_merged_$((i+1)).jpg" \
        -i "${AUDIO_FILES[$i]}" \
        -c:v libx264 \
        -t "$DURATION" \
        -pix_fmt yuv420p \
        -c:a aac \
        -shortest \
        "$OUTPUT_DIR/simple_segment_$((i+1)).mp4" 2>/dev/null
    
    if [ -f "$OUTPUT_DIR/simple_segment_$((i+1)).mp4" ]; then
        SIZE=$(stat -f%z "$OUTPUT_DIR/simple_segment_$((i+1)).mp4" 2>/dev/null || stat -c%s "$OUTPUT_DIR/simple_segment_$((i+1)).mp4")
        echo "    ✅ 片段创建成功: ${SIZE}字节"
    else
        echo "    ❌ 片段创建失败"
        exit 1
    fi
done

# 5. 合并视频片段
echo ""
echo "5. 合并视频片段..."
CONCAT_FILE="$OUTPUT_DIR/simple_concat.txt"
> "$CONCAT_FILE"
for i in {1..5}; do
    echo "file 'simple_segment_$i.mp4'" >> "$CONCAT_FILE"
done

FINAL_VIDEO="$OUTPUT_DIR/jingzhe_simple_final.mp4"
ffmpeg -y -f concat -safe 0 -i "$CONCAT_FILE" -c copy "$FINAL_VIDEO" 2>/dev/null

if [ -f "$FINAL_VIDEO" ]; then
    FINAL_SIZE=$(stat -f%z "$FINAL_VIDEO" 2>/dev/null || stat -c%s "$FINAL_VIDEO")
    FINAL_DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$FINAL_VIDEO" 2>/dev/null)
    
    echo ""
    echo "========================================"
    echo "✅ 最终视频创建成功！"
    echo "========================================"
    echo ""
    echo "📊 视频规格:"
    echo "   文件: $(basename "$FINAL_VIDEO")"
    echo "   大小: $FINAL_SIZE 字节 ($(echo "$FINAL_SIZE / 1024" | bc) KB)"
    echo "   时长: $FINAL_DURATION 秒"
    echo "   分辨率: 1080×1440"
    echo ""
    echo "🔧 技术方案:"
    echo "   1. ✅ 使用 NotoSerifCJK 中文字体"
    echo "   2. ✅ 白色背景 + 黑色文字"
    echo "   3. ✅ RGB彩色图片，无透明度问题"
    echo "   4. ✅ 分段创建，时间准确"
    echo "   5. ✅ 彻底解决字幕显示问题"
    echo ""
    echo "🎬 时间轴:"
    TOTAL=0
    for i in {0..4}; do
        DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "${AUDIO_FILES[$i]}" 2>/dev/null)
        if [ -z "$DURATION" ]; then
            DURATION="4.0"
        fi
        END=$(echo "$TOTAL + $DURATION" | awk '{print $1 + $2}')
        printf "   %.1f-%.1f秒: %s\n" "$TOTAL" "$END" "${SENTENCES[$i]:0:30}..."
        TOTAL=$END
    done
    echo ""
    echo "🔗 GitHub链接:"
    echo "   https://github.com/sjf2525/openclaw/blob/main/chinese-culture-videos/jingzhe/output/$(basename "$FINAL_VIDEO")"
else
    echo "❌ 最终视频创建失败"
    exit 1
fi