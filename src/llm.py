import os
import json
from openai import OpenAI  # 导入OpenAI库用于访问GPT模型
from logger import LOG  # 导入日志模块
import re

class LLM:
    def __init__(self):
        # 创建一个OpenAI客户端实例
        self.client = OpenAI()
        # 从TXT文件加载提示信息
        with open("prompts/report_prompt.txt", "r", encoding='utf-8') as file:
            self.system_prompt = file.read()
        # 配置日志文件，当文件大小达到1MB时自动轮转，日志级别为DEBUG
        LOG.add("logs/llm_logs.log", rotation="1 MB", level="DEBUG")

    def extract_project_info(self, markdown_content):
        # 使用正則表達式從 markdown_content 提取項目名稱和日期範圍
        match = re.search(r"# Progress for (.+) \((.+)\)", markdown_content)
        if match:
            project_name = match.group(1)
            date_range = match.group(2)
            return project_name, date_range
        else:
            LOG.warning("Could not extract project name and date range from markdown content.")
            return "Unknown Project", "Unknown Date Range"

    def generate_daily_report(self, markdown_content, dry_run=False):
        project_name, report_date = self.extract_project_info(markdown_content)

        user_prompt = f"""
        任務：為 GitHub 項目 {project_name} 生成 {report_date} 的中文日報。

        背景：
        - 項目名稱：{project_name}
        - 報告日期：{report_date}
        - 項目描述：[這裡可以添加項目的簡短描述，如果有的話]
        - 目的：總結項目的最新進展，分析變更的影響，並提供洞見

        請首先生成一個簡要的日報大綱，然後我們將基於這個大綱進行詳細擴展。

        輸入：
        ```
        {markdown_content}
        ```

        大綱格式：
        1. 摘要
        2. 詳細分析
           2.1 新增功能
           2.2 主要改進
           2.3 問題修復
           2.4 其他變更
        3. 影響評估
        4. 未來展望
        5. 總結

        請根據輸入內容生成這個大綱，每個部分只需要列出關鍵點。
        """

        if dry_run:
            LOG.info("Dry run mode enabled. Saving prompt to file.")
            with open("daily_progress/prompt.txt", "w+", encoding='utf-8') as f:
                json.dump([
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ], f, indent=4, ensure_ascii=False)
            LOG.debug("Prompt saved to daily_progress/prompt.txt")
            return "DRY RUN"

        LOG.info("Starting report outline generation using GPT model.")

        try:
            outline_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            outline = outline_response.choices[0].message.content

            detailed_prompt = f"""
            非常好，現在請基於以下大綱生成詳細的日報。請確保每個部分都有充分的內容和深入的分析。

            {outline}

            在擴展這個大綱時，請遵循以下指導原則：
            1. 深入分析：不僅描述變更，還要解釋其重要性和潛在影響。
            2. 上下文關聯：將變更與項目的整體目標和之前的發展聯繫起來。
            3. 平衡詳細度：提供足夠的技術細節，但保持報告對非技術讀者也易於理解。
            4. 技術準確性：確保所有技術描述準確無誤。
            5. 建設性意見：在適當的地方提供建設性的建議或觀察。
            6. 使用繁體中文。

            如果某個部分沒有相關更新，請標明「本次更新無相關內容」並簡要解釋原因。

            請生成一份詳細的中文日報，格式為 Markdown。
            """

            LOG.info("Starting detailed report generation using GPT model.")

            detailed_response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt},
                    {"role": "assistant", "content": outline},
                    {"role": "user", "content": detailed_prompt}
                ],
                temperature=0.3
            )

            LOG.debug("GPT response: {}", detailed_response)
            return detailed_response.choices[0].message.content
        except Exception as e:
            LOG.error("An error occurred while generating the report: {}", e)
            raise