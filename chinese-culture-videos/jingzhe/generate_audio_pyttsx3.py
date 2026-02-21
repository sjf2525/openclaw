#!/usr/bin/env python3
"""
使用pyttsx3生成惊蛰节气配音音频
离线文本转语音，无需网络
"""

import os
import pyttsx3
from pathlib import Path
import time

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

def init_tts_engine():
    """初始化TTS引擎"""
    print("初始化pyttsx3 TTS引擎...")
    
    try:
        engine = pyttsx3.init()
        
        # 获取可用声音
        voices = engine.getProperty('voices')
        print(f"找到 {len(voices)} 个语音引擎")
        
        # 尝试设置中文语音（如果可用）
        for voice in voices:
            if 'chinese' in voice.name.lower() or 'zh' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                print(f"使用中文语音: {voice.name}")
                break
        else:
            print("未找到中文语音，使用默认语音")
        
        # 设置语速（默认200，范围0-400）
        engine.setProperty('rate', 180)
        
        # 设置音量（0.0-1.0）
        engine.setProperty('volume', 0.9)
        
        return engine
        
    except Exception as e:
        print(f"初始化TTS引擎失败: {e}")
        return None

def generate_audio_with_pyttsx3(engine):
    """使用pyttsx3生成音频"""
    print("\n使用pyttsx3生成惊蛰配音音频...")
    
    all_audio_files = []
    
    for i, sentence in enumerate(sentences, 1):
        print(f"\n生成第 {i} 句: {sentence}")
        
        output_file = AUDIO_DIR / f"jingzhe_sentence_{i}.mp3"
        
        try:
            # 保存音频到文件
            engine.save_to_file(sentence, str(output_file))
            
            # 运行并等待完成
            engine.runAndWait()
            
            # 检查文件大小
            if output_file.exists():
                file_size = output_file.stat().st_size
                print(f"  已保存: {output_file} ({file_size} 字节)")
                
                if file_size > 1000:  # 确保文件不是空的
                    all_audio_files.append(output_file)
                else:
                    print(f"  警告: 文件太小，可能生成失败")
            else:
                print(f"  错误: 文件未生成")
            
            # 短暂暂停
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  生成错误: {e}")
    
    return all_audio_files

def merge_audio_with_ffmpeg(audio_files, output_file):
    """使用FFmpeg合并音频"""
    print(f"\n使用FFmpeg合并音频文件到: {output_file}")
    
    # 创建文件列表
    list_file = AUDIO_DIR / "audio_list.txt"
    with open(list_file, 'w') as f:
        for audio_file in audio_files:
            f.write(f"file '{audio_file.absolute()}'\n")
    
    # FFmpeg合并命令
    cmd = f"ffmpeg -f concat -safe 0 -i {list_file} -c copy {output_file}"
    print(f"执行命令: {cmd}")
    
    try:
        import subprocess
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"合并成功: {output_file}")
            if output_file.exists():
                file_size = output_file.stat().st_size
                print(f"文件大小: {file_size} 字节")
            return True
        else:
            print(f"合并失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"执行FFmpeg错误: {e}")
        print("请确保FFmpeg已安装: sudo apt install ffmpeg")
        return False

def create_simple_merge_script(audio_files):
    """创建简单的合并脚本"""
    print("\n创建音频合并脚本...")
    
    script_content = """#!/bin/bash
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
"""
    
    # 添加文件列表
    for audio_file in audio_files:
        script_content += f"file '{audio_file.absolute()}'\n"
    
    script_content += """EOF

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
"""
    
    script_file = AUDIO_DIR / "merge_audio.sh"
    script_file.write_text(script_content)
    script_file.chmod(0o755)
    
    print(f"合并脚本已创建: {script_file}")
    print(f"运行命令: cd {AUDIO_DIR} && bash merge_audio.sh")

def main():
    """主函数"""
    print("=" * 50)
    print("惊蛰节气音频生成脚本 (pyttsx3离线版)")
    print("=" * 50)
    
    # 初始化TTS引擎
    engine = init_tts_engine()
    if not engine:
        print("无法初始化TTS引擎")
        return
    
    # 生成音频
    audio_files = generate_audio_with_pyttsx3(engine)
    
    if not audio_files:
        print("\n未生成任何音频文件")
        return
    
    print(f"\n成功生成 {len(audio_files)} 个音频文件")
    
    # 创建合并脚本
    create_simple_merge_script(audio_files)
    
    # 尝试自动合并（如果FFmpeg可用）
    output_file = AUDIO_DIR / "jingzhe_full.mp3"
    print(f"\n尝试自动合并音频...")
    
    # 检查FFmpeg
    import subprocess
    ffmpeg_check = subprocess.run("which ffmpeg", shell=True, capture_output=True, text=True)
    
    if ffmpeg_check.returncode == 0:
        print("FFmpeg已安装，尝试合并...")
        if merge_audio_with_ffmpeg(audio_files, output_file):
            print("音频合并成功!")
        else:
            print("音频合并失败，请手动运行合并脚本")
    else:
        print("FFmpeg未安装，请手动运行合并脚本")
        print("安装FFmpeg: sudo apt install ffmpeg")
    
    print("\n" + "=" * 50)
    print("音频生成完成！")
    print("=" * 50)
    print("\n下一步：")
    print(f"1. 查看音频文件: {AUDIO_DIR}")
    print(f"2. 运行合并脚本: cd {AUDIO_DIR} && bash merge_audio.sh")
    print("3. 使用 jingzhe_full.mp3 进行视频制作")
    print("\n如果音频质量不理想，可以：")
    print("1. 调整pyttsx3的语速和音量")
    print("2. 尝试其他TTS引擎")
    print("3. 使用在线TTS服务生成音频")

if __name__ == "__main__":
    main()