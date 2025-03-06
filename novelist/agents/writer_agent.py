#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any, List
import os
from datetime import datetime

from ..core.workflow import NovelAgent


class WriterAgent(NovelAgent):
    """小说创作Agent"""

    def __init__(self):
        super().__init__("writer")

    def _format_chapter_prompt(
        self, chapter: Dict[str, Any], outline: Dict[str, Any]
    ) -> str:
        """
        格式化章节写作提示

        Args:
            chapter: 章节信息
            outline: 故事大纲

        Returns:
            str: 格式化后的提示文本
        """
        prompt = [
            f"请根据以下要素创作《{outline['title']}》第{chapter['chapter']}章的内容：\n",
            f"章节标题：{chapter['title']}",
            "\n故事背景：",
            f"- 时代：{outline['settings']['time']}",
            f"- 地点：{outline['settings']['location']}",
            f"- 季节：{outline['settings']['season']}",
            "\n写作要求：",
            f"- 风格基调：{outline['style']['tone']}",
            f"- 叙事节奏：{outline['style']['pacing']}",
            f"- 叙述视角：{outline['style']['narrative']}",
            f"- 表现重点：{outline['style']['focus']}",
            "\n本章关键情节：",
        ]

        for point in chapter["key_points"]:
            prompt.append(f"- {point}")

        prompt.extend(["\n人物信息："])

        for char in outline["characters"]:
            prompt.extend(
                [
                    f"\n{char['name']}：",
                    f"- 角色：{char['role']}",
                    f"- 性格：{', '.join(char['traits'])}",
                ]
            )

        return "\n".join(prompt)

    async def _generate_chapter_content(
        self, chapter: Dict[str, Any], outline: Dict[str, Any]
    ) -> str:
        """
        生成章节内容

        Args:
            chapter: 章节信息
            outline: 故事大纲

        Returns:
            str: 生成的章节内容
        """
        # 构建写作提示
        prompt = self._format_chapter_prompt(chapter, outline)

        # 请求LLM生成内容
        response = await self.generate_reply(
            messages=[{"role": "user", "content": prompt}]
        )

        # 格式化章节内容
        content = [
            f"# 第{chapter['chapter']}章 {chapter['title']}\n",
            response.content if hasattr(response, "content") else response,
            "\n" + "=" * 50 + "\n",  # 章节分隔符
        ]

        return "\n".join(content)

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        创作小说内容

        Args:
            context: 包含outline和前轮反馈（如果有）的上下文

        Returns:
            Dict[str, Any]: 创作的小说内容
        """
        self.log_activity("开始", "开始创作小说内容")

        try:
            # 获取大纲
            outline = context.get("outline")
            if not outline:
                raise ValueError("未找到故事大纲")

            # 获取之前的反馈（如果有）
            feedback = context.get("feedback", {})
            if feedback:
                self.log_activity("信息", f"处理审阅反馈: {feedback}")

            # 生成小说内容
            draft = []
            for chapter in outline["chapters"]:
                self.log_activity("进行", f"创作第{chapter['chapter']}章")
                chapter_content = await self._generate_chapter_content(chapter, outline)
                draft.append(chapter_content)

            # 合并所有章节
            complete_draft = "\n".join(
                [f"# {outline['title']}\n", f"作者：AI写手\n", "---\n", *draft]
            )

            # 保存草稿
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "outputs", "drafts"
            )
            os.makedirs(output_dir, exist_ok=True)

            draft_file = os.path.join(
                output_dir, f"draft_{datetime.now():%Y%m%d_%H%M%S}.txt"
            )

            with open(draft_file, "w", encoding="utf-8") as f:
                f.write(complete_draft)

            self.log_activity("完成", f"创作完成，草稿已保存至: {draft_file}")
            return {"current_draft": complete_draft}

        except Exception as e:
            self.log_activity("错误", f"创作过程出错: {str(e)}")
            raise
