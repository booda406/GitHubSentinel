import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

# Add src directory to module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from config import Config  # Import the Config class
from notifier import Notifier  # Import the Notifier class
from logger import LOG  # Import the logger

class TestNotifier(unittest.TestCase):
    def setUp(self):
        """
        Run before each test method to initialize Notifier instance and test data, and set up log capture.
        """
        self.config = Config()
        self.notifier = Notifier(self.config.email, self.config.slack_webhook_url)
        self.test_repo = "DjangoPeng/openai-quickstart"
        self.test_github_report = """
        # DjangoPeng/openai-quickstart 项目进展

        ## 时间周期：2024-08-24

        ## 新增功能
        - Assistants API 代码与文档

        ## 主要改进
        - 适配 LangChain 新版本

        ## 修复问题
        - 关闭了一些未解决的问题。
        """
        self.test_hn_report = """
        # Hacker News 前沿技术趋势 (2024-09-01)

        ## Top 1：硬盘驱动器的讨论引发热门讨论
        """
        self.test_linkedin_report = """
        # LinkedIn Job Listings

        ## Date: 2024-09-01

        ## New Jobs
        - Software Engineer at LinkedIn
        - Data Scientist at NVIDIA
        """

        # Set up log capture
        self.log_capture = StringIO()
        self.capture_id = LOG.add(self.log_capture, level="INFO")

    def tearDown(self):
        """
        Run after each test method to remove log capture.
        """
        LOG.remove(self.capture_id)
        self.log_capture.close()

    @patch('smtplib.SMTP_SSL')
    def test_notify_github_report_success(self, mock_smtp):
        """
        Test if GitHub report email is successfully sent when email settings are correct, and check log output.
        """
        # Execute email sending
        self.notifier.notify_github_report(self.test_repo, self.test_github_report)

        # Get and check log content
        log_content = self.log_capture.getvalue()
        self.assertIn("邮件发送成功！", log_content)

    @patch('smtplib.SMTP_SSL')
    def test_notify_hn_report_success(self, mock_smtp):
        """
        Test if Hacker News report email is successfully sent when email settings are correct, and check log output.
        """
        # Execute email sending
        self.notifier.notify_hn_report("2024-09-01", self.test_hn_report)

        # Get and check log content
        log_content = self.log_capture.getvalue()
        self.assertIn("邮件发送成功！", log_content)

    @patch('requests.post')
    def test_notify_linkedin_report_success(self, mock_post):
        """
        Test if LinkedIn report Slack message is successfully sent when Slack webhook URL is provided, and check log output.
        """
        # Mock Slack API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Execute Slack notification
        self.notifier.notify_linkedin_report(self.test_linkedin_report)

        # Get and check log content
        log_content = self.log_capture.getvalue()
        self.assertIn("LinkedIn Slack 消息发送成功！", log_content)

    def test_notify_without_email_settings(self):
        """
        Test if Notifier does not send email and logs a warning when email settings are not configured correctly.
        """
        faulty_notifier = Notifier(None)
        faulty_notifier.notify_github_report(self.test_repo, self.test_github_report)

        log_content = self.log_capture.getvalue()
        self.assertIn("邮件设置未配置正确", log_content)

    def test_notify_without_slack_webhook(self):
        """
        Test if Notifier does not send Slack message and logs a warning when Slack webhook URL is not configured.
        """
        faulty_notifier = Notifier(self.config.email, None)
        faulty_notifier.notify_linkedin_report(self.test_linkedin_report)

        log_content = self.log_capture.getvalue()
        self.assertIn("Slack Webhook URL 未配置", log_content)

if __name__ == '__main__':
    unittest.main()
