# 安全指南 - 避免敏感信息泄露

## 经验教训

### 2026-02-22 敏感信息泄露事件
- **问题**：在推送到GitHub仓库的代码中包含了Gmail SMTP密码
- **影响**：密码 `ffojcxxakliwbjgd` 被暴露在公开仓库中
- **解决**：立即删除包含密码的文件并更新MEMORY.md

### 已删除的文件
1. `send_fixed_video.py` - 包含SMTP密码
2. `complete_video_workflow.py` - 包含SMTP密码
3. `send_imagemagick_video_email.py` - 包含SMTP密码
4. `send_pil_video_email.py` - 包含SMTP密码
5. `send_video_email.py` - 包含SMTP密码
6. `send_perfect_video_email.py` - 包含SMTP密码
7. `send_segmented_video_email.py` - 包含SMTP密码
8. `send_email.py` - 包含SMTP密码
9. `DELIVERY_CONFIRMATION.md` - 包含邮箱地址

### 已更新的文件
1. `MEMORY.md` - 将密码和API密钥替换为 `***`
2. `memory/2026-02-21.md` - 将邮箱地址替换为 `***@gmail.com`
3. `memory/2026-02-21-summary.md` - 将邮箱地址替换为 `***@gmail.com`

## 安全最佳实践

### 1. 密码和API密钥处理
- **绝对不要** 将明文密码或API密钥提交到版本控制系统
- 使用环境变量或配置文件（不提交到仓库）
- 在代码中使用占位符，如 `***` 或 `YOUR_API_KEY_HERE`
- 在文档中说明如何设置这些值

### 2. 邮箱地址处理
- 避免在代码中硬编码邮箱地址
- 如果必须引用，使用通用格式，如 `user@example.com`
- 在公开文档中使用占位符，如 `***@gmail.com`

### 3. 配置文件管理
- 创建 `.env.example` 文件作为模板
- 将实际的 `.env` 文件添加到 `.gitignore`
- 在README中说明如何创建配置文件

### 4. 代码审查
- 在提交前检查代码中是否包含敏感信息
- 使用工具扫描敏感信息：`grep -r "password\|api_key\|secret\|token" .`
- 定期审查仓库历史，确保没有敏感信息泄露

### 5. Git操作
- 如果敏感信息已提交，立即：
  1. 从仓库中删除包含敏感信息的文件
  2. 更新相关文件，替换敏感信息为占位符
  3. 提交更改并推送到远程仓库
  4. 考虑是否需要重写Git历史（对于严重泄露）

## 模板示例

### Python代码中的安全配置
```python
# 不安全 - 硬编码密码
smtp_password = "ffojcxxakliwbjgd"

# 安全 - 使用环境变量
import os
smtp_password = os.getenv("SMTP_PASSWORD", "***")
```

### 配置文件模板 (.env.example)
```bash
# 邮箱配置
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here

# API密钥
TAVILY_API_KEY=your_tavily_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 文档中的占位符
```markdown
## 邮箱配置
- SMTP主机: smtp.gmail.com
- SMTP端口: 465
- 邮箱账号: ***@gmail.com
- 邮箱密码: ***
```

## 紧急处理流程

如果发现敏感信息已泄露：

1. **立即行动**
   - 删除包含敏感信息的文件
   - 更新相关文档
   - 提交修复

2. **通知相关人员**
   - 如果涉及第三方服务（如Gmail），考虑更改密码
   - 如果涉及API密钥，考虑重新生成密钥

3. **预防措施**
   - 更新.gitignore文件
   - 建立代码审查流程
   - 培训团队成员

## 工具推荐

1. **git-secrets** - 防止将敏感信息提交到Git仓库
2. **truffleHog** - 扫描Git仓库中的敏感信息
3. **gitleaks** - 检测硬编码的密码和密钥

---

**记住**：安全不是一次性的任务，而是持续的过程。每次提交代码前都要问自己："这里面有没有不应该公开的信息？"