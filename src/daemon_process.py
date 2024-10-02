import schedule
import time
import signal
import sys

from config import Config
from github_client import GitHubClient
from notifier import Notifier
from report_generator import ReportGenerator
from llm import LLM
from subscription_manager import SubscriptionManager
from logger import LOG
from hacker_news_client import HackerNewsClient  # 新增：導入 HackerNewsClient

def graceful_shutdown(signum, frame):
    LOG.info("[优雅退出]守护进程接收到终止信号")
    sys.exit(0)

def github_job(subscription_manager, github_client, report_generator, notifier, days):
    LOG.info("[开始执行 GitHub 定时任务]")
    subscriptions = subscription_manager.list_github_subscriptions()
    LOG.info(f"订阅列表：{subscriptions}")
    for repo in subscriptions:
        markdown_file_path = github_client.export_progress_by_date_range(repo, days)
        report, report_file_path = report_generator.generate_report_by_date_range(markdown_file_path, days)
        notifier.notify(repo, report)
    LOG.info(f"[GitHub 定时任务执行完毕]")

def hacker_news_job(hacker_news_client, report_generator, notifier):
    LOG.info("[开始执行 Hacker News 定时任务]")
    unfiltered_file_path, filtered_file_path = hacker_news_client.export_daily_trends()

    # 生成未過濾的報告
    unfiltered_report, unfiltered_report_path = report_generator.generate_report_by_date_range(unfiltered_file_path, 1)
    notifier.notify("Hacker News Daily Trends - Unfiltered", unfiltered_report)

    # 生成過濾後的報告
    filtered_report, filtered_report_path = report_generator.generate_report_by_date_range(filtered_file_path, 1)
    notifier.notify("Hacker News Daily Trends - Filtered", filtered_report)

    LOG.info(f"[Hacker News 定时任务执行完毕]")

def main():
    signal.signal(signal.SIGTERM, graceful_shutdown)

    config = Config()
    github_client = GitHubClient(config.github_token)
    notifier = Notifier(config.email, config.slack_webhook_url)  # 更新：添加 Slack Webhook URL
    llm = LLM()
    report_generator = ReportGenerator(llm)
    subscription_manager = SubscriptionManager(config.subscriptions_file)
    hacker_news_client = HackerNewsClient(keywords=config.hacker_news['keywords'])  # 新增：創建 HackerNewsClient 實例

    # GitHub 任務設置
    github_job(subscription_manager, github_client, report_generator, notifier, config.freq_days)
    schedule.every(config.freq_days).days.at(config.exec_time).do(
        github_job, subscription_manager, github_client, report_generator, notifier, config.freq_days
    )

    # 新增：Hacker News 任務設置
    if config.hacker_news['enabled']:
        hacker_news_job(hacker_news_client, report_generator, notifier)  # 立即執行一次
        for execution_time in config.hacker_news['execution_time'].split(','):
            schedule.every().day.at(execution_time.strip()).do(
                hacker_news_job, hacker_news_client, report_generator, notifier
            )

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception as e:
        LOG.error(f"主进程发生异常: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
