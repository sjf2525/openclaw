#!/usr/bin/env python3
"""
发送惊蛰视频到邮箱
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from pathlib import Path

# 项目路径
PROJECT_DIR = Path(__file__).parent
VIDEO_FILE = PROJECT_DIR / "output" / "jingzhe_video_with_subtitles.mp4"

# 邮件配置 (从MEMORY.md获取)
SMTP_CONFIG = {
    "host": "smtp.gmail.com",
    "port": 465,
    "username": "shenjianfei82@gmail.com",
    "password": "ffojcxxakliwbjgd",
    "use_ssl": True
}

# 收件人
TO_EMAIL = "shenjianfei82@gmail.com"  # 发送到自己的邮箱
FROM_EMAIL = "shenjianfei82@gmail.com"

def send_email_with_video():
    """发送带视频附件的邮件"""
    print("准备发送惊蛰视频到邮箱...")
    
    if not VIDEO_FILE.exists():
        print(f"错误: 视频文件不存在: {VIDEO_FILE}")
        return False
    
    # 创建邮件
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL
    msg['Subject'] = "惊蛰节气短视频 - 中国传统文化项目成果"
    
    # 邮件正文
    body = """您好！

这是使用OpenClaw自动化生成的惊蛰节气短视频项目成果。

项目详情：
- 主题：二十四节气之惊蛰
- 时长：约18秒
- 规格：1080×1440 (3:4竖屏)，适合小红书
- 技术栈：完全免费工具 (edge-tts + tavily_search + FFmpeg)
- 成本：0元

视频内容：
1. 惊蛰，是二十四节气中的第三个节气。
2. 春雷始鸣，惊醒蛰伏于地下越冬的昆虫。
3. 此时气温回升，雨水增多，万物开始复苏。
4. 农民开始春耕，桃花红、李花白，黄莺鸣叫、燕子飞来。
5. 惊蛰吃梨，寓意远离疾病，开启健康一年。

GitHub项目地址：https://github.com/sjf2525/openclaw/tree/main/chinese-culture-videos/jingzhe

此视频完全使用自动化脚本生成，展示了零成本制作高质量中国传统文化短视频的可行性。

祝好！
OpenClaw AI助手
"""
    
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # 添加视频附件
    try:
        with open(VIDEO_FILE, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="{VIDEO_FILE.name}"'
        )
        msg.attach(part)
        print(f"已添加视频附件: {VIDEO_FILE.name}")
    except Exception as e:
        print(f"添加附件失败: {e}")
        return False
    
    # 发送邮件
    try:
        print("连接SMTP服务器...")
        if SMTP_CONFIG["use_ssl"]:
            server = smtplib.SMTP_SSL(SMTP_CONFIG["host"], SMTP_CONFIG["port"])
        else:
            server = smtplib.SMTP(SMTP_CONFIG["host"], SMTP_CONFIG["port"])
            server.starttls()
        
        print("登录邮箱...")
        server.login(SMTP_CONFIG["username"], SMTP_CONFIG["password"])
        
        print("发送邮件...")
        server.send_message(msg)
        server.quit()
        
        print("✅ 邮件发送成功！")
        print(f"收件人: {TO_EMAIL}")
        print(f"主题: {msg['Subject']}")
        print(f"附件: {VIDEO_FILE.name} ({VIDEO_FILE.stat().st_size} 字节)")
        
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        print("\n可能的原因:")
        print("1. Gmail应用密码错误或过期")
        print("2. 需要开启Gmail的'低安全性应用访问'")
        print("3. 网络连接问题")
        print("4. SMTP配置错误")
        
        # 提供替代方案
        print("\n替代方案:")
        print(f"1. 手动从GitHub下载: https://github.com/sjf2525/openclaw/blob/main/chinese-culture-videos/jingzhe/output/jingzhe_video_with_subtitles.mp4")
        print(f"2. 使用WhatsApp接收文件")
        
        return False

def create_alternative_download_instructions():
    """创建替代下载说明"""
    print("\n创建替代下载说明...")
    
    instructions = f"""# 惊蛰视频下载说明

由于邮件发送可能失败，请通过以下方式获取视频文件：

## 方法1: GitHub直接下载
1. 访问: https://github.com/sjf2525/openclaw
2. 进入目录: chinese-culture-videos/jingzhe/output/
3. 下载文件: jingzhe_video_with_subtitles.mp4

## 方法2: 原始GitHub链接
直接访问: https://github.com/sjf2525/openclaw/blob/main/chinese-culture-videos/jingzhe/output/jingzhe_video_with_subtitles.mp4
点击"Download"按钮

## 方法3: 通过WhatsApp接收
视频文件已通过WhatsApp发送到您的手机。

## 文件信息
- 文件名: jingzhe_video_with_subtitles.mp4
- 大小: {VIDEO_FILE.stat().st_size} 字节
- 规格: 1080×1440 (3:4竖屏)
- 时长: 约18秒
- 内容: 惊蛰节气介绍，带中文字幕

## 视频内容
1. 惊蛰，是二十四节气中的第三个节气。
2. 春雷始鸣，惊醒蛰伏于地下越冬的昆虫。
3. 此时气温回升，雨水增多，万物开始复苏。
4. 农民开始春耕，桃花红、李花白，黄莺鸣叫、燕子飞来。
5. 惊蛰吃梨，寓意远离疾病，开启健康一年。
"""
    
    instructions_file = PROJECT_DIR / "DOWNLOAD_INSTRUCTIONS.md"
    instructions_file.write_text(instructions)
    print(f"下载说明已保存: {instructions_file}")

def main():
    """主函数"""
    print("=" * 50)
    print("发送惊蛰视频到邮箱")
    print("=" * 50)
    
    # 检查视频文件
    if not VIDEO_FILE.exists():
        print(f"错误: 视频文件不存在")
        print(f"请确保文件存在: {VIDEO_FILE}")
        return
    
    print(f"视频文件: {VIDEO_FILE}")
    print(f"文件大小: {VIDEO_FILE.stat().st_size} 字节")
    
    # 尝试发送邮件
    success = send_email_with_video()
    
    if not success:
        print("\n邮件发送失败，创建替代方案...")
        create_alternative_download_instructions()
    
    print("\n" + "=" * 50)
    print("完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()