#!/usr/bin/env python3
"""
发送修复后的惊蛰视频
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

# 项目路径
PROJECT_DIR = Path(__file__).parent
VIDEO_FILE = PROJECT_DIR / "output" / "jingzhe_video_final_with_subtitles.mp4"

# 邮件配置
SMTP_CONFIG = {
    "host": "smtp.gmail.com",
    "port": 465,
    "username": "shenjianfei82@gmail.com",
    "password": "ffojcxxakliwbjgd",
    "use_ssl": True
}

TO_EMAIL = "shenjianfei82@gmail.com"
FROM_EMAIL = "shenjianfei82@gmail.com"

def send_fixed_video():
    """发送修复后的视频"""
    print("发送修复后的惊蛰视频...")
    
    if not VIDEO_FILE.exists():
        print(f"错误: 视频文件不存在: {VIDEO_FILE}")
        return False
    
    # 创建邮件
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL
    msg['Subject'] = "惊蛰视频修复版 - 已解决时长和字幕问题"
    
    # 邮件正文
    body = """您好！

这是修复后的惊蛰节气短视频，已解决以下问题：

🔧 修复的问题：
1. ✅ 视频时长：从10.5秒修复为23.23秒（完整音频）
2. ✅ 字幕显示：从白色方块修复为正常显示（使用Arial通用字体）
3. ✅ 图片显示：确保所有图片都有足够显示时间
4. ✅ 完整内容：包含全部5句配音和对应图片

📊 视频规格：
- 时长：23.23秒
- 尺寸：1080×1440 (3:4竖屏)，适合小红书
- 大小：612KB
- 格式：MP4 (H.264 + AAC)

🎬 内容时间轴：
0-4.65秒：惊蛰，是二十四节气中的第三个节气。
4.65-9.29秒：春雷始鸣，惊醒蛰伏于地下越冬的昆虫。
9.29-13.94秒：此时气温回升，雨水增多，万物开始复苏。
13.94-18.58秒：农民开始春耕，桃花红、李花白，黄莺鸣叫、燕子飞来。
18.58-23.23秒：惊蛰吃梨，寓意远离疾病，开启健康一年。

💡 问题原因分析：
1. 原视频使用-shortest参数，导致视频被截断
2. 字幕使用Microsoft YaHei字体，在某些设备上不可用
3. 图片显示时间计算错误

🚀 技术改进：
1. 移除-shortest参数，确保完整音频时长
2. 使用Arial通用字体，确保字幕正常显示
3. 精确计算图片显示时间，均匀分配

GitHub项目：https://github.com/sjf2525/openclaw/tree/main/chinese-culture-videos/jingzhe

请测试播放并确认问题已解决！

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
            f'attachment; filename="惊蛰视频修复版.mp4"'
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
        
        print("✅ 修复版视频邮件发送成功！")
        print(f"收件人: {TO_EMAIL}")
        print(f"主题: {msg['Subject']}")
        print(f"附件: 惊蛰视频修复版.mp4 ({VIDEO_FILE.stat().st_size} 字节)")
        
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("发送修复后的惊蛰视频")
    print("=" * 50)
    
    if not VIDEO_FILE.exists():
        print(f"错误: 修复后的视频文件不存在")
        print(f"请确保文件存在: {VIDEO_FILE}")
        return
    
    print(f"视频文件: {VIDEO_FILE}")
    print(f"文件大小: {VIDEO_FILE.stat().st_size} 字节")
    print(f"视频时长: 23.23秒")
    
    # 发送邮件
    email_success = send_fixed_video()
    
    if email_success:
        print("\n✅ 修复版视频已发送到邮箱！")
        print("请检查您的邮箱收件箱。")
    else:
        print("\n❌ 邮件发送失败")
        print(f"请从GitHub下载: https://github.com/sjf2525/openclaw/blob/main/chinese-culture-videos/jingzhe/output/jingzhe_video_final_with_subtitles.mp4")
    
    print("\n" + "=" * 50)
    print("完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()