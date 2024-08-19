from github import Github
from config import GITHUB_TOKEN

class GitHubService:
    def __init__(self):
        self.client = Github(GITHUB_TOKEN)

    def get_repo_info(self, repo_url):
        repo = self.client.get_repo(repo_url.split('github.com/')[1])
        return {
            "name": repo.name,
            "url": repo.html_url,
            "description": repo.description,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "last_updated": repo.updated_at,
        }
