#!/usr/bin/env python3
"""
中国移动招标信息抓取与飞书推送系统
- 只对标题进行关键词筛选
- 获取点击后新窗口的详情页URL
- 推送到指定飞书Webhook
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from playwright.sync_api import sync_playwright


class FeishuAPI:
    def send_webhook(self, webhook_url, message):
        headers = {"Content-Type": "application/json"}
        data = {"msg_type": "text", "content": {"text": message}}
        resp = requests.post(webhook_url, headers=headers, json=data, timeout=30)
        return resp.status_code == 200


class BiddingScraper:
    URLS = {
        "招标采购公告": "https://b2b.10086.cn/#/biddingProcurementBulletin",
    }
    
    def __init__(self):
        self.browser = None
        self.page = None
        
    def init_browser(self):
        p = sync_playwright().start()
        self.browser = p.chromium.launch(headless=True)
        self.context = self.browser.new_context(viewport={"width": 1920, "height": 1080})
        self.page = self.context.new_page()
        
    def fetch_page(self, url, category="招标采购公告"):
        try:
            print(f"正在抓取: {url}")
            self.page.goto(url, wait_until="networkidle", timeout=90000)
            self.page.wait_for_timeout(10000)
            
            rows = self.page.query_selector_all("table tbody tr")
            print(f"找到 {len(rows)} 行数据")
            
            bids = []
            for row in rows:
                bid = self._parse_row(row, category)
                if bid:
                    bids.append(bid)
                    
            return bids
        except Exception as e:
            print(f"抓取失败: {e}")
            return []
    
    def _parse_row(self, row, category):
        try:
            cells = row.query_selector_all("td")
            if len(cells) < 4:
                return None
            
            province = cells[0].inner_text().strip()
            bid_type = cells[1].inner_text().strip()
            title = cells[2].inner_text().strip()
            date_str = cells[3].inner_text().strip()
            
            return {
                "type": bid_type,
                "title": title,
                "date": date_str,
                "province": province,
                "url": "",
                "category": category,
            }
        except Exception as e:
            return None
    
    def get_detail_url_for_bid(self, bid):
        """点击标题，在新窗口获取详情URL"""
        try:
            title = bid.get("title", "")
            print(f"  获取详情URL: {title[:40]}...")
            
            # 在页面中找到对应标题的行
            rows = self.page.query_selector_all("table tbody tr")
            target_row = None
            for row in rows:
                cells = row.query_selector_all("td")
                if len(cells) >= 4:
                    row_title = cells[2].inner_text().strip()
                    if row_title == title:
                        target_row = row
                        break
            
            if not target_row:
                print(f"    ✗ 未找到对应行")
                return ""
            
            # 找到标题单元格中的可点击元素
            cells = target_row.query_selector_all("td")
            title_cell = cells[2]
            clickable = title_cell.query_selector("span")
            
            if not clickable:
                print(f"    ✗ 未找到可点击元素")
                return ""
            
            # 等待新窗口弹出
            with self.page.expect_popup(timeout=10000) as popup_info:
                clickable.click()
            
            popup = popup_info.value
            popup.wait_for_load_state("networkidle")
            detail_url = popup.url
            popup.close()
            
            if "noticeDetail" in detail_url:
                print(f"    ✓ 获取成功")
                return detail_url
            else:
                print(f"    ✗ URL不含noticeDetail")
                return ""
                
        except Exception as e:
            print(f"    ✗ 获取失败: {e}")
            return ""
    
    def close(self):
        if self.browser:
            self.browser.close()


class BiddingNotifier:
    KEYWORDS = [
        "系统集成", "硬件集成", "智算", "网络", "智算优化", "城域网", "承载网", 
        "CMNET", "支撑", "边缘云", "数据网", "资源池", "网络云", "IPNET", 
        "MDCN", "CDN", "路由器", "核心网", "5G", "SDN", "数据中心", 
        "防火墙", "可视化", "大屏", "短信", "彩信", "短彩信", "内容管理", 
        "短消息", "消息"
    ]
    
    def __init__(self):
        self.webhook = os.getenv("FEISHU_WEBHOOK", "https://open.feishu.cn/open-apis/bot/v2/hook/ecec741c-1993-43b4-88ea-b73e7e7c2bc2")
        self.fetch_hours = int(os.getenv("FETCH_HOURS", "2"))
        self.pushed_file = "pushed_bids.json"
        self.scraper = BiddingScraper()
        self.feishu = FeishuAPI()
        
    def load_pushed(self):
        try:
            with open(self.pushed_file, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except:
            return set()
    
    def save_pushed(self, titles):
        with open(self.pushed_file, 'w', encoding='utf-8') as f:
            json.dump(list(titles), f)
    
    def match_by_title(self, bid):
        title = bid.get("title", "")
        for keyword in self.KEYWORDS:
            if keyword in title:
                return True, keyword
        return False, None
    
    def is_recent(self, bid):
        try:
            date_str = bid.get("date", "")
            bid_date = date_parser.parse(date_str)
            cutoff = datetime.now() - timedelta(hours=self.fetch_hours)
            result = bid_date > cutoff
            print(f"    → 日期解析: '{date_str}' -> {bid_date}, 截止时间: {cutoff}, 是否最近: {result}")
            return result
        except Exception as e:
            print(f"    → 日期解析失败 '{bid.get('date', '')}': {e}, 默认通过")
            return True
    
    def format_message(self, bids):
        type_counts = {}
        for bid in bids:
            t = bid.get("type", "其他")
            type_counts[t] = type_counts.get(t, 0) + 1
        
        summary = " | ".join([f"{t}{c}条" for t, c in type_counts.items()])
        message = f"您好，此次一共检索{len(bids)}条新消息（{summary}）～\n\n"
        
        for bid_type in type_counts.keys():
            type_bids = [b for b in bids if b.get("type") == bid_type]
            for i, bid in enumerate(type_bids, 1):
                message += f"【{bid_type}{i}】\n"
                message += f"发布单位：{bid.get('province', '未知')}\n"
                message += f"发布时间：{bid.get('date', '未知')}\n"
                message += f"《{bid.get('title', '无标题')}》\n"
                url = bid.get('url', '')
                if url:
                    message += f"链接：{url}\n\n"
                else:
                    message += f"链接：https://b2b.10086.cn/#/biddingProcurementBulletin\n\n"
        
        return message
    
    def run(self):
        print("=" * 50)
        print("开始抓取招标信息...")
        print("=" * 50)
        
        self.scraper.init_browser()
        pushed = self.load_pushed()
        print(f"已有 {len(pushed)} 条推送记录\n")
        
        # 抓取所有招标
        all_bids = []
        for category, url in BiddingScraper.URLS.items():
            print(f"正在抓取: {category}")
            bids = self.scraper.fetch_page(url, category)
            all_bids.extend(bids)
            print(f"  抓取到 {len(bids)} 条\n")
        
        # 筛选: 时间 + 未推送 + 标题匹配
        matched = []
        for bid in all_bids:
            title = bid.get("title", "")
            bid_date = bid.get("date", "")
            print(f"  检查: {title[:40]}... | 日期: {bid_date}")

            if title in pushed:
                print(f"    → 已推送过，跳过")
                continue
            if not self.is_recent(bid):
                cutoff = datetime.now() - timedelta(hours=self.fetch_hours)
                print(f"    → 不在时间范围内 ({self.fetch_hours}小时), 截止时间: {cutoff}")
                continue
            is_match, keyword = self.match_by_title(bid)
            if is_match:
                print(f"    → ✓ 匹配关键词: {keyword}")
                matched.append(bid)
            else:
                print(f"    → 未匹配任何关键词")

        print(f"\n总计: {len(all_bids)} 条, 匹配: {len(matched)} 条")
        
        # 为匹配项获取详情URL
        if matched:
            print("正在为匹配项获取详情URL...")
            for bid in matched:
                detail_url = self.scraper.get_detail_url_for_bid(bid)
                bid["url"] = detail_url
        
        self.scraper.close()
        
        if not matched:
            print("没有匹配的招标信息")
            return
        
        # 显示匹配结果
        for bid in matched:
            url_short = bid.get('url', '')[:50] + "..." if bid.get('url') else "列表页"
            print(f"✓ {bid.get('title', '')[:40]}... | URL: {url_short}")
        
        # 推送
        message = self.format_message(matched)
        success = self.feishu.send_webhook(self.webhook, message)
        print(f"\n推送结果: {'成功' if success else '失败'}")
        
        # 保存已推送
        for bid in matched:
            pushed.add(bid.get("title"))
        self.save_pushed(pushed)
        
        print("完成!")


if __name__ == "__main__":
    notifier = BiddingNotifier()
    notifier.run()
