import json
import os

class Config:
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        # 尝试从环境变量获取配置或使用 config.json 文件中的配置作为回退
        with open('config.json', 'r') as f:
            config = json.load(f)
            
            # 使用环境变量或配置文件的 GitHub Token
            self.github_token = os.getenv('GITHUB_TOKEN', config.get('github_token'))

            # 初始化电子邮件设置
            self.email = config.get('email', {})
            # 使用环境变量或配置文件中的电子邮件密码
            self.email['password'] = os.getenv('EMAIL_PASSWORD', self.email.get('password', ''))

            # 使用环境变量或配置文件中的 Slack Webhook URL
            self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL', config.get('slack_webhook_url'))

            self.subscriptions_file = config.get('subscriptions_file')
            # 默认每天执行
            self.freq_days = config.get('github_progress_frequency_days', 1)
            # 默认早上8点更新 (操作系统默认时区是 UTC +0，08点刚好对应北京时间凌晨12点)
            self.exec_time = config.get('github_progress_execution_time', "08:00")

        # Hacker News 配置
        self.hacker_news = config.get('hacker_news', {})
        self.hacker_news['enabled'] = config.get('hacker_news', {}).get('enabled', False)
        self.hacker_news['check_frequency_hours'] = config.get('hacker_news', {}).get('check_frequency_hours', 6)
        self.hacker_news['execution_time'] = config.get('hacker_news', {}).get('execution_time', "00:00,06:00,12:00,18:00")
        self.hacker_news['top_stories_limit'] = config.get('hacker_news', {}).get('top_stories_limit', 30)

        # 新增：讀取 Hacker News keywords
        self.hacker_news['keywords'] = self.load_hacker_news_keywords()

    def load_hacker_news_keywords(self):
        with open(self.subscriptions_file, 'r') as f:
            subscriptions = json.load(f)
        return subscriptions.get('hacker_news', {}).get('keywords', [])
