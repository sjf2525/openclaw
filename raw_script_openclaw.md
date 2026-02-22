# OpenClaw 部署、配置与技能使用指南

## 1. OpenClaw 概述
OpenClaw 是一个开源AI助手框架，支持本地部署和云部署。它可以通过插件集成各种消息通道（如Feishu、WhatsApp、Telegram等），并拥有丰富的技能库。

## 2. 部署方法
### 2.1 本地部署（使用Ollama和Kimi K2.5）
- 运行Ollama服务
- 配置Kimi K2.5作为AI模型服务
- 启动OpenClaw并选择模型
- 安装核心技能（文档处理、网页自动化、系统集成）
- 通过浏览器访问OpenClaw界面

### 2.2 配置步骤
1. 选择AI模型服务（如Kimi K2.5）
2. 安装所需技能（建议仅安装核心技能，避免耗时）
3. 接受默认设置或进行自定义
4. 选择在浏览器中打开OpenClaw

## 3. 技能使用
### 3.1 技能安装
- 使用命令：`openclaw plugins install @m1heng-clawd/feishu`（安装Feishu插件）
- 技能市场：https://clawhub.com 查找新技能
- 通过ClawHub CLI搜索、安装、更新和发布技能

### 3.2 核心技能
- **文档处理**：office-document-specialist-suite（Word、Excel、PowerPoint）
- **PDF提取**：pdf-extract（使用pdftotext）
- **PPT生成**：ppt-generator（乔布斯风HTML演示稿）
- **网页自动化**：浏览器控制技能
- **系统集成**：Feishu、WhatsApp、Telegram等通道集成

## 4. Feishu集成
### 4.1 创建Feishu应用
1. 访问Feishu开放平台（open.feishu.cn）
2. 进入开发者控制台，创建自建应用
3. 填写应用信息
4. 在"凭证与基础信息"页面获取App ID和App Secret

### 4.2 配置OpenClaw
```bash
openclaw config set channels.feishu.appId "YOUR_APP_ID"
openclaw config set channels.feishu.appSecret "YOUR_APP_SECRET"
openclaw config set channels.feishu.enabled true
openclaw config set channels.feishu.connectionMode websocket
openclaw config set channels.feishu.dmPolicy pairing
openclaw config set channels.feishu.groupPolicy allowlist
openclaw config set channels.feishu.requireMention true
```

### 4.3 安装Feishu桥接技能
- 技能名称：feishu-bridge
- 功能：通过WebSocket长连接将Feishu机器人连接到Clawdbot
- 无需公共服务器、域名或ngrok
- 本地运行，维护出站WebSocket连接

### 4.4 配置权限和事件
- 启用权限：`im:message`、`im:message.group_at_msg`、`im:message.p2p_msg`
- 添加事件：`im.message.receive_v1`
- 设置交付方式为WebSocket长连接
- 发布应用（创建版本→申请审核）

## 5. 技能开发
### 5.1 技能结构
- 技能目录：`~/.openclaw/skills/[skill_name]/`
- 入口文件：`__init__.py`或指定Python文件
- 工具注册：通过`@tool`装饰器注册
- 配置文件：`SKILL.md`提供使用说明

### 5.2 创建技能步骤
1. 创建技能目录
2. 创建核心文件（__init__.py、功能文件、SKILL.md）
3. 编写核心功能代码
4. 配置认证信息
5. 测试技能功能
6. 在OpenClaw中调用技能

## 6. 最佳实践
### 6.1 部署建议
- 仅安装需要的技能，避免安装所有技能（耗时）
- 定期更新OpenClaw和技能
- 备份配置文件

### 6.2 使用场景
- 桌面应用程序控制（打开WPS并创建文档）
- 消息平台集成（Feishu/Lark）
- 浏览器自动化与研究
- 文档搜索和检索
- 自动消息撰写和发送
- 会议摘要生成
- 任务管理和提醒创建

### 6.3 故障排除
- 检查网关状态：`openclaw gateway status`
- 重启服务：`openclaw gateway restart`
- 查看日志：`openclaw tui /status`
- 验证Feishu连接：检查桥接服务状态

## 7. 资源链接
- 官方文档：https://docs.openclaw.ai
- 技能市场：https://clawhub.com
- GitHub仓库：https://github.com/openclaw/openclaw
- 社区支持：Discord https://discord.com/invite/clawd
- 独立指南：https://open-claw.online（多语言文档和技能排行榜）

## 8. 总结
OpenClaw是一个强大的本地AI助手框架，通过灵活的插件和技能系统，可以集成到各种工作流程中。Feishu集成使团队能够直接在聊天中与AI助手交互，提高工作效率。