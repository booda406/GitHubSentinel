import smtplib
import markdown2
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from logger import LOG

class Notifier:
    def __init__(self, email_settings, slack_webhook_url=None):
        self.email_settings = email_settings
        self.slack_webhook_url = slack_webhook_url

    def notify(self, repo, report):
        if self.email_settings:
            self.send_email(repo, report)
        else:
            LOG.warning("邮件设置未配置正确，无法发送邮件通知")

        if self.slack_webhook_url:
            self.send_slack_message(repo, report)
        else:
            LOG.warning("Slack Webhook URL 未配置，无法发送 Slack 通知")

    def send_email(self, repo, report):
        LOG.info("准备发送邮件")
        msg = MIMEMultipart()
        msg['From'] = self.email_settings['from']
        msg['To'] = self.email_settings['to']
        msg['Subject'] = f"[GitHubSentinel]{repo} 进展简报"

        # 将Markdown内容转换为HTML
        html_report = markdown2.markdown(report)

        msg.attach(MIMEText(html_report, 'html'))
        try:
            with smtplib.SMTP_SSL(self.email_settings['smtp_server'], self.email_settings['smtp_port']) as server:
                LOG.debug("登录SMTP服务器")
                server.login(msg['From'], self.email_settings['password'])
                server.sendmail(msg['From'], msg['To'], msg.as_string())
                LOG.info("邮件发送成功！")
        except Exception as e:
            LOG.error(f"发送邮件失败：{str(e)}")

    def send_slack_message(self, repo, report):
        LOG.info("准备发送 Slack 消息")

        # 将 Markdown 报告转换为 Slack 消息格式
        slack_message = self.format_slack_message(repo, report)

        try:
            response = requests.post(
                self.slack_webhook_url,
                json={"text": slack_message}
            )
            response.raise_for_status()
            LOG.info("Slack 消息发送成功！")
        except requests.RequestException as e:
            LOG.error(f"发送 Slack 消息失败：{str(e)}")

    def format_slack_message(self, repo, report):
        # 将 Markdown 报告转换为 Slack 消息格式
        # 这里我们只做了一个简单的转换，你可以根据需要进行更复杂的格式化
        slack_message = f"*[GitHubSentinel] {repo} 进展简报*\n\n"
        slack_message += report.replace("# ", "*").replace("## ", "*")
        return slack_message

if __name__ == '__main__':
    from config import Config
    config = Config()
    notifier = Notifier(config.email, config.slack_webhook_url)

    test_repo = "DjangoPeng/openai-quickstart"
    test_report = """
# DjangoPeng/openai-quickstart 项目进展

## 时间周期：2024-08-24

## 新增功能
- Assistants API 代码与文档

## 主要改进
- 适配 LangChain 新版本

## 修复问题
- 关闭了一些未解决的问题。
"""
    notifier.notify(test_repo, test_report)
