#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any, List, Tuple
import re
import os
from datetime import datetime

from ..core.workflow import NovelAgent


class EditorAgent(NovelAgent):
    """文本编辑Agent"""

    def __init__(self):
        super().__init__("editor")
        self.format_issues = {
            "paragraph": "段落过短或过长",
            "punctuation": "标点符号使用不当",
            "spacing": "空格使用不规范",
            "structure": "文章结构不清晰",
        }

    def _format_edit_prompt(self, draft: str) -> str:
        """
        格式化编辑提示

        Args:
            draft: 待编辑的文本

        Returns:
            str: 格式化后的提示文本
        """
        prompt = [
            "请对以下文本进行全面的编辑和润色，重点关注：\n",
            "1. 文字表达：",
            "   - 修正错别字和语法错误",
            "   - 改进不通顺的句子",
            "   - 统一同类词汇的用法",
            "\n2. 标点符号：",
            "   - 规范标点符号使用",
            "   - 处理重复的标点",
            "   - 调整标点的位置",
            "\n3. 段落结构：",
            "   - 优化段落长度",
            "   - 调整段落顺序",
            "   - 确保段落连贯",
            "\n4. 整体风格：",
            "   - 保持文风统一",
            "   - 提升语言优美度",
            "   - 增强表达精确性",
            "\n请返回以下内容：",
            "1. 编辑后的完整文本",
            "2. 编辑报告（包含修改要点和建议）",
            "3. 文本质量评估",
        ]
        return "\n".join(prompt)

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        编辑和润色文本

        Args:
            context: 包含current_draft的上下文

        Returns:
            Dict[str, Any]: 包含编辑后的文本和编辑报告
        """
        self.log_activity("开始", "开始编辑润色")

        try:
            # 获取当前草稿
            draft = context.get("current_draft")
            if not draft:
                raise ValueError("未找到待编辑的草稿")

            # 构建编辑提示
            prompt = self._format_edit_prompt(draft)

            # 请求LLM进行编辑
            edit_response = await self.generate_reply(
                messages=[
                    {"role": "user", "content": prompt + "\n\n待编辑文本：\n" + draft}
                ]
            )

            # 处理编辑结果
            response_text = (
                edit_response.content
                if hasattr(edit_response, "content")
                else edit_response
            )

            # 分离编辑后的文本和报告
            sections = response_text.split("---")
            if len(sections) >= 2:
                edited_text = sections[0].strip()
                edit_report = sections[1].strip()
            else:
                edited_text = response_text
                edit_report = "编辑报告解析失败"

            # 保存最终稿
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "outputs", "drafts"
            )
            os.makedirs(output_dir, exist_ok=True)

            final_file = os.path.join(
                output_dir, f"final_{datetime.now():%Y%m%d_%H%M%S}.txt"
            )

            with open(final_file, "w", encoding="utf-8") as f:
                f.write(edited_text)

            self.log_activity("完成", f"编辑完成，最终稿已保存至: {final_file}")

            return {
                "final_draft": edited_text,
                "edit_report": {"summary": edit_report, "file_path": final_file},
            }

        except Exception as e:
            self.log_activity("错误", f"编辑过程出错: {str(e)}")
            raise

    def _detect_format_issues(self, text: str) -> List[Dict[str, str]]:
        """
        检测格式问题

        Args:
            text: 待检查的文本

        Returns:
            List[Dict[str, str]]: 发现的问题列表
        """
        issues = []

        # 检查段落长度
        paragraphs = text.split("\n\n")
        for i, para in enumerate(paragraphs):
            if len(para.strip()) < 50:  # 段落过短
                issues.append(
                    {
                        "type": "paragraph",
                        "position": f"第{i+1}段",
                        "description": "段落过短，建议合并或扩充",
                    }
                )
            elif len(para.strip()) > 500:  # 段落过长
                issues.append(
                    {
                        "type": "paragraph",
                        "position": f"第{i+1}段",
                        "description": "段落过长，建议适当分段",
                    }
                )

        # 检查标点使用
        punctuation_patterns = {
            r"[，,]{2,}": "重复的逗号",
            r"[。.]{2,}": "重复的句号",
            r"[！!]{2,}": "重复的感叹号",
            r"[？?]{2,}": "重复的问号",
            r"[，。！？][的地得]": "标点后接的地得不当",
        }

        for pattern, desc in punctuation_patterns.items():
            matches = list(re.finditer(pattern, text))
            for match in matches:
                issues.append(
                    {
                        "type": "punctuation",
                        "position": f"位置{match.start()}",
                        "description": desc,
                    }
                )

        return issues
