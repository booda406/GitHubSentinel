# ./src/hacker_news_client.py

import requests
from logger import LOG
from datetime import datetime, timedelta
import os

class HackerNewsClient:
    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def __init__(self, keywords=None):
        self.session = requests.Session()
        self.keywords = keywords or []

    def filter_stories_by_keywords(self, stories):
        if not self.keywords:
            return stories

        filtered_stories = []
        for story in stories:
            title = story.get('title', '').lower()
            if any(keyword.lower() in title for keyword in self.keywords):
                filtered_stories.append(story)
        return filtered_stories

    def get_top_stories(self, limit=30):
        """獲取最新的熱門故事 ID 列表"""
        try:
            response = self.session.get(f"{self.BASE_URL}/topstories.json")
            response.raise_for_status()
            return response.json()[:limit]
        except requests.RequestException as e:
            LOG.error(f"獲取熱門故事時發生錯誤: {e}")
            return []

    def get_item_details(self, item_id):
        """獲取特定項目的詳細信息"""
        try:
            response = self.session.get(f"{self.BASE_URL}/item/{item_id}.json")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            LOG.error(f"獲取項目 {item_id} 詳細信息時發生錯誤: {e}")
            return None

    def get_top_stories_details(self, limit=30):
        """獲取最新熱門故事的詳細信息"""
        top_stories = self.get_top_stories(limit)
        stories_details = []
        for story_id in top_stories:
            story_details = self.get_item_details(story_id)
            if story_details:
                stories_details.append(story_details)
        return stories_details

    def export_daily_trends(self):
        """導出每日趨勢報告"""
        LOG.debug("[準備導出 Hacker News 每日趨勢]")
        today = datetime.now().date().isoformat()
        all_stories = self.get_top_stories_details()
        filtered_stories = self.filter_stories_by_keywords(all_stories)

        trends_dir = os.path.join('..', 'daily_progress', 'hacker_news')
        os.makedirs(trends_dir, exist_ok=True)

        # 生成未過濾的報告
        unfiltered_file_path = os.path.join(trends_dir, f'{today}_unfiltered.md')
        self._write_report(unfiltered_file_path, all_stories, today, "Unfiltered")

        # 生成過濾後的報告
        filtered_file_path = os.path.join(trends_dir, f'{today}_filtered.md')
        self._write_report(filtered_file_path, filtered_stories, today, "Filtered")

        LOG.info(f"[Hacker News] 每日趨勢文件生成：{unfiltered_file_path}, {filtered_file_path}")
        return unfiltered_file_path, filtered_file_path

    def export_trends_by_date_range(self, days):
        """導出指定日期範圍的趨勢報告"""
        LOG.debug(f"[準備導出 Hacker News {days} 天趨勢]")
        today = datetime.now().date()
        since = today - timedelta(days=days)
        stories = self.get_top_stories_details(50)  # 獲取更多故事以涵蓋更長時間範圍

        trends_dir = os.path.join('..', 'daily_progress', 'hacker_news')
        os.makedirs(trends_dir, exist_ok=True)

        date_str = f"{since}_to_{today}"
        file_path = os.path.join(trends_dir, f'{date_str}.md')

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"# Hacker News Trends ({since} to {today})\n\n")
            for story in stories:
                file.write(f"## {story.get('title', 'No Title')}\n")
                file.write(f"- URL: {story.get('url', 'N/A')}\n")
                file.write(f"- Score: {story.get('score', 'N/A')}\n")
                file.write(f"- Author: {story.get('by', 'N/A')}\n")
                file.write(f"- Comments: {story.get('descendants', 'N/A')}\n")
                file.write(f"- Date: {datetime.fromtimestamp(story.get('time', 0)).date().isoformat()}\n\n")

        LOG.info(f"[Hacker News] {days} 天趨勢文件生成：{file_path}")
        return file_path

    def _write_report(self, file_path, stories, date, report_type):
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"# Hacker News Daily Trends - {report_type} ({date})\n\n")
            for story in stories:
                file.write(f"## {story.get('title', 'No Title')}\n")
                file.write(f"- URL: {story.get('url', 'N/A')}\n")
                file.write(f"- Score: {story.get('score', 'N/A')}\n")
                file.write(f"- Author: {story.get('by', 'N/A')}\n")
                file.write(f"- Comments: {story.get('descendants', 'N/A')}\n\n")

if __name__ == "__main__":
    # 測試代碼
    client = HackerNewsClient()

    # 測試每日趨勢報告
    unfiltered_path, filtered_path = client.export_daily_trends()
    print(f"未過濾的每日趨勢報告已生成：{unfiltered_path}")
    print(f"已過濾的每日趨勢報告已生成：{filtered_path}")

    # 測試日期範圍趨勢報告
    range_report_path = client.export_trends_by_date_range(7)  # 生成過去7天的趨勢報告
    print(f"7天趨勢報告已生成：{range_report_path}")
