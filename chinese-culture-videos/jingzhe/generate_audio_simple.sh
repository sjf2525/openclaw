#!/bin/bash
# 生成惊蛰音频的简单脚本

cd "$(dirname "$0")"
AUDIO_DIR="audio"
mkdir -p "$AUDIO_DIR"

# 惊蛰脚本
SENTENCES=(
    "惊蛰，是二十四节气中的第三个节气。"
    "春雷始鸣，惊醒蛰伏于地下越冬的昆虫。"
    "此时气温回升，雨水增多，万物开始复苏。"
    "农民开始春耕，桃花红、李花白，黄莺鸣叫、燕子飞来。"
    "惊蛰吃梨，寓意远离疾病，开启健康一年。"
)

echo "开始生成惊蛰音频..."
echo "================================"

for i in "${!SENTENCES[@]}"; do
    sentence="${SENTENCES[$i]}"
    output_file="$AUDIO_DIR/jingzhe_$((i+1)).mp3"
    
    echo "生成第 $((i+1)) 句: ${sentence:0:20}..."
    
    # 使用edge-tts技能
    cd ~/.openclaw/workspace/skills/edge-tts/scripts
    node tts-converter.js "$sentence" \
        --voice zh-CN-XiaoxiaoNeural \
        --output "$(cd - && pwd)/$output_file"
    
    if [ $? -eq 0 ]; then
        file_size=$(stat -f%z "$(cd - && pwd)/$output_file" 2>/dev/null || stat -c%s "$(cd - && pwd)/$output_file" 2>/dev/null)
        echo "  成功: $output_file (${file_size}字节)"
    else
        echo "  失败"
    fi
    
    echo "--------------------------------"
    sleep 1
done

echo "音频生成完成！"
echo "================================"
echo "生成的音频文件:"
ls -la "$AUDIO_DIR"/*.mp3 2>/dev/null || echo "暂无音频文件"

# 创建合并脚本
echo ""
echo "创建合并脚本..."
cat > "$AUDIO_DIR/merge.sh" << 'EOF'
#!/bin/bash
# 合并惊蛰音频

echo "正在合并音频..."
ffmpeg -f concat -safe 0 -i file_list.txt -c copy jingzhe_full.mp3

if [ $? -eq 0 ]; then
    echo "合并成功: jingzhe_full.mp3"
else
    echo "合并失败，请检查FFmpeg是否安装"
fi
EOF

# 创建文件列表
echo "file 'jingzhe_1.mp3'" > "$AUDIO_DIR/file_list.txt"
echo "file 'jingzhe_2.mp3'" >> "$AUDIO_DIR/file_list.txt"
echo "file 'jingzhe_3.mp3'" >> "$AUDIO_DIR/file_list.txt"
echo "file 'jingzhe_4.mp3'" >> "$AUDIO_DIR/file_list.txt"
echo "file 'jingzhe_5.mp3'" >> "$AUDIO_DIR/file_list.txt"

chmod +x "$AUDIO_DIR/merge.sh"

echo ""
echo "要合并音频，请运行:"
echo "  cd $AUDIO_DIR && ./merge.sh"
echo ""
echo "注意: 需要FFmpeg来合并音频"