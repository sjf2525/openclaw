#!/usr/bin/env python3
"""
测试字幕图片是否包含文字
"""

import subprocess
import os
from pathlib import Path

# 项目路径
PROJECT_DIR = Path(__file__).parent
OUTPUT_DIR = PROJECT_DIR / "output"

def test_subtitle_image(image_path):
    """测试字幕图片是否包含文字"""
    print(f"\n测试字幕图片: {image_path.name}")
    
    # 检查文件大小
    file_size = image_path.stat().st_size
    print(f"  文件大小: {file_size} 字节")
    
    # 使用ImageMagick检查图片信息
    cmd = ["identify", "-verbose", str(image_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if "Colorspace: Gray" in result.stdout:
        print("  ⚠️  警告: 图片为灰度图，可能没有文字")
    
    if "Colorspace: sRGB" in result.stdout:
        print("  ✅ 图片为彩色图")
    
    # 检查是否有文字内容（通过检查像素值）
    cmd = ["convert", str(image_path), "-format", "%[fx:mean]", "info:"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout.strip():
        mean_value = float(result.stdout.strip())
        print(f"  平均像素值: {mean_value:.3f}")
        if mean_value < 0.1:
            print("  ⚠️  警告: 图片非常暗，可能只有背景没有文字")
        elif mean_value > 0.9:
            print("  ⚠️  警告: 图片非常亮，可能只有白色背景")
        else:
            print("  ✅ 图片有合理的像素分布")
    
    # 检查图片尺寸
    cmd = ["identify", "-format", "%wx%h", str(image_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"  图片尺寸: {result.stdout.strip()}")

def create_proper_subtitle(text, output_path):
    """创建正确的字幕图片"""
    print(f"\n创建正确的字幕图片: {text[:20]}...")
    
    # 使用更简单的命令创建字幕图片
    cmd = [
        "convert",
        "-size", "1080x200",
        "xc:'rgba(0,0,0,180)'",  # 黑色半透明背景
        "-fill", "white",
        "-font", "DejaVu-Sans",
        "-pointsize", "40",
        "-gravity", "center",
        f"label:{text}",
        str(output_path)
    ]
    
    print(f"  执行命令: {' '.join(cmd[:5])}...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"  ✅ 字幕图片创建成功")
        
        # 验证图片
        test_subtitle_image(output_path)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ 创建失败: {e}")
        return False

def main():
    """主函数"""
    print("测试字幕图片问题...")
    print("=" * 60)
    
    # 测试现有的字幕图片
    subtitle_files = list(OUTPUT_DIR.glob("subtitle_*.png"))
    
    if subtitle_files:
        print(f"找到 {len(subtitle_files)} 个字幕图片")
        for file in subtitle_files[:3]:  # 只测试前3个
            test_subtitle_image(file)
    else:
        print("没有找到字幕图片")
    
    # 创建新的字幕图片测试
    print("\n" + "=" * 60)
    print("创建新的字幕图片测试...")
    
    test_text = "测试字幕：惊蛰节气"
    test_output = OUTPUT_DIR / "test_subtitle_new.png"
    
    if create_proper_subtitle(test_text, test_output):
        print(f"\n✅ 测试字幕图片创建成功: {test_output}")
        
        # 显示图片信息
        cmd = ["identify", str(test_output)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(f"图片信息: {result.stdout.strip()}")
        
        # 检查文件大小
        file_size = test_output.stat().st_size
        print(f"文件大小: {file_size} 字节")
        
        if file_size > 5000:
            print("✅ 文件大小正常（应大于5KB）")
        else:
            print("⚠️  文件大小可能太小")
    else:
        print("\n❌ 测试字幕图片创建失败")
    
    print("\n" + "=" * 60)
    print("问题分析:")
    print("1. 现有的字幕图片可能没有正确包含文字")
    print("2. ImageMagick的label命令可能没有正确渲染中文字体")
    print("3. 需要尝试不同的字体和参数")
    print("\n建议解决方案:")
    print("1. 使用-caption代替label（自动换行）")
    print("2. 尝试不同的字体")
    print("3. 增加字体大小")
    print("4. 添加描边效果")

if __name__ == "__main__":
    main()