#!/usr/bin/env python3
"""
生成惊蛰节气配音音频
使用gTTS（Google Text-to-Speech）在线服务
"""

import os
from pathlib import Path
from gtts import gTTS
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

def generate_audio_with_gtts():
    """使用gTTS生成音频"""
    print("使用gTTS生成惊蛰配音音频...")
    print("注意：需要网络连接，使用Google TTS服务")
    
    all_audio_files = []
    
    for i, sentence in enumerate(sentences, 1):
        print(f"\n生成第 {i} 句: {sentence}")
        
        output_file = AUDIO_DIR / f"jingzhe_sentence_{i}.mp3"
        
        try:
            # 使用gTTS生成音频
            tts = gTTS(text=sentence, lang='zh-cn', slow=False)
            tts.save(str(output_file))
            
            # 检查文件大小
            file_size = output_file.stat().st_size
            print(f"  已保存: {output_file} ({file_size} 字节)")
            
            all_audio_files.append(output_file)
            
            # 避免请求过快
            time.sleep(1)
            
        except Exception as e:
            print(f"  错误: {e}")
            print("  可能的原因：网络连接问题或gTTS服务限制")
    
    return all_audio_files

def merge_audio_files(audio_files, output_file):
    """合并多个音频文件"""
    print(f"\n合并音频文件到: {output_file}")
    
    try:
        # 使用pydub合并音频
        from pydub import AudioSegment
        
        combined = AudioSegment.empty()
        for audio_file in audio_files:
            audio = AudioSegment.from_mp3(str(audio_file))
            combined += audio
            # 添加短暂静音
            combined += AudioSegment.silent(duration=200)  # 200毫秒静音
        
        combined.export(str(output_file), format="mp3")
        print(f"合并完成: {output_file}")
        return True
        
    except ImportError:
        print("未安装pydub，无法自动合并音频")
        print("请手动合并音频文件或安装pydub: pip install pydub")
        return False
    except Exception as e:
        print(f"合并错误: {e}")
        return False

def create_ffmpeg_merge_script(audio_files):
    """创建FFmpeg合并脚本"""
    print("\n创建FFmpeg合并脚本...")
    
    # 创建文件列表
    list_file = AUDIO_DIR / "audio_list.txt"
    with open(list_file, 'w') as f:
        for audio_file in audio_files:
            f.write(f"file '{audio_file.absolute()}'\n")
    
    # 创建合并脚本
    script_content = f"""#!/bin/bash
# FFmpeg合并音频脚本

# 合并所有句子
ffmpeg -f concat -safe 0 -i {list_file} -c copy {AUDIO_DIR}/jingzhe_full.mp3

echo "音频已合并到: {AUDIO_DIR}/jingzhe_full.mp3"
"""
    
    script_file = AUDIO_DIR / "merge_audio.sh"
    script_file.write_text(script_content)
    script_file.chmod(0o755)
    
    print(f"FFmpeg脚本已创建: {script_file}")
    print(f"运行命令: bash {script_file}")

def main():
    """主函数"""
    print("=" * 50)
    print("惊蛰节气音频生成脚本")
    print("=" * 50)
    
    # 检查gTTS是否可用
    try:
        import gtts
        print("gTTS模块可用")
    except ImportError:
        print("未安装gTTS，尝试安装...")
        try:
            import subprocess
            subprocess.run(["pip", "install", "gtts"], check=False)
            print("gTTS安装完成")
        except:
            print("无法安装gTTS，请手动安装: pip install gtts")
            return
    
    # 生成音频
    audio_files = generate_audio_with_gtts()
    
    if not audio_files:
        print("\n未生成任何音频文件")
        return
    
    # 创建合并脚本
    create_ffmpeg_merge_script(audio_files)
    
    print("\n" + "=" * 50)
    print("音频生成完成！")
    print("=" * 50)
    print("\n下一步：")
    print(f"1. 查看音频文件: {AUDIO_DIR}")
    print(f"2. 运行合并脚本: bash {AUDIO_DIR}/merge_audio.sh")
    print("3. 使用合并后的完整音频进行视频制作")

if __name__ == "__main__":
    main()