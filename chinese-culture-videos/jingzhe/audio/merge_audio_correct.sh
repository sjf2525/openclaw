#!/bin/bash
# 正确的音频合并脚本
# 先转换WAV到MP3，再合并

echo "开始处理惊蛰音频..."

# 检查文件
echo "检查音频文件..."
for i in {1..5}; do
    file="jingzhe_sentence_${i}.mp3"
    if [ -f "$file" ]; then
        size=$(stat -c%s "$file")
        echo "  $file: $size 字节"
    else
        echo "  错误: $file 不存在"
        exit 1
    fi
done

# 先转换所有文件为标准的MP3格式
echo -e "\n转换音频格式..."
for i in {1..5}; do
    input="jingzhe_sentence_${i}.mp3"
    output="jingzhe_sentence_${i}_converted.mp3"
    
    echo "转换 $input -> $output"
    ffmpeg -i "$input" -acodec libmp3lame -b:a 128k -ar 44100 -ac 2 "$output" -y 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "  转换成功"
    else
        echo "  转换失败"
        exit 1
    fi
done

# 创建文件列表
echo -e "\n创建合并文件列表..."
cat > filelist.txt << 'EOF'
file 'jingzhe_sentence_1_converted.mp3'
file 'jingzhe_sentence_2_converted.mp3'
file 'jingzhe_sentence_3_converted.mp3'
file 'jingzhe_sentence_4_converted.mp3'
file 'jingzhe_sentence_5_converted.mp3'
EOF

echo "文件列表内容:"
cat filelist.txt

# 合并音频
echo -e "\n合并音频文件..."
ffmpeg -f concat -safe 0 -i filelist.txt -c copy jingzhe_full_final.mp3 -y

if [ $? -eq 0 ]; then
    echo -e "\n合并成功!"
    echo "输出文件: jingzhe_full_final.mp3"
    
    # 显示文件信息
    echo -e "\n文件信息:"
    file jingzhe_full_final.mp3
    ls -lh jingzhe_full_final.mp3
    
    # 测试播放（如果可能）
    echo -e "\n音频时长:"
    ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 jingzhe_full_final.mp3 2>/dev/null | awk '{printf "%.2f 秒\n", $1}'
    
else
    echo "合并失败"
    exit 1
fi

echo -e "\n清理临时文件..."
rm -f jingzhe_sentence_*_converted.mp3 filelist.txt

echo -e "\n完成! 最终音频文件: jingzhe_full_final.mp3"