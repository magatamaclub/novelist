#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any, List
import yaml
import os
from datetime import datetime

from ..core.workflow import NovelAgent


class CreatorAgent(NovelAgent):
    """故事创意生成器"""

    def __init__(self):
        super().__init__("creator")

    def _format_outline_prompt(self, seed: Dict[str, Any]) -> str:
        """
        格式化大纲生成提示

        Args:
            seed: 故事种子配置

        Returns:
            str: 格式化后的提示文本
        """
        prompt = [
            "请根据以下要素创作一个详细的故事大纲：\n",
            f"标题：{seed['title']}",
            f"主题：{seed['theme']}",
            "\n场景设定：",
            f"- 时代背景：{seed['settings']['time']}",
            f"- 地点：{seed['settings']['location']}",
            f"- 季节：{seed['settings']['season']}",
            "\n主要人物：",
        ]

        for char in seed["characters"]:
            prompt.extend(
                [
                    f"\n{char['name']}（{char['role']}）：",
                    f"- 年龄：{char['age']}",
                    f"- 职业：{char['occupation']}",
                    f"- 性格特征：{', '.join(char['traits'])}",
                    f"- 背景：{char['background']}",
                ]
            )

        prompt.extend(
            [
                "\n冲突要素：",
                "\n".join(
                    f"- {conflict}" for conflict in seed["plot_elements"]["conflicts"]
                ),
                "\n关键场景：",
                "\n".join(
                    f"- {scene}" for scene in seed["plot_elements"]["key_scenes"]
                ),
                "\n写作风格：",
                f"- 基调：{seed['style_preferences']['tone']}",
                f"- 节奏：{seed['style_preferences']['pacing']}",
                f"- 叙事视角：{seed['style_preferences']['narrative']}",
                f"- 重点：{seed['style_preferences']['focus']}",
            ]
        )

        return "\n".join(prompt)

    def _generate_chapter_structure(
        self, key_scenes: List[str]
    ) -> List[Dict[str, Any]]:
        """
        生成章节结构

        Args:
            key_scenes: 关键场景列表

        Returns:
            List[Dict[str, Any]]: 章节结构列表
        """
        chapters = []
        scene_count = len(key_scenes)

        # 生成约10章的结构
        chapter_count = min(max(scene_count * 2, 8), 12)

        # 分配关键场景到章节
        scenes_per_chapter = scene_count / chapter_count

        for i in range(chapter_count):
            scene_index = int(i * scenes_per_chapter)
            chapters.append(
                {
                    "chapter": i + 1,
                    "title": f"第{i + 1}章",  # 实际标题将由LLM生成
                    "key_points": (
                        [key_scenes[scene_index]] if scene_index < scene_count else []
                    ),
                    "summary": "",  # 章节概要将由LLM生成
                }
            )

        return chapters

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成故事大纲

        Args:
            context: 包含story_seed的上下文信息

        Returns:
            Dict[str, Any]: 生成的故事大纲
        """
        self.log_activity("开始", "开始生成故事大纲")

        try:
            # 获取故事种子
            seed = context.get("story_seed")
            if not seed:
                raise ValueError("未找到故事种子配置")

            # 构建提示
            prompt = self._format_outline_prompt(seed)

            # 调用LLM生成大纲
            outline_response = await self.generate_reply(
                messages=[{"role": "user", "content": prompt}]
            )

            # 使用LLM生成的大纲创建结构化输出
            chapters = self._generate_chapter_structure(
                seed["plot_elements"]["key_scenes"]
            )

            # 组装大纲数据
            outline = {
                "title": seed["title"],
                "theme": seed["theme"],
                "settings": seed["settings"],
                "characters": seed["characters"],
                "chapters": chapters,
                "style": seed["style_preferences"],
            }

            # 保存大纲
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "outputs", "outlines"
            )
            os.makedirs(output_dir, exist_ok=True)

            outline_file = os.path.join(
                output_dir, f"outline_{datetime.now():%Y%m%d_%H%M%S}.yaml"
            )

            with open(outline_file, "w", encoding="utf-8") as f:
                yaml.dump(outline, f, allow_unicode=True, sort_keys=False)

            self.log_activity("完成", f"大纲已保存至: {outline_file}")

            return {"outline": outline}

        except Exception as e:
            self.log_activity("错误", f"大纲生成失败: {str(e)}")
            raise
