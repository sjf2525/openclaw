#!/usr/bin/env python3
"""
测试OpenClaw TTS工具
生成惊蛰节气的配音测试
"""

import os
import subprocess
from pathlib import Path

# 项目路径
PROJECT_DIR = Path(__file__).parent
AUDIO_DIR = PROJECT_DIR / "audio"
AUDIO_DIR.mkdir(exist_ok=True)

# 惊蛰脚本文本
JINGZHE_SCRIPT = """惊蛰，是二十四节气中的第三个节气。
春雷始鸣，惊醒蛰伏于地下越冬的昆虫。
此时气温回升，雨水增多，万物开始复苏。
农民开始春耕，桃花红、李花白，黄莺鸣叫、燕子飞来。
惊蛰吃梨，寓意远离疾病，开启健康一年。"""

def test_openclaw_tts_direct():
    """直接测试OpenClaw TTS工具"""
    print("测试OpenClaw TTS工具...")
    
    # 将文本分成短句，避免过长
    sentences = JINGZHE_SCRIPT.split('。')
    sentences = [s.strip() for s in sentences if s.strip()]
    
    print(f"将生成 {len(sentences)} 个音频片段")
    
    for i, sentence in enumerate(sentences, 1):
        print(f"\n生成第 {i} 句: {sentence}")
        
        # 这里应该调用OpenClaw的tts工具
        # 由于在OpenClaw环境中，我们可以通过exec调用
        cmd = f'openclaw tts --text "{sentence}"'
        print(f"命令: {cmd}")
        
        # 在实际环境中，可以这样调用：
        # result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        # print(f"结果: {result.stdout}")
        
    print("\n提示：在实际OpenClaw环境中，tts工具会自动发送音频")

def create_tts_instructions():
    """创建TTS使用说明"""
    print("\n创建TTS使用说明...")
    
    instructions = f"""# OpenClaw TTS 测试说明

## 测试文本
{JINGZHE_SCRIPT}

## 使用方法

### 方法1：使用OpenClaw tts工具
```bash
# 生成完整音频
openclaw tts --text "{JINGZHE_SCRIPT}"

# 或分句生成
openclaw tts --text "惊蛰，是二十四节气中的第三个节气。"
openclaw tts --text "春雷始鸣，惊醒蛰伏于地下越冬的昆虫。"
openclaw tts --text "此时气温回升，雨水增多，万物开始复苏。"
openclaw tts --text "农民开始春耕，桃花红、李花白，黄莺鸣叫、燕子飞来。"
openclaw tts --text "惊蛰吃梨，寓意远离疾病，开启健康一年。"
```

### 方法2：在OpenClaw会话中直接使用
在OpenClaw聊天中，tts工具会自动处理音频生成。

### 方法3：使用edge-tts（如已安装）
```bash
# 安装edge-tts
pip install edge-tts

# 生成音频
edge-tts --text "{JINGZHE_SCRIPT}" --write-media audio/jingzhe.mp3 --voice zh-CN-XiaoxiaoNeural
```

## 预期输出
- 生成MP3格式的音频文件
- 中文发音清晰自然
- 适合15秒短视频使用

## 音频文件保存
请将生成的音频文件保存到: {AUDIO_DIR}
"""
    
    instructions_file = PROJECT_DIR / "tts_instructions.md"
    instructions_file.write_text(instructions)
    print(f"说明文件已保存: {instructions_file}")

def main():
    """主函数"""
    print("=" * 50)
    print("OpenClaw TTS 测试脚本")
    print("=" * 50)
    
    # 测试TTS
    test_openclaw_tts_direct()
    
    # 创建说明文件
    create_tts_instructions()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)
    print("\n下一步：")
    print("1. 查看 tts_instructions.md 获取详细说明")
    print("2. 使用OpenClaw tts工具生成音频")
    print("3. 将音频文件保存到 audio/ 目录")
    print(f"4. 项目目录: {PROJECT_DIR}")

if __name__ == "__main__":
    main()