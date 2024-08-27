import gradio as gr
import os
from config import Config
from github_client import GitHubClient
from report_generator import ReportGenerator
from llm import LLM
from subscription_manager import SubscriptionManager
from logger import LOG
import random
import tempfile

# 創建各個組件的實例
config = Config()
github_client = GitHubClient(config.github_token)
llm = LLM()
report_generator = ReportGenerator(llm)
subscription_manager = SubscriptionManager(config.subscriptions_file)

def export_progress_by_date_range(repo, days):
    try:
        raw_file_path = github_client.export_progress_by_date_range(repo, days)
        report, report_file_path = report_generator.generate_report_by_date_range(raw_file_path, days)
        return report, report_file_path
    except Exception as e:
        LOG.error(f"Error in export_progress_by_date_range: {str(e)}")
        raise

def generate_report(repo, days):
    try:
        LOG.info(f"Generating report for repo: {repo}, days: {days}")
        report, report_file_path = export_progress_by_date_range(repo, days)
        LOG.info(f"Generated report file: {report_file_path}")
        return report, gr.update(visible=True), report_file_path
    except Exception as e:
        LOG.error(f"Error generating report: {str(e)}")
        return f"生成報告時出錯: {str(e)}", gr.update(visible=False), None

def validate_inputs(repo, days):
    if not repo:
        return "請選擇一個 GitHub 項目", gr.update(visible=False)
    if days < 1 or days > 30:
        return "請選擇 1 到 30 天之間的時間範圍", gr.update(visible=False)
    return None, gr.update(visible=False)

with gr.Blocks(title="GitHub 項目進度報告生成器", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# GitHub 項目進度報告生成器")
    
    with gr.Row():
        with gr.Column(scale=2):
            repo = gr.Dropdown(subscription_manager.list_subscriptions(),
                label="選擇 GitHub 項目",
                info="從已訂閱的項目中選擇")
            days = gr.Slider(minimum=1, maximum=30, value=1, step=1, label="報告時間範圍 (天)")
            generate_btn = gr.Button("生成報告")
            with gr.Accordion("使用說明", open=False):
                gr.Markdown("""
                1. 在下拉菜單中選擇或輸入 GitHub 項目名稱（格式：用戶名/項目名）
                2. 使用滑塊選擇要分析的時間範圍（1-30天）
                3. 點擊"生成報告"按鈕
                4. 等待報告生成完成
                5. 在右側查看報告預覽，並使用下方的"下載完整報告"按鈕獲取完整報告
                """)
            download_btn = gr.DownloadButton("下載完整報告", visible=False)
            error_output = gr.Textbox(label="錯誤信息", visible=False)
        
        with gr.Column(scale=3):
            output = gr.Markdown(label="報告預覽")

    generate_btn.click(
        fn=validate_inputs,
        inputs=[repo, days],
        outputs=[error_output, download_btn]
    ).success(
        fn=generate_report,
        inputs=[repo, days],
        outputs=[output, download_btn, download_btn],
        show_progress=True
    )

if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0")
    # 可選帶有用戶認證的啟動方式
    # demo.launch(share=True, server_name="0.0.0.0", auth=("username", "password"))
