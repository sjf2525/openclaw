#!/usr/bin/env python3
"""
使用edge-tts技能生成惊蛰配音音频
"""

import os
import subprocess
import time
from pathlib import Path

# 项目路径
PROJECT_DIR = Path(__file__).parent
AUDIO_DIR = PROJECT_DIR / "audio"
AUDIO_DIR.mkdir(exist_ok=True)

# 惊蛰脚本
sentences = [
    "惊蛰，是二十四节气中的第三个节气。",
    "春雷始鸣，惊醒蛰伏于地下越冬的昆虫。",
    "此时气温回升，雨水增多，万物开始复苏。",
    "农民开始春耕，桃花红、李花白，黄莺鸣叫、燕子飞来。",
    "惊蛰吃梨，寓意远离疾病，开启健康一年。"
]

def run_edge_tts_script(text, output_file):
    """运行edge-tts脚本生成音频"""
    print(f"生成: {text[:20]}...")
    
    # edge-tts技能脚本路径
    edge_tts_dir = Path.home() / ".openclaw/workspace/skills/edge-tts"
    tts_script = edge_tts_dir / "scripts/tts-converter.js"
    
    if not tts_script.exists():
        print(f"错误: 未找到edge-tts脚本: {tts_script}")
        return False
    
    # 构建命令
    cmd = [
        "node", str(tts_script),
        f'"{text}"',
        "--voice", "zh-CN-XiaoxiaoNeural",
        "--output", str(output_file)
    ]
    
    print(f"命令: {' '.join(cmd)}")
    
    try:
        # 切换到脚本目录
        os.chdir(tts_script.parent)
        
        # 运行命令
        result = subprocess.run(
            ["node", "tts-converter.js", text, 
             "--voice", "zh-CN-XiaoxiaoNeural",
             "--output", str(output_file)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"  成功: {output_file}")
            return True
        else:
            print(f"  错误: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  异常: {e}")
        return False

def generate_audio_with_edge_tts():
    """使用edge-tts生成音频"""
    print("使用edge-tts生成惊蛰配音音频...")
    
    all_audio_files = []
    
    for i, sentence in enumerate(sentences, 1):
        output_file = AUDIO_DIR / f"jingzhe_sentence_{i}.mp3"
        
        if run_edge_tts_script(sentence, output_file):
            # 检查文件是否生成
            if output_file.exists() and output_file.stat().st_size > 0:
                file_size = output_file.stat().st_size
                print(f"  文件大小: {file_size} 字节")
                all_audio_files.append(output_file)
            else:
                print(f"  警告: 文件可能为空或未生成")
        
        # 避免请求过快
        time.sleep(2)
    
    return all_audio_files

def create_simple_audio_alternative():
    """创建简单的音频替代方案（如果edge-tts失败）"""
    print("\n创建简单的音频替代方案...")
    
    # 创建文本文件，供手动处理
    text_file = AUDIO_DIR / "jingzhe_script.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write("惊蛰配音脚本\n")
        f.write("=" * 40 + "\n\n")
        
        for i, sentence in enumerate(sentences, 1):
            f.write(f"句子 {i}:\n")
            f.write(f"{sentence}\n\n")
    
    print(f"脚本已保存: {text_file}")
    
    # 创建手动处理说明
    instructions = f"""# 手动生成惊蛰音频说明

## 方法1: 使用edge-tts命令行
```bash
# 安装edge-tts
npm install -g edge-tts

# 生成音频
edge-tts --text "惊蛰，是二十四节气中的第三个节气。" --write-media audio/jingzhe_1.mp3 --voice zh-CN-XiaoxiaoNeural
```

## 方法2: 使用OpenClaw tts工具
在OpenClaw会话中直接使用tts工具：
```
tts("惊蛰，是二十四节气中的第三个节气。")
```

## 方法3: 使用在线TTS服务
1. 访问: https://tts.travisvn.com/
2. 选择中文语音: zh-CN-XiaoxiaoNeural
3. 输入文本并下载音频

## 音频文件列表
需要生成5个音频文件：
1. audio/jingzhe_sentence_1.mp3
2. audio/jingzhe_sentence_2.mp3
3. audio/jingzhe_sentence_3.mp3
4. audio/jingzhe_sentence_4.mp3
5. audio/jingzhe_sentence_5.mp3

## 合并音频
```bash
# 使用FFmpeg合并
ffmpeg -f concat -safe 0 -i audio_list.txt -c copy audio/jingzhe_full.mp3

# audio_list.txt内容：
file 'jingzhe_sentence_1.mp3'
file 'jingzhe_sentence_2.mp3'
file 'jingzhe_sentence_3.mp3'
file 'jingzhe_sentence_4.mp3'
file 'jingzhe_sentence_5.mp3'
```
"""
    
    instructions_file = AUDIO_DIR / "MANUAL_AUDIO_GUIDE.md"
    instructions_file.write_text(instructions)
    print(f"手动指南已保存: {instructions_file}")

def main():
    """主函数"""
    print("=" * 50)
    print("使用edge-tts生成惊蛰音频")
    print("=" * 50)
    
    # 检查edge-tts技能
    edge_tts_dir = Path.home() / ".openclaw/workspace/skills/edge-tts"
    if not edge_tts_dir.exists():
        print("错误: edge-tts技能未安装")
        print("请运行: clawhub install edge-tts")
        create_simple_audio_alternative()
        return
    
    print(f"edge-tts技能路径: {edge_tts_dir}")
    
    # 尝试生成音频
    audio_files = generate_audio_with_edge_tts()
    
    if audio_files:
        print(f"\n成功生成 {len(audio_files)} 个音频文件")
        
        # 创建合并脚本
        create_merge_script(audio_files)
    else:
        print("\nedge-tts生成失败，创建替代方案")
        create_simple_audio_alternative()
    
    print("\n" + "=" * 50)
    print("音频生成完成！")
    print("=" * 50)

def create_merge_script(audio_files):
    """创建合并脚本"""
    print("\n创建音频合并脚本...")
    
    # 创建文件列表
    list_file = AUDIO_DIR / "audio_list.txt"
    with open(list_file, 'w') as f:
        for audio_file in audio_files:
            f.write(f"file '{audio_file.name}'\n")
    
    # 创建合并脚本
    script_content = f"""#!/bin/bash
# 合并惊蛰音频脚本

echo "合并惊蛰音频..."

# 检查FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "错误: FFmpeg未安装"
    echo "请安装: sudo apt install ffmpeg"
    exit 1
fi

# 合并音频
ffmpeg -f concat -safe 0 -i {list_file.name} -c copy {AUDIO_DIR}/jingzhe_full.mp3

if [ $? -eq 0 ]; then
    echo "成功合并音频: {AUDIO_DIR}/jingzhe_full.mp3"
    echo "文件信息:"
    ffmpeg -i {AUDIO_DIR}/jingzhe_full.mp3 2>&1 | grep -E "Duration|Stream"
else
    echo "合并失败"
fi
"""
    
    script_file = AUDIO_DIR / "merge_audio.sh"
    script_file.write_text(script_content)
    script_file.chmod(0o755)
    
    print(f"合并脚本已创建: {script_file}")
    print(f"运行命令: bash {script_file}")

if __name__ == "__main__":
    main()