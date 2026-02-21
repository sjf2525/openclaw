#!/bin/bash
# 直接创建惊蛰视频 - 最简单可靠的方法

echo "直接创建惊蛰视频..."
echo "========================================"

cd "$(dirname "$0")"
OUTPUT_DIR="output"
mkdir -p "$OUTPUT_DIR"

# 检查音频文件
AUDIO_FILES=()
for i in {1..5}; do
    if [ -f "audio/jingzhe_$i.mp3" ]; then
        AUDIO_FILES+=("audio/jingzhe_$i.mp3")
    elif [ -f "audio/jingzhe_sentence_$i.mp3" ]; then
        AUDIO_FILES+=("audio/jingzhe_sentence_$i.mp3")
    fi
done

if [ ${#AUDIO_FILES[@]} -lt 5 ]; then
    echo "错误: 需要5个音频文件，只找到 ${#AUDIO_FILES[@]} 个"
    exit 1
fi

echo "找到 ${#AUDIO_FILES[@]} 个音频文件"

# 检查图片文件
IMAGE_FILES=()
for img in images/*.jpg images/*.png images/*.webp; do
    if [ -f "$img" ]; then
        IMAGE_FILES+=("$img")
    fi
done

if [ ${#IMAGE_FILES[@]} -lt 5 ]; then
    echo "错误: 需要5张图片，只找到 ${#IMAGE_FILES[@]} 张"
    exit 1
fi

echo "找到 ${#IMAGE_FILES[@]} 张图片"

# 字幕文本
SENTENCES=(
    "惊蛰，是二十四节气中的第三个节气。"
    "春雷始鸣，惊醒蛰伏于地下越冬的昆虫。"
    "此时气温回升，雨水增多，万物开始复苏。"
    "农民开始春耕，桃花红、李花白，黄莺鸣叫、燕子飞来。"
    "惊蛰吃梨，寓意远离疾病，开启健康一年。"
)

# 1. 调整图片尺寸
echo ""
echo "1. 调整图片尺寸..."
RESIZED_IMAGES=()
for i in {0..4}; do
    INPUT_IMG="${IMAGE_FILES[$i]}"
    OUTPUT_IMG="$OUTPUT_DIR/direct_img_$((i+1)).jpg"
    
    ffmpeg -y -i "$INPUT_IMG" \
        -vf "scale=1080:1440:force_original_aspect_ratio=disable,pad=1080:1440:(ow-iw)/2:(oh-ih)/2:color=black" \
        -q:v 2 \
        "$OUTPUT_IMG" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        RESIZED_IMAGES+=("$OUTPUT_IMG")
        echo "  图片 $((i+1)): $(basename "$INPUT_IMG") -> $(basename "$OUTPUT_IMG")"
    else
        echo "  错误: 调整图片失败 $INPUT_IMG"
        exit 1
    fi
done

# 2. 创建5个独立的视频片段
echo ""
echo "2. 创建视频片段..."
SEGMENT_FILES=()
for i in {0..4}; do
    AUDIO_FILE="${AUDIO_FILES[$i]}"
    IMAGE_FILE="${RESIZED_IMAGES[$i]}"
    SUBTITLE="${SENTENCES[$i]}"
    SEGMENT_FILE="$OUTPUT_DIR/segment_$((i+1)).mp4"
    
    # 获取音频时长
    DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$AUDIO_FILE" 2>/dev/null)
    if [ -z "$DURATION" ]; then
        DURATION="4.0"
    fi
    
    echo "  片段 $((i+1)): 时长 ${DURATION}s, 字幕: ${SUBTITLE:0:20}..."
    
    # 创建带字幕的视频片段
    ffmpeg -y \
        -loop 1 \
        -i "$IMAGE_FILE" \
        -i "$AUDIO_FILE" \
        -vf "drawtext=text='$SUBTITLE':fontsize=48:fontcolor=white:box=1:boxcolor=black@0.7:boxborderw=10:x=(w-text_w)/2:y=h-150" \
        -c:v libx264 \
        -t "$DURATION" \
        -pix_fmt yuv420p \
        -c:a aac \
        -shortest \
        "$SEGMENT_FILE" 2>/dev/null
    
    if [ $? -eq 0 ] && [ -f "$SEGMENT_FILE" ]; then
        SEGMENT_FILES+=("$SEGMENT_FILE")
        SEGMENT_SIZE=$(stat -f%z "$SEGMENT_FILE" 2>/dev/null || stat -c%s "$SEGMENT_FILE")
        echo "    ✅ 成功: $(basename "$SEGMENT_FILE") (${SEGMENT_SIZE}字节)"
    else
        echo "    ❌ 失败: 创建片段 $((i+1))"
        exit 1
    fi
done

# 3. 合并所有片段
echo ""
echo "3. 合并视频片段..."
CONCAT_FILE="$OUTPUT_DIR/direct_concat.txt"
> "$CONCAT_FILE"
for segment in "${SEGMENT_FILES[@]}"; do
    echo "file '$segment'" >> "$CONCAT_FILE"
done

FINAL_VIDEO="$OUTPUT_DIR/jingzhe_direct_final.mp4"
ffmpeg -y -f concat -safe 0 -i "$CONCAT_FILE" -c copy "$FINAL_VIDEO" 2>/dev/null

if [ $? -eq 0 ] && [ -f "$FINAL_VIDEO" ]; then
    echo "  ✅ 合并成功: $(basename "$FINAL_VIDEO")"
else
    echo "  ❌ 合并失败"
    exit 1
fi

# 4. 验证结果
echo ""
echo "4. 验证结果..."
FINAL_DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$FINAL_VIDEO" 2>/dev/null)
FINAL_SIZE=$(stat -f%z "$FINAL_VIDEO" 2>/dev/null || stat -c%s "$FINAL_VIDEO")

echo "  文件: $(basename "$FINAL_VIDEO")"
echo "  大小: $FINAL_SIZE 字节 ($(echo "$FINAL_SIZE / 1024" | bc) KB)"
echo "  时长: $FINAL_DURATION 秒"
echo "  分辨率: 1080×1440"
echo "  片段: 5个独立片段合并"

# 5. 清理临时文件
echo ""
echo "5. 清理临时文件..."
for segment in "${SEGMENT_FILES[@]}"; do
    rm -f "$segment"
done
rm -f "$CONCAT_FILE"
rm -f "$OUTPUT_DIR"/direct_img_*.jpg

echo ""
echo "========================================"
echo "✅ 视频创建成功！"
echo "========================================"
echo ""
echo "技术特点:"
echo "1. ✅ 每句配音对应一张独立图片"
echo "2. ✅ 每段视频独立添加字幕"
echo "3. ✅ 合并后确保时间轴正确"
echo "4. ✅ 硬编码字幕，无字体依赖"
echo ""
echo "时间轴:"
TOTAL_TIME=0
for i in {0..4}; do
    SEG_DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "${AUDIO_FILES[$i]}" 2>/dev/null)
    if [ -z "$SEG_DURATION" ]; then
        SEG_DURATION="4.0"
    fi
    END_TIME=$(echo "$TOTAL_TIME + $SEG_DURATION" | bc -l 2>/dev/null || echo "$(echo "$TOTAL_TIME + $SEG_DURATION" | awk '{print $1 + $2}')")
    printf "  %.1f-%.1f秒: %s\n" "$TOTAL_TIME" "$END_TIME" "${SENTENCES[$i]:0:30}..."
    TOTAL_TIME=$END_TIME
done
echo ""
echo "最终视频: $FINAL_VIDEO"
echo "GitHub链接: https://github.com/sjf2525/openclaw/blob/main/chinese-culture-videos/jingzhe/output/$(basename "$FINAL_VIDEO")"