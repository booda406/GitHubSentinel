import os
from datetime import date, datetime, timedelta
from typing import Dict, Tuple, Any
from logger import LOG

class ReportGenerator:
    DAILY_PROGRESS_DIR = 'daily_progress'

    def __init__(self, llm: Any):
        """
        Initialize the ReportGenerator.

        :param llm: The language model to use for report generation.
        """
        self.llm = llm
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


    def get_full_path(self, relative_path: str) -> str:
        """
        Get the full path for a file relative to the base directory.

        :param relative_path: The relative path of the file.
        :return: The full path of the file.
        """
        return os.path.join(self.base_dir, relative_path)


    def export_daily_progress(self, repo: str, updates: Dict[str, list]) -> str:
        """
        Export daily progress for a repository.

        :param repo: The repository name.
        :param updates: A dictionary containing 'issues' and 'pull_requests'.
        :return: The path to the exported file.
        """
        repo_dir = os.path.join(self.DAILY_PROGRESS_DIR, repo.replace("/", "_"))
        os.makedirs(repo_dir, exist_ok=True)
        
        file_path = os.path.join(repo_dir, f'{date.today()}.md')
        try:
            with open(file_path, 'w') as file:
                file.write(f"# Daily Progress for {repo} ({date.today()})\n\n")
                file.write("\n## Issues\n")
                for issue in updates['issues']:
                    file.write(f"- {issue['title']} #{issue['number']}\n")
                file.write("\n## Pull Requests\n")
                for pr in updates['pull_requests']:
                    file.write(f"- {pr['title']} #{pr['number']}\n")
        except IOError as e:
            LOG.error(f"Error writing to file {file_path}: {e}")
            raise
        return file_path

    def export_progress_by_date_range(self, repo: str, updates: Dict[str, list], days: int) -> str:
        """
        Export progress for a repository over a specific date range.

        :param repo: The repository name.
        :param updates: A dictionary containing 'issues' and 'pull_requests'.
        :param days: The number of days to cover in the report.
        :return: The path to the exported file.
        """
        repo_dir = os.path.join(self.DAILY_PROGRESS_DIR, repo.replace("/", "_"))
        os.makedirs(repo_dir, exist_ok=True)

        today = date.today()
        since = today - timedelta(days=days)
        
        date_str = f"{since}_to_{today}"
        file_path = os.path.join(repo_dir, f'{date_str}.md')
        
        try:
            with open(file_path, 'w') as file:
                file.write(f"# Progress for {repo} ({since} to {today})\n\n")
                file.write(f"\n## Issues Closed in the Last {days} Days\n")
                for issue in updates['issues']:
                    file.write(f"- {issue['title']} #{issue['number']}\n")
                file.write(f"\n## Pull Requests Merged in the Last {days} Days\n")
                for pr in updates['pull_requests']:
                    file.write(f"- {pr['title']} #{pr['number']}\n")
        except IOError as e:
            LOG.error(f"Error writing to file {file_path}: {e}")
            raise
        
        LOG.info(f"Exported time-range progress to {file_path}")
        return file_path

    def generate_daily_report(self, relative_markdown_path: str) -> Tuple[str, str]:
        """
        Generate a daily report from a markdown file.

        :param relative_markdown_path: The relative path to the markdown file from the base directory.
        :return: A tuple containing the report content and the report file path.
        """
        full_markdown_path = self.get_full_path(relative_markdown_path)
        return self._generate_report(full_markdown_path)

    def _generate_report(self, markdown_file_path: str) -> Tuple[str, str]:
        """
        Generate a report from a markdown file.

        :param markdown_file_path: The full path to the markdown file.
        :return: A tuple containing the report content and the report file path.
        """
        try:
            with open(markdown_file_path, 'r') as file:
                markdown_content = file.read()
        except IOError as e:
            LOG.error(f"Error reading file {markdown_file_path}: {e}")
            raise

        # Extract project name and date from the file path
        file_name = os.path.basename(markdown_file_path)
        project_name = os.path.basename(os.path.dirname(markdown_file_path)).replace("_", "/")
        date_str = os.path.splitext(file_name)[0]
        
        try:
            report_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            # If the date is not in the expected format, use today's date
            report_date = datetime.now().date()

        report = self.llm.generate_daily_report(markdown_content, project_name, report_date)

        report_file_path = f"{os.path.splitext(markdown_file_path)[0]}_report.md"
        try:
            with open(report_file_path, 'w') as report_file:
                report_file.write(report)
        except IOError as e:
            LOG.error(f"Error writing to file {report_file_path}: {e}")
            raise

        LOG.info(f"Generated report saved to {report_file_path}")
        
        return report, report_file_path

    def generate_report_by_date_range(self, relative_markdown_path: str, days: int) -> Tuple[str, str]:
        """
        Generate a report for a specific date range from a markdown file.

        :param relative_markdown_path: The relative path to the markdown file from the base directory.
        :param days: The number of days covered in the report.
        :return: A tuple containing the report content and the report file path.
        """
        full_markdown_path = self.get_full_path(relative_markdown_path)
        
        try:
            with open(full_markdown_path, 'r') as file:
                markdown_content = file.read()
        except IOError as e:
            LOG.error(f"Error reading file {full_markdown_path}: {e}")
            raise

        today = date.today()
        since = today - timedelta(days=days)
        
        # Add date range information to the markdown content
        date_range_info = f"\nDate Range: {since} to {today}\n"
        markdown_content = date_range_info + markdown_content

        report = self.llm.generate_daily_report(markdown_content)  # Assuming your LLM can handle the date range

        report_file_path = f"{os.path.splitext(full_markdown_path)[0]}_{since}_to_{today}_report.md"
        try:
            with open(report_file_path, 'w') as report_file:
                report_file.write(report)
        except IOError as e:
            LOG.error(f"Error writing to file {report_file_path}: {e}")
            raise

        LOG.info(f"Generated date range report saved to {report_file_path}")
        
        return report, report_file_path
