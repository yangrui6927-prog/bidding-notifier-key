# 招标通知助手 (Bidding Notifier)

中国移动招标信息自动抓取与飞书推送系统。

## 功能

- 自动抓取中国移动采购与招标网的招标公告
- 根据关键词对标题进行智能筛选
- 获取详情页链接（点击标题后的具体页面）
- 推送到飞书群聊

## 关键词列表

系统集成、硬件集成、智算、网络、智算优化、城域网、承载网、CMNET、支撑、边缘云、数据网、资源池、网络云、IPNET、MDCN、CDN、路由器、核心网、5G、SDN、数据中心、防火墙、可视化、大屏、短信、彩信、短彩信、内容管理、短消息、消息

## 安装依赖

```bash
pip install playwright requests python-dateutil
playwright install chromium
```

## 运行

```bash
python bidding_notifier.py
```

## 配置

- `FEISHU_WEBHOOK`: 飞书Webhook地址
- `FETCH_HOURS`: 抓取时间范围（默认25小时）

## GitHub Actions 定时运行

配置每小时自动抓取并推送：

1. Fork 或创建仓库
2. 在仓库 Settings → Secrets → Actions 中添加 `FEISHU_WEBHOOK`
3. 定时任务会自动每小时运行

详见 [GITHUB_ACTIONS.md](GITHUB_ACTIONS.md)

## 推送目标

飞书群: https://open.feishu.cn/open-apis/bot/v2/hook/ecec741c-1993-43b4-88ea-b73e7e7c2bc2
