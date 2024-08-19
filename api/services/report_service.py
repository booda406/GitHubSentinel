from .github_service import GitHubService

class ReportService:
    def __init__(self):
        self.github_service = GitHubService()

    def generate_report(self, repo_url):
        repo_info = self.github_service.get_repo_info(repo_url)
        
        report = f"""
        Repository Report for {repo_info['name']}
        
        URL: {repo_info['url']}
        Description: {repo_info['description']}
        Stars: {repo_info['stars']}
        Forks: {repo_info['forks']}
        Last Updated: {repo_info['last_updated']}
        
        This repository has been starred by {repo_info['stars']} users and forked {repo_info['forks']} times.
        It was last updated on {repo_info['last_updated']}.
        """
        
        return report
