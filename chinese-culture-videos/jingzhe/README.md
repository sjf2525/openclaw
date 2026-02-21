# 惊蛰节气短视频生成项目

## 项目概述
这是一个用于生成中国传统文化短视频的自动化脚本项目，以"惊蛰"节气为例，展示如何使用免费工具创建高质量的小红书短视频。

## 技术栈
- **配音**: OpenClaw TTS / edge-tts
- **图片素材**: tavily search
- **字幕**: Whisper (可选)
- **视频剪辑**: FFmpeg
- **编程语言**: Python 3

## 项目结构
```
jingzhe/
├── script.md              # 视频脚本和分镜设计
├── generate_video.py      # 主视频生成脚本
├── test_tts.py           # TTS测试脚本
├── tts_instructions.md   # TTS使用说明
├── README.md             # 项目说明
├── audio/                # 音频文件目录
├── images/               # 图片素材目录
└── output/               # 输出文件目录
```

## 快速开始

### 1. 环境准备
```bash
# 确保有Python 3
python3 --version

# 安装FFmpeg (如未安装)
# Ubuntu/Debian: sudo apt install ffmpeg
# macOS: brew install ffmpeg
```

### 2. 生成配音
```bash
# 方法1: 使用OpenClaw TTS (在OpenClaw环境中)
openclaw tts --text "惊蛰，是二十四节气中的第三个节气。"

# 方法2: 使用edge-tts
pip install edge-tts
edge-tts --text "惊蛰..." --write-media audio/jingzhe.mp3 --voice zh-CN-XiaoxiaoNeural
```

### 3. 获取图片素材
```bash
# 使用tavily_search获取惊蛰相关图片
# 关键词: 惊蛰 节气 春雷 春雨 桃花 春耕 燕子 梨子
```

### 4. 生成视频
```bash
# 运行主脚本
python3 generate_video.py

# 或手动使用FFmpeg
ffmpeg -loop 1 -i images/1.jpg -i audio/jingzhe.mp3 -c:v libx264 -c:a aac -shortest output/jingzhe.mp4
```

## 视频规格
- **时长**: 15秒
- **比例**: 3:4 (竖屏)
- **分辨率**: 1080×1440
- **平台**: 小红书

## 脚本内容
视频脚本包含4个镜头：
1. **0-3秒**: 春雷惊醒万物
2. **3-7秒**: 春雨滋润大地
3. **7-11秒**: 春耕生机勃勃
4. **11-15秒**: 惊蛰习俗与祝福

## 标签建议
- #二十四节气 #惊蛰 #传统文化 #中国风 #春天 #节气养生

## 扩展计划
1. 实现全自动化流水线
2. 扩展到其他23个节气
3. 添加更多传统文化主题
4. 集成A/B测试和数据分析

## 注意事项
1. 确保使用有版权的图片素材，或使用免费图库
2. TTS音频需要测试不同声音，选择最适合的
3. 视频前3秒必须有吸引人的"钩子"
4. 添加字幕提高观看体验

## 贡献
欢迎提交Issue和Pull Request，共同完善中国传统文化短视频自动化工具。