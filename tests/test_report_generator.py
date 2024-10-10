import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add src directory to module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from report_generator import ReportGenerator  # Import the ReportGenerator class

class TestReportGenerator(unittest.TestCase):
    def setUp(self):
        """
        Run before each test method to initialize the test environment.
        """
        # Create a mock LLM (Large Language Model) object
        self.mock_llm = MagicMock()
        self.mock_llm.model = "mock_model"  # Ensure the mock object has a valid model name

        # Mock prompt contents
        self.mock_prompts = {
            "github": "GitHub specific prompt...",
            "hacker_news_hours_topic": "Hacker News topic specific prompt...",
            "hacker_news_daily_report": "Hacker News daily summary prompt...",
            "linkedin": "LinkedIn specific prompt..."
        }

        # Set up test Markdown file paths
        self.test_markdown_file_path = 'test_daily_progress.md'
        self.test_hn_topic_file_path = 'test_hn_topic.md'
        self.test_hn_daily_dir_path = 'test_hn_daily_dir'
        self.test_linkedin_file_path = 'test_linkedin_jobs.md'

        # Mock Markdown content representing daily project progress
        self.markdown_content = """
        # Daily Progress for DjangoPeng/openai-quickstart (2024-08-24)

        ## Issues Closed Today
        - Fix bug #123
        """

        # Create test Markdown files and directories
        with open(self.test_markdown_file_path, 'w') as file:
            file.write(self.markdown_content)

        with open(self.test_hn_topic_file_path, 'w') as file:
            file.write(self.markdown_content)

        os.makedirs(self.test_hn_daily_dir_path, exist_ok=True)
        self.hn_topic_report_path = os.path.join(self.test_hn_daily_dir_path, "test_topic_01_topic.md")
        with open(self.hn_topic_report_path, 'w') as file:
            file.write(self.markdown_content)

        with open(self.test_linkedin_file_path, 'w') as file:
            file.write(self.markdown_content)

    def tearDown(self):
        """
        Run after each test method to clean up the test environment.
        """
        # Remove test Markdown files
        if os.path.exists(self.test_markdown_file_path):
            os.remove(self.test_markdown_file_path)
        if os.path.exists(self.test_hn_topic_file_path):
            os.remove(self.test_hn_topic_file_path)
        if os.path.exists(self.test_linkedin_file_path):
            os.remove(self.test_linkedin_file_path)

        # Remove generated report files
        report_file_path = os.path.splitext(self.test_markdown_file_path)[0] + "_report.md"
        if os.path.exists(report_file_path):
            os.remove(report_file_path)

        hn_topic_report_path = os.path.splitext(self.test_hn_topic_file_path)[0] + "_topic.md"
        if os.path.exists(hn_topic_report_path):
            os.remove(hn_topic_report_path)

        hn_daily_report_path = os.path.join("hacker_news/tech_trends/", f"{os.path.basename(self.test_hn_daily_dir_path)}_trends.md")
        if os.path.exists(hn_daily_report_path):
            os.remove(hn_daily_report_path)

        linkedin_report_path = os.path.splitext(self.test_linkedin_file_path)[0] + "_linkedin_report.md"
        if os.path.exists(linkedin_report_path):
            os.remove(linkedin_report_path)

        # Remove Hacker News test directory
        if os.path.exists(self.test_hn_daily_dir_path):
            for file in os.listdir(self.test_hn_daily_dir_path):
                os.remove(os.path.join(self.test_hn_daily_dir_path, file))
            os.rmdir(self.test_hn_daily_dir_path)

    @patch.object(ReportGenerator, '_preload_prompts', return_value=None)
    def test_generate_github_report(self, mock_preload_prompts):
        """
        Test if generate_github_report method correctly generates and saves the report.
        """
        # Initialize ReportGenerator instance and manually set prompts
        self.report_generator = ReportGenerator(self.mock_llm, ["github", "hacker_news_hours_topic", "hacker_news_daily_report", "linkedin"])
        self.report_generator.prompts = self.mock_prompts

        # Mock the report content returned by the LLM
        mock_report = "This is a generated report."
        self.mock_llm.generate_report.return_value = mock_report

        # Call generate_github_report method
        report, report_file_path = self.report_generator.generate_github_report(self.test_markdown_file_path)

        # Verify the return values
        self.assertEqual(report, mock_report)
        self.assertTrue(report_file_path.endswith("_report.md"))

        # Verify the content of the generated report file
        with open(report_file_path, 'r') as file:
            content = file.read()
            self.assertEqual(content, mock_report)

        # Verify that the LLM's generate_report method was called with the correct parameters
        self.mock_llm.generate_report.assert_called_once_with(self.mock_prompts["github"], self.markdown_content)

    @patch.object(ReportGenerator, '_preload_prompts', return_value=None)
    def test_generate_hn_topic_report(self, mock_preload_prompts):
        """
        Test if generate_hn_topic_report method correctly generates and saves the report.
        """
        # Initialize ReportGenerator instance and manually set prompts
        self.report_generator = ReportGenerator(self.mock_llm, ["github", "hacker_news_hours_topic", "hacker_news_daily_report", "linkedin"])
        self.report_generator.prompts = self.mock_prompts

        # Mock the report content returned by the LLM
        mock_report = "This is a generated Hacker News topic report."
        self.mock_llm.generate_report.return_value = mock_report

        # Call generate_hn_topic_report method
        report, report_file_path = self.report_generator.generate_hn_topic_report(self.test_hn_topic_file_path)

        # Verify the return values
        self.assertEqual(report, mock_report)
        self.assertTrue(report_file_path.endswith("_topic.md"))

        # Verify the content of the generated report file
        with open(report_file_path, 'r') as file:
            content = file.read()
            self.assertEqual(content, mock_report)

        # Verify that the LLM's generate_report method was called with the correct parameters
        self.mock_llm.generate_report.assert_called_once_with(self.mock_prompts["hacker_news_hours_topic"], self.markdown_content)

    @patch.object(ReportGenerator, '_preload_prompts', return_value=None)
    def test_generate_hn_daily_report(self, mock_preload_prompts):
        """
        Test if generate_hn_daily_report method correctly generates the daily summary report and saves it to a file.
        """
        # Initialize ReportGenerator instance and manually set prompts
        self.report_generator = ReportGenerator(self.mock_llm, ["github", "hacker_news_hours_topic", "hacker_news_daily_report", "linkedin"])
        self.report_generator.prompts = self.mock_prompts

        # Mock the report content returned by the LLM
        mock_report = "This is a generated Hacker News daily trends report."
        self.mock_llm.generate_report.return_value = mock_report

        # Call generate_hn_daily_report method
        report, report_file_path = self.report_generator.generate_hn_daily_report(self.test_hn_daily_dir_path)

        # Verify the return values
        self.assertEqual(report, mock_report)
        self.assertTrue(report_file_path.endswith("_trends.md"))

        # Verify the content of the generated report file
        with open(report_file_path, 'r') as file:
            content = file.read()
            self.assertEqual(content, mock_report)

        # Verify that the LLM's generate_report method was called with the correct parameters
        aggregated_content = self.report_generator._aggregate_topic_reports(self.test_hn_daily_dir_path)
        self.mock_llm.generate_report.assert_called_once_with(self.mock_prompts["hacker_news_daily_report"], aggregated_content)

    @patch.object(ReportGenerator, '_preload_prompts', return_value=None)
    def test_generate_linkedin_report(self, mock_preload_prompts):
        """
        Test if generate_linkedin_report method correctly generates and saves the LinkedIn report.
        """
        # Initialize ReportGenerator instance and manually set prompts
        self.report_generator = ReportGenerator(self.mock_llm, ["github", "hacker_news_hours_topic", "hacker_news_daily_report", "linkedin"])
        self.report_generator.prompts = self.mock_prompts

        # Mock the report content returned by the LLM
        mock_report = "This is a generated LinkedIn report."
        self.mock_llm.generate_report.return_value = mock_report

        # Call generate_linkedin_report method
        report, report_file_path = self.report_generator.generate_linkedin_report(self.test_linkedin_file_path)

        # Verify the return values
        self.assertEqual(report, mock_report)
        self.assertTrue(report_file_path.endswith("_linkedin_report.md"))

        # Verify the content of the generated report file
        with open(report_file_path, 'r') as file:
            content = file.read()
            self.assertEqual(content, mock_report)

        # Verify that the LLM's generate_report method was called with the correct parameters
        self.mock_llm.generate_report.assert_called_once_with(self.mock_prompts["linkedin"], self.markdown_content)

if __name__ == '__main__':
    unittest.main()
