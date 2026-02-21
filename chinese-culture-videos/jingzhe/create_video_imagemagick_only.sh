#!/bin/bash
# 使用ImageMagick创建带字幕图片的视频
# 彻底解决字幕白框问题

echo "使用ImageMagick创建带字幕视频..."
echo "========================================"

cd "$(dirname "$0")"
OUTPUT_DIR="output"
mkdir -p "$OUTPUT_DIR"

# 检查ImageMagick
if ! command -v convert &> /dev/null; then
    echo "错误: ImageMagick未安装"
    echo "请安装: sudo apt-get install imagemagick"
    exit 1
fi

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
echo "1. 调整背景图片尺寸..."
for i in {0..4}; do
    INPUT_IMG="${IMAGE_FILES[$i]}"
    OUTPUT_IMG="$OUTPUT_DIR/bg_$((i+1)).jpg"
    
    ffmpeg -y -i "$INPUT_IMG" \
        -vf "scale=1080:1440:force_original_aspect_ratio=disable,pad=1080:1440:(ow-iw)/2:(oh-ih)/2:color=black" \
        -q:v 2 \
        "$OUTPUT_IMG" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "  背景图片 $((i+1)): $(basename "$INPUT_IMG")"
    else
        echo "  错误: 调整背景图片失败"
        exit 1
    fi
done

# 2. 创建字幕图片
echo ""
echo "2. 创建字幕图片..."
for i in {0..4}; do
    SUBTITLE="${SENTENCES[$i]}"
    SUBTITLE_IMG="$OUTPUT_DIR/subtitle_$((i+1)).png"
    
    # 使用ImageMagick创建字幕图片
    convert -size 1080x200 \
        xc:'rgba(0,0,0,0.7)' \
        -font "DejaVu-Sans" \
        -pointsize 40 \
        -fill white \
        -gravity center \
        -stroke black \
        -strokewidth 2 \
        -annotate +0+0 "$SUBTITLE" \
        "$SUBTITLE_IMG" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "  字幕图片 $((i+1)): ${SUBTITLE:0:20}..."
    else
        echo "  警告: 创建字幕图片失败，尝试备用字体..."
        # 尝试使用Arial字体
        convert -size 1080x200 \
            xc:'rgba(0,0,0,0.7)' \
            -font "Arial" \
            -pointsize 40 \
            -fill white \
            -gravity center \
            -annotate +0+0 "$SUBTITLE" \
            "$SUBTITLE_IMG" 2>/dev/null
        
        if [ $? -ne 0 ]; then
            echo "  错误: 创建字幕图片完全失败"
            exit 1
        fi
    fi
done

# 3. 合并背景和字幕图片
echo ""
echo "3. 合并背景和字幕图片..."
for i in {0..4}; do
    BG_IMG="$OUTPUT_DIR/bg_$((i+1)).jpg"
    SUB_IMG="$OUTPUT_DIR/subtitle_$((i+1)).png"
    FINAL_IMG="$OUTPUT_DIR/final_with_sub_$((i+1)).jpg"
    
    # 使用ImageMagick合并
    convert "$BG_IMG" "$SUB_IMG" \
        -geometry +0+1240 \
        -composite \
        "$FINAL_IMG" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "  合并图片 $((i+1)) 成功"
    else
        echo "  警告: ImageMagick合并失败，尝试FFmpeg..."
        # 使用FFmpeg合并
        ffmpeg -y \
            -i "$BG_IMG" \
            -i "$SUB_IMG" \
            -filter_complex "[0:v][1:v]overlay=0:1240" \
            "$FINAL_IMG" 2>/dev/null
        
        if [ $? -ne 0 ]; then
            echo "  错误: 合并图片完全失败"
            exit 1
        fi
    fi
done

# 4. 创建视频片段
echo ""
echo "4. 创建视频片段..."
SEGMENT_FILES=()
for i in {0..4}; do
    AUDIO_FILE="${AUDIO_FILES[$i]}"
    IMAGE_FILE="$OUTPUT_DIR/final_with_sub_$((i+1)).jpg"
    SEGMENT_FILE="$OUTPUT_DIR/im_segment_$((i+1)).mp4"
    
    # 获取音频时长
    DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$AUDIO_FILE" 2>/dev/null)
    if [ -z "$DURATION" ]; then
        DURATION="4.0"
    fi
    
    echo "  片段 $((i+1)): 图片+字幕，音频 ${DURATION}s"
    
    # 创建视频片段（无额外字幕，字幕已经在图片中）
    ffmpeg -y \
        -loop 1 \
        -i "$IMAGE_FILE" \
        -i "$AUDIO_FILE" \
        -c:v libx264 \
        -t "$DURATION" \
        -pix_fmt yuv420p \
        -c:a aac \
        -shortest \
        "$SEGMENT_FILE" 2>/dev/null
    
    if [ $? -eq 0 ] && [ -f "$SEGMENT_FILE" ]; then
        SEGMENT_FILES+=("$SEGMENT_FILE")
        SEGMENT_SIZE=$(stat -f%z "$SEGMENT_FILE" 2>/dev/null || stat -c%s "$SEGMENT_FILE")
        echo "    ✅ 成功: $(basename "$SEGMENT_FILE")"
    else
        echo "    ❌ 失败: 创建片段 $((i+1))"
        exit 1
    fi
done

# 5. 合并视频片段
echo ""
echo "5. 合并视频片段..."
CONCAT_FILE="$OUTPUT_DIR/im_concat.txt"
> "$CONCAT_FILE"
for segment in "${SEGMENT_FILES[@]}"; do
    echo "file '$segment'" >> "$CONCAT_FILE"
done

FINAL_VIDEO="$OUTPUT_DIR/jingzhe_imagemagick_final.mp4"
ffmpeg -y -f concat -safe 0 -i "$CONCAT_FILE" -c copy "$FINAL_VIDEO" 2>/dev/null

if [ $? -eq 0 ] && [ -f "$FINAL_VIDEO" ]; then
    echo "  ✅ 合并成功: $(basename "$FINAL_VIDEO")"
else
    echo "  ❌ 合并失败"
    exit 1
fi

# 6. 验证结果
echo ""
echo "6. 验证结果..."
FINAL_DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$FINAL_VIDEO" 2>/dev/null)
FINAL_SIZE=$(stat -f%z "$FINAL_VIDEO" 2>/dev/null || stat -c%s "$FINAL_VIDEO")
RESOLUTION=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$FINAL_VIDEO" 2>/dev/null)

echo "  文件: $(basename "$FINAL_VIDEO")"
echo "  大小: $FINAL_SIZE 字节"
echo "  时长: $FINAL_DURATION 秒"
echo "  分辨率: $RESOLUTION"

# 7. 清理临时文件
echo ""
echo "7. 清理临时文件..."
rm -f "$OUTPUT_DIR"/bg_*.jpg
rm -f "$OUTPUT_DIR"/subtitle_*.png
rm -f "$OUTPUT_DIR"/final_with_sub_*.jpg
rm -f "$OUTPUT_DIR"/im_segment_*.mp4
rm -f "$CONCAT_FILE"

echo ""
echo "========================================"
echo "✅ 视频创建成功！"
echo "========================================"
echo ""
echo "技术特点:"
echo "1. ✅ 使用ImageMagick创建字幕图片"
echo "2. ✅ 字幕为图片格式，彻底解决白框问题"
echo "3. ✅ 字幕图片叠加到背景图片上"
echo "4. ✅ 使用带字幕的图片创建视频"
echo "5. ✅ 分段创建，确保时间准确"
echo ""
echo "字幕解决方案:"
echo "  - 不再使用FFmpeg的drawtext滤镜"
echo "  - 使用ImageMagick生成高质量字幕图片"
echo "  - 字幕图片为PNG格式，带透明背景"
echo "  - 字幕位置：视频底部200像素高度"
echo ""
echo "时间轴:"
TOTAL=0
for i in {0..4}; do
    DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "${AUDIO_FILES[$i]}" 2>/dev/null)
    if [ -z "$DURATION" ]; then
        DURATION="4.0"
    fi
    END=$(echo "$TOTAL + $DURATION" | awk '{print $1 + $2}')
    printf "  %.1f-%.1f秒: %s\n" "$TOTAL" "$END" "${SENTENCES[$i]:0:30}..."
    TOTAL=$END
done
echo ""
echo "最终视频: $FINAL_VIDEO"
echo "GitHub链接: https://github.com/sjf2525/openclaw/blob/main/chinese-culture-videos/jingzhe/output/$(basename "$FINAL_VIDEO")"