# GitHub Actions 配置说明

## 定时任务配置

工作流文件已创建：`.github/workflows/bidding-monitor.yml`

### 触发条件
- **定时触发**：每小时运行一次（UTC时间整点）
- **手动触发**：可在 GitHub 页面点击 "Run workflow" 手动运行

### 北京时间对应
| UTC时间 | 北京时间 |
|---------|---------|
| 0:00 | 8:00 |
| 1:00 | 9:00 |
| ... | ... |
| 23:00 | 7:00+1 |

## 配置步骤

### 1. 设置 Secrets

在 GitHub 仓库页面：
1. 点击 **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. 添加以下 Secret：

| 名称 | 值 |
|------|-----|
| `FEISHU_WEBHOOK` | `https://open.feishu.cn/open-apis/bot/v2/hook/ecec741c-1993-43b4-88ea-b73e7e7c2bc2` |

### 2. 上传代码

将以下文件上传到 GitHub 仓库：
- `bidding_notifier.py` - 主程序
- `requirements.txt` - Python依赖
- `.github/workflows/bidding-monitor.yml` - GitHub Actions配置
- `README.md` - 说明文档

### 3. 验证运行

1. 进入仓库的 **Actions** 标签页
2. 点击 **招标信息监控** 工作流
3. 点击 **Run workflow** 手动触发测试
4. 查看运行日志确认是否正常

## 文件说明

### requirements.txt
```
playwright>=1.40.0
requests>=2.28.0
python-dateutil>=2.8.0
```

### 运行环境
- Ubuntu Latest
- Python 3.10
- Chromium 浏览器（通过 Playwright 安装）

## 常见问题

### 1. 推送记录丢失
GitHub Actions 每次运行都是新环境，推送记录通过 Artifacts 保存。工作流配置了自动上传 `pushed_bids.json` 文件。

### 2. 运行超时
如果网页加载慢，可以调整脚本中的等待时间：
```python
self.page.wait_for_timeout(10000)  # 改为更长的时间
```

### 3. 飞书推送失败
检查 Secret `FEISHU_WEBHOOK` 是否正确配置。
