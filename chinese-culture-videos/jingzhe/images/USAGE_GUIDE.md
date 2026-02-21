# 惊蛰节气图片使用说明

## 已下载的图片

### 1. jingzhe_spring_thunder.jpg
- **用途**: 春雷闪电动画背景
- **场景**: 视频开头0-3秒
- **内容**: 春雷惊醒万物

### 2. jingzhe_insects.jpg
- **用途**: 昆虫苏醒特写
- **场景**: 镜头1，配合"惊醒蛰伏于地下越冬的昆虫"
- **内容**: 土壤中昆虫爬出

### 3. jingzhe_spring_rain.jpg
- **用途**: 春雨滋润大地
- **场景**: 镜头2，配合"雨水增多，万物复苏"
- **内容**: 春雨场景

### 4. jingzhe_peach_blossom.jpg
- **用途**: 桃花李花绽放
- **场景**: 镜头2-3，配合"桃花红、李花白"
- **内容**: 春季花朵

### 5. jingzhe_farming.jpg
- **用途**: 农民春耕
- **场景**: 镜头3，配合"农民开始春耕"
- **内容**: 春耕场景

## 图片处理建议

### 1. 尺寸调整
所有图片应调整为小红书竖屏比例 3:4 (1080×1440)

```bash
# 使用ImageMagick调整尺寸
mogrify -resize 1080x1440^ -gravity center -extent 1080x1440 images/*.jpg
```

### 2. 添加文字
为每张图片添加相应的文字说明：
- 使用白色字体，黑色描边
- 字体大小适中，不影响画面主体
- 位置：底部或顶部安全区域

### 3. 转场效果
建议使用淡入淡出效果：
- 每张图片显示3-4秒
- 转场时间0.5秒
- 配合音频节奏

## 版权注意事项
1. 这些图片来自网络搜索，请确认版权状态
2. 建议最终使用前替换为有明确授权的图片
3. 可考虑使用免费图库如Pexels、Pixabay的替代图片

## 备用图片关键词
如果图片不合适，可搜索以下关键词：
- "spring thunder china"
- "insects waking up soil"
- "spring rain landscape"
- "peach blossom china"
- "traditional chinese farming"
