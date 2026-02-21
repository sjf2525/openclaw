#!/bin/bash
# 惊蛰音频合并脚本
# 使用方法: bash merge_audio.sh

echo "合并惊蛰音频..."

# 检查FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "错误: FFmpeg未安装"
    echo "请安装: sudo apt install ffmpeg"
    exit 1
fi

# 创建文件列表
echo "创建音频文件列表..."
cat > audio_list.txt << 'EOF'
file '/home/codespace/.openclaw/workspace/chinese-culture-videos/jingzhe/audio/jingzhe_sentence_1.mp3'
file '/home/codespace/.openclaw/workspace/chinese-culture-videos/jingzhe/audio/jingzhe_sentence_2.mp3'
file '/home/codespace/.openclaw/workspace/chinese-culture-videos/jingzhe/audio/jingzhe_sentence_3.mp3'
file '/home/codespace/.openclaw/workspace/chinese-culture-videos/jingzhe/audio/jingzhe_sentence_4.mp3'
file '/home/codespace/.openclaw/workspace/chinese-culture-videos/jingzhe/audio/jingzhe_sentence_5.mp3'
EOF

# 合并音频
echo "合并音频文件..."
ffmpeg -f concat -safe 0 -i audio_list.txt -c copy jingzhe_full.mp3

if [ $? -eq 0 ]; then
    echo "合并成功: jingzhe_full.mp3"
    echo "文件信息:"
    file jingzhe_full.mp3
    ls -lh jingzhe_full.mp3
else
    echo "合并失败"
    exit 1
fi

echo "完成!"
