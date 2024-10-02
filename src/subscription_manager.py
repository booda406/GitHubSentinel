import json
from logger import LOG

class SubscriptionManager:
    def __init__(self, subscriptions_file):
        self.subscriptions_file = subscriptions_file
        self.subscriptions = self.load_subscriptions()

    def load_subscriptions(self):
        try:
            with open(self.subscriptions_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            LOG.warning(f"Subscriptions file not found. Creating a new one.")
            return {"github": [], "hacker_news": {"enabled": False, "keywords": []}}
        except json.JSONDecodeError:
            LOG.error(f"Invalid JSON in subscriptions file. Initializing with empty subscriptions.")
            return {"github": [], "hacker_news": {"enabled": False, "keywords": []}}

    def save_subscriptions(self):
        with open(self.subscriptions_file, 'w') as f:
            json.dump(self.subscriptions, f, indent=4)

    def list_github_subscriptions(self):
        return self.subscriptions.get("github", [])

    def add_github_subscription(self, repo):
        if repo not in self.subscriptions.get("github", []):
            self.subscriptions.setdefault("github", []).append(repo)
            self.save_subscriptions()
            LOG.info(f"Added GitHub subscription: {repo}")

    def remove_github_subscription(self, repo):
        if repo in self.subscriptions.get("github", []):
            self.subscriptions["github"].remove(repo)
            self.save_subscriptions()
            LOG.info(f"Removed GitHub subscription: {repo}")

    def get_hacker_news_subscription(self):
        return self.subscriptions.get("hacker_news", {"enabled": False, "keywords": []})

    def update_hacker_news_subscription(self, enabled, keywords):
        self.subscriptions["hacker_news"] = {"enabled": enabled, "keywords": keywords}
        self.save_subscriptions()
        LOG.info(f"Updated Hacker News subscription: enabled={enabled}, keywords={keywords}")

    def is_hacker_news_enabled(self):
        return self.subscriptions.get("hacker_news", {}).get("enabled", False)

    def get_hacker_news_keywords(self):
        return self.subscriptions.get("hacker_news", {}).get("keywords", [])

if __name__ == "__main__":
    # 測試代碼
    manager = SubscriptionManager("test_subscriptions.json")

    # 測試 GitHub 訂閱
    manager.add_github_subscription("octocat/Hello-World")
    manager.add_github_subscription("microsoft/vscode")
    print("GitHub subscriptions:", manager.list_github_subscriptions())

    manager.remove_github_subscription("octocat/Hello-World")
    print("GitHub subscriptions after removal:", manager.list_github_subscriptions())

    # 測試 Hacker News 訂閱
    manager.update_hacker_news_subscription(True, ["AI", "Python", "Blockchain"])
    print("Hacker News subscription:", manager.get_hacker_news_subscription())
    print("Is Hacker News enabled?", manager.is_hacker_news_enabled())
    print("Hacker News keywords:", manager.get_hacker_news_keywords())
