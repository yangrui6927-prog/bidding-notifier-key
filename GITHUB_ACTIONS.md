# GitHub Actions 配置指南

## 设置步骤

### 1. 配置 Secrets

在 GitHub 仓库页面，点击 **Settings → Secrets and variables → Actions**，添加以下 Secret：

| Secret 名称 | 值 |
|------------|-----|
| `FEISHU_WEBHOOK` | `https://open.feishu.cn/open-apis/bot/v2/hook/ecec741c-1993-43b4-88ea-b73e7e7c2bc2` |

### 2. 定时任务说明

工作流文件: `.github/workflows/bidding-monitor.yml`

默认每小时运行一次（UTC时间）：
```yaml
on:
  schedule:
    - cron: '0 * * * *'  # 每小时UTC时间运行
```

时间对应表：
- UTC 0:00 = 北京时间 8:00
- UTC 1:00 = 北京时间 9:00
- ...以此类推

如需修改运行时间，编辑 `bidding-monitor.yml` 中的 cron 表达式。

### 3. 常用 Cron 表达式

```yaml
# 每小时运行
- cron: '0 * * * *'

# 每2小时运行
- cron: '0 */2 * * *'

# 每天北京时间8点运行 (UTC 0:00)
- cron: '0 0 * * *'

# 工作日每小时运行 (周一到周五)
- cron: '0 * * * 1-5'
```

### 4. 手动触发

在 GitHub 仓库页面：
1. 点击 **Actions** 标签
2. 选择 **招标信息监控** 工作流
3. 点击 **Run workflow** 手动运行

### 5. 查看运行日志

1. 点击 **Actions** 标签
2. 点击具体的工作流运行记录
3. 查看每个步骤的执行日志

## 文件说明

| 文件 | 说明 |
|------|------|
| `bidding_notifier.py` | 主程序 |
| `requirements.txt` | Python 依赖 |
| `.github/workflows/bidding-monitor.yml` | GitHub Actions 配置 |
| `pushed_bids.json` | 已推送记录（自动生成） |

## 故障排查

### 推送失败
- 检查 Secrets 中的 `FEISHU_WEBHOOK` 是否正确
- 查看 Actions 日志中的错误信息

### 抓取失败
- 可能是网站结构变化，需要更新脚本
- 检查网络连接（GitHub Actions 网络环境）

### 重复推送
- 检查 `pushed_bids.json` 是否正确上传
-  Artifact 会保留30天，超时后会重新推送
