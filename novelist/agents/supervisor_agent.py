#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any, List
import json

from ..core.workflow import NovelAgent


class SupervisorAgent(NovelAgent):
    """故事监制Agent"""

    def __init__(self):
        super().__init__("supervisor")

    def _format_review_prompt(self, draft: str, outline: Dict[str, Any]) -> str:
        """
        格式化审查提示

        Args:
            draft: 小说草稿
            outline: 故事大纲

        Returns:
            str: 格式化后的提示文本
        """
        prompt = [
            f"请对《{outline['title']}》进行全面审查，重点关注以下方面：\n",
            "1. 情节连贯性：",
            "   - 故事是否按照大纲发展",
            "   - 情节转折是否合理",
            "   - 是否存在逻辑漏洞",
            "\n2. 人物塑造：",
            "   - 人物性格是否前后一致",
            "   - 人物行为是否符合其设定",
            "   - 人物发展是否合理",
            "\n3. 叙事结构：",
            "   - 故事节奏是否合适",
            "   - 各章节是否衔接自然",
            "   - 重要情节是否得到充分展现",
            "\n4. 写作风格：",
            f"   - 是否符合'{outline['style']['tone']}'的基调",
            f"   - 是否保持了'{outline['style']['pacing']}'的节奏",
            f"   - 是否贯彻了'{outline['style']['narrative']}'的视角",
            "\n请以JSON格式输出审查结果，包含以下字段：",
            "- approved: 是否通过审核（boolean）",
            "- issues: 发现的具体问题列表",
            "- suggestions: 改进建议列表",
            "- comments: 其他评审意见",
        ]
        return "\n".join(prompt)

    def _parse_review_response(self, response: str) -> Dict[str, Any]:
        """
        解析LLM的审核回复

        Args:
            response: LLM的原始回复

        Returns:
            Dict[str, Any]: 解析后的审核结果
        """
        try:
            # 提取JSON部分
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1]

            result = json.loads(json_str)

            # 确保所有必要字段都存在
            required_fields = ["approved", "issues", "suggestions", "comments"]
            for field in required_fields:
                if field not in result:
                    result[field] = []
                    if field == "approved":
                        result[field] = False

            return result

        except Exception as e:
            self.log_activity("警告", f"审核结果解析失败: {str(e)}，使用默认结构")
            return {
                "approved": False,
                "issues": ["审核结果解析失败"],
                "suggestions": ["请重新生成内容"],
                "comments": [str(e)],
            }

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        审核小说内容

        Args:
            context: 包含outline和current_draft的上下文

        Returns:
            Dict[str, Any]: 审核结果
        """
        self.log_activity("开始", "开始审核小说内容")

        try:
            # 获取当前草稿和大纲
            draft = context.get("current_draft")
            outline = context.get("outline")

            if not draft or not outline:
                raise ValueError("缺少待审核的草稿或大纲")

            # 构建审核提示
            prompt = self._format_review_prompt(draft, outline)

            # 调用LLM进行审核
            review_response = await self.generate_reply(
                messages=[
                    {"role": "user", "content": prompt + "\n\n待审核内容：\n" + draft}
                ]
            )

            # 解析审核结果
            review_result = self._parse_review_response(
                review_response.content
                if hasattr(review_response, "content")
                else review_response
            )

            # 记录审核结果
            if review_result["approved"]:
                self.log_activity("完成", "审核通过")
            else:
                issues_count = len(review_result["issues"])
                self.log_activity("完成", f"审核未通过，发现{issues_count}个问题")

            return review_result

        except Exception as e:
            self.log_activity("错误", f"审核过程出错: {str(e)}")
            raise
