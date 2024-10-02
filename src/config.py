import json
import os

class Config:
    def __init__(self):
        self.load_config()

    def load_config(self):
        with open('config.json', 'r') as f:
            config = json.load(f)

            # 優先使用環境變量中的 GitHub token，如果不存在，則使用 config.json 中的值
            self.github_token = os.environ.get('GITHUB_TOKEN') or config.get('github_token')

            # 如果兩者都不存在，拋出異常
            if not self.github_token:
                raise ValueError("GitHub token not found in environment variables or config.json")

            # 其他配置保持不變
            self.notification_settings = config.get('notification_settings')
            self.subscriptions_file = config.get('subscriptions_file')
            self.update_interval = config.get('update_interval', 24 * 60 * 60)  # Default to 24 hours

