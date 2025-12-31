# 🚀 Streamlit Cloud 部署指南

## 部署步骤

### 第 1 步：准备 GitHub 账号

1. 访问 [GitHub](https://github.com)
2. 注册或登录账号
3. 创建新仓库 `deepinsight`

### 第 2 步：上传代码到 GitHub

#### 方式 A：使用 GitHub Web 界面（推荐新手）

1. 在 GitHub 创建新仓库 `deepinsight`
2. 点击 "Add file" → "Upload files"
3. 上传以下文件：
   - `app.py`
   - `database.py`
   - `data_provider.py`
   - `deepseek_analyzer.py`
   - `cache_manager.py`
   - `config.py`
   - `requirements.txt`
   - `.gitignore`
   - `README.md`
   - `QUICKSTART.md`
   - `ARCHITECTURE.md`
   - `.streamlit/config.toml`

4. 提交更改

#### 方式 B：使用 Git 命令（推荐开发者）

```bash
# 1. 在 GitHub 创建仓库后获取 HTTPS URL
# 例如: https://github.com/your-username/deepinsight.git

# 2. 添加远程仓库
cd /home/ubuntu/deepinsight
git remote add origin https://github.com/your-username/deepinsight.git

# 3. 推送代码
git branch -M main
git push -u origin main
```

### 第 3 步：部署到 Streamlit Cloud

1. 访问 [Streamlit Cloud](https://streamlit.io/cloud)
2. 点击 "Sign up" 并用 GitHub 账号登录
3. 授权 Streamlit 访问 GitHub
4. 点击 "New app"
5. 填写部署信息：
   - **Repository**: `your-username/deepinsight`
   - **Branch**: `main`
   - **Main file path**: `app.py`
6. 点击 "Deploy"

### 第 4 步：配置 Secrets（API Key）

1. 部署完成后，点击应用右上角的 "☰" 菜单
2. 选择 "Settings"
3. 点击 "Secrets"
4. 添加以下 Secret：
   ```
   DEEPSEEK_API_KEY = "sk-your-api-key-here"
   ```
5. 保存并重启应用

### 第 5 步：验证部署

1. 应用应该自动启动
2. 访问生成的 URL（例如 `https://deepinsight.streamlit.app`）
3. 检查所有功能是否正常

## 部署后的维护

### 自动更新

Streamlit Cloud 会自动监听 GitHub 仓库：
- 每当您推送代码到 `main` 分支时，应用会自动重新部署
- 无需手动操作

### 更新代码

```bash
# 修改代码后
git add .
git commit -m "Update: 描述更改"
git push origin main
# 应用会自动重新部署
```

### 查看日志

1. 在 Streamlit Cloud 应用页面
2. 点击右上角的 "☰" 菜单
3. 选择 "View logs"

### 重启应用

1. 应用页面右上角 "☰" 菜单
2. 选择 "Reboot app"

## 常见问题

### Q1: 部署后应用无法启动？

**A:** 检查以下几点：

1. 查看日志中的错误信息
2. 确认 `requirements.txt` 包含所有依赖
3. 确认 `app.py` 在仓库根目录
4. 检查是否有 Python 语法错误

### Q2: API Key 无法读取？

**A:** 确认：

1. Secret 已正确添加到 Streamlit Cloud
2. 在代码中使用 `st.secrets["DEEPSEEK_API_KEY"]` 读取
3. 应用已重启

### Q3: 数据库文件丢失？

**A:** Streamlit Cloud 容器重启时会丢失本地文件。解决方案：

1. **短期**：使用 Streamlit Cloud 的 file upload 功能
2. **长期**：迁移到云数据库（MySQL/PostgreSQL）

### Q4: 应用很慢？

**A:** 可能原因：

1. AkShare 数据获取慢 → 添加缓存
2. DeepSeek API 响应慢 → 正常（10-30 秒）
3. Streamlit Cloud 免费层限制 → 升级到付费

### Q5: 如何删除应用？

**A:** 在 Streamlit Cloud 应用设置中选择 "Delete app"

## 成本说明

### Streamlit Cloud 免费层

- ✅ **完全免费**
- ✅ 无限应用数量
- ✅ 无限用户访问
- ✅ 自动 HTTPS
- ⚠️ 容器 1 小时无活动会休眠
- ⚠️ 存储限制（但 SQLite 很小）

### 升级到付费

如果需要：
- 更高的性能
- 24/7 运行（不休眠）
- 更多存储

可以升级到 Streamlit Cloud Pro（$15/月）

## 备份和恢复

### 备份数据库

```bash
# 从 Streamlit Cloud 下载数据库
# 1. 在应用中添加下载功能
# 2. 或者通过 GitHub 上传备份

# 本地备份
cp /home/ubuntu/deepinsight/deepinsight.db backup_$(date +%Y%m%d).db
```

### 恢复数据库

```bash
# 将备份文件上传到 GitHub
git add deepinsight.db
git commit -m "Backup database"
git push origin main
```

## 监控和告警

### 检查应用状态

访问 Streamlit Cloud 仪表板查看：
- 应用状态
- 最后部署时间
- 资源使用情况

### 设置告警（可选）

使用 GitHub Actions 定期检查应用健康状态：

```yaml
# .github/workflows/health-check.yml
name: Health Check
on:
  schedule:
    - cron: '0 */6 * * *'  # 每 6 小时检查一次

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Check app
        run: curl -f https://your-app.streamlit.app || exit 1
```

## 下一步

### 优化建议

1. **添加云数据库**
   - 迁移到 MySQL/PostgreSQL
   - 支持多用户和数据持久化

2. **添加用户认证**
   - 使用 Streamlit 的 authentication
   - 支持多用户登录

3. **性能优化**
   - 添加更多缓存
   - 优化 API 调用

4. **监控和分析**
   - 添加使用统计
   - 性能监控

## 技术支持

- [Streamlit 文档](https://docs.streamlit.io)
- [Streamlit Cloud 文档](https://docs.streamlit.io/streamlit-cloud)
- [GitHub 帮助](https://docs.github.com)

---

**部署完成后，您的应用将永久在线！** 🎉
