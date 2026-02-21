#!/bin/bash
# 创建完美的惊蛰视频：图片轮播 + 硬编码字幕

echo "创建完美的惊蛰视频..."
echo "========================================"

cd "$(dirname "$0")"
OUTPUT_DIR="output"
mkdir -p "$OUTPUT_DIR"

AUDIO_FILE="audio/jingzhe_full_new.mp3"
if [ ! -f "$AUDIO_FILE" ]; then
    echo "错误: 音频文件不存在: $AUDIO_FILE"
    exit 1
fi

# 获取音频时长
AUDIO_DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$AUDIO_FILE")
echo "音频时长: $AUDIO_DURATION 秒"

# 获取图片文件
IMAGES=()
for img in images/*.jpg images/*.png images/*.webp; do
    if [ -f "$img" ]; then
        IMAGES+=("$img")
    fi
done

if [ ${#IMAGES[@]} -eq 0 ]; then
    echo "错误: 没有找到图片文件"
    exit 1
fi

echo "找到 ${#IMAGES[@]} 张图片"

# 调整图片尺寸
echo "调整图片尺寸..."
RESIZED_IMAGES=()
for i in "${!IMAGES[@]}"; do
    INPUT_IMG="${IMAGES[$i]}"
    OUTPUT_IMG="$OUTPUT_DIR/resized_$((i+1)).jpg"
    
    ffmpeg -y -i "$INPUT_IMG" \
        -vf "scale=1080:1440:force_original_aspect_ratio=disable,pad=1080:1440:(ow-iw)/2:(oh-ih)/2:color=black" \
        -q:v 2 \
        "$OUTPUT_IMG" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        RESIZED_IMAGES+=("$OUTPUT_IMG")
        echo "调整完成: $(basename "$INPUT_IMG") -> $(basename "$OUTPUT_IMG")"
    fi
done

if [ ${#RESIZED_IMAGES[@]} -eq 0 ]; then
    echo "错误: 没有调整后的图片"
    exit 1
fi

# 创建图片列表文件
echo "创建图片列表..."
CONCAT_FILE="$OUTPUT_DIR/concat_list.txt"
> "$CONCAT_FILE"

# 每张图片显示时间
IMAGE_COUNT=${#RESIZED_IMAGES[@]}
IMAGE_DURATION=$(echo "$AUDIO_DURATION / $IMAGE_COUNT" | bc -l)

for img in "${RESIZED_IMAGES[@]}"; do
    echo "file '$img'" >> "$CONCAT_FILE"
    echo "duration $IMAGE_DURATION" >> "$CONCAT_FILE"
done

# 创建无声视频
echo "创建无声视频..."
SILENT_VIDEO="$OUTPUT_DIR/silent_video.mp4"
ffmpeg -y -f concat -safe 0 -i "$CONCAT_FILE" \
    -c:v libx264 -pix_fmt yuv420p -vf "fps=30" -r 30 \
    "$SILENT_VIDEO" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "错误: 创建无声视频失败"
    exit 1
fi

# 添加音频
echo "添加音频..."
VIDEO_WITH_AUDIO="$OUTPUT_DIR/video_with_audio.mp4"
ffmpeg -y -i "$SILENT_VIDEO" -i "$AUDIO_FILE" \
    -c:v copy -c:a aac \
    "$VIDEO_WITH_AUDIO" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "错误: 添加音频失败"
    exit 1
fi

# 创建硬编码字幕视频
echo "创建硬编码字幕视频..."
FINAL_VIDEO="$OUTPUT_DIR/jingzhe_perfect_final.mp4"

# 字幕内容
SENTENCES=(
    "惊蛰，是二十四节气中的第三个节气。"
    "春雷始鸣，惊醒蛰伏于地下越冬的昆虫。"
    "此时气温回升，雨水增多，万物开始复苏。"
    "农民开始春耕，桃花红、李花白，黄莺鸣叫、燕子飞来。"
    "惊蛰吃梨，寓意远离疾病，开启健康一年。"
)

# 构建drawtext滤镜
DRAWTEXT_FILTER=""
SENTENCE_COUNT=${#SENTENCES[@]}
SENTENCE_DURATION=$(echo "$AUDIO_DURATION / $SENTENCE_COUNT" | bc -l)

for i in "${!SENTENCES[@]}"; do
    START_TIME=$(echo "$i * $SENTENCE_DURATION" | bc -l)
    END_TIME=$(echo "($i + 1) * $SENTENCE_DURATION" | bc -l)
    
    if [ $i -eq 0 ]; then
        DRAWTEXT_FILTER="drawtext=text='${SENTENCES[$i]}':fontsize=48:fontcolor=white:box=1:boxcolor=black@0.7:boxborderw=10:x=(w-text_w)/2:y=h-150:enable='between(t,$START_TIME,$END_TIME)'"
    else
        DRAWTEXT_FILTER="$DRAWTEXT_FILTER,drawtext=text='${SENTENCES[$i]}':fontsize=48:fontcolor=white:box=1:boxcolor=black@0.7:boxborderw=10:x=(w-text_w)/2:y=h-150:enable='between(t,$START_TIME,$END_TIME)'"
    fi
done

# 应用字幕
ffmpeg -y -i "$VIDEO_WITH_AUDIO" \
    -vf "$DRAWTEXT_FILTER" \
    -c:a copy \
    "$FINAL_VIDEO" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ 完美视频创建成功: $FINAL_VIDEO"
    
    # 验证结果
    FINAL_DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$FINAL_VIDEO" 2>/dev/null)
    FINAL_SIZE=$(stat -f%z "$FINAL_VIDEO" 2>/dev/null || stat -c%s "$FINAL_VIDEO")
    
    echo ""
    echo "视频信息:"
    echo "  文件: $(basename "$FINAL_VIDEO")"
    echo "  大小: $FINAL_SIZE 字节 ($(echo "$FINAL_SIZE / 1024" | bc) KB)"
    echo "  时长: $FINAL_DURATION 秒"
    echo "  分辨率: 1080×1440"
    echo "  图片数量: $IMAGE_COUNT 张"
    echo "  字幕: 硬编码，无字体依赖"
    
    echo ""
    echo "时间轴:"
    for i in "${!SENTENCES[@]}"; do
        START_TIME=$(echo "$i * $SENTENCE_DURATION" | bc -l | xargs printf "%.2f")
        END_TIME=$(echo "($i + 1) * $SENTENCE_DURATION" | bc -l | xargs printf "%.2f")
        echo "  $START_TIME-$END_TIME秒: ${SENTENCES[$i]:0:20}..."
    done
    
    # 清理临时文件
    rm -f "$SILENT_VIDEO" "$VIDEO_WITH_AUDIO" "$CONCAT_FILE"
    
else
    echo "❌ 添加字幕失败"
    echo "使用无字幕版本: $VIDEO_WITH_AUDIO"
    cp "$VIDEO_WITH_AUDIO" "$FINAL_VIDEO"
fi

echo ""
echo "========================================"
echo "完成！"
echo "========================================"
echo "最终视频: $FINAL_VIDEO"
echo "GitHub链接: https://github.com/sjf2525/openclaw/blob/main/chinese-culture-videos/jingzhe/output/$(basename "$FINAL_VIDEO")"