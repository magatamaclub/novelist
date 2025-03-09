#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any, List, Optional, Union
from ..core.adapter import NovelAgentAdapter, Message


class WriterAgent(NovelAgentAdapter):
    """小说写作者，负责根据大纲进行具体写作"""

    def __init__(self):
        super().__init__("writer")

        # 注册消息处理回调
        self.register_reply(
            trigger=["开始写作", "根据大纲写作", "撰写故事"],
            reply_func=self._write_story,
        )
        self.register_reply(
            trigger=["修改内容", "调整文字", "优化段落"],
            reply_func=self._revise_content,
        )

    async def handle_message(
        self, message: Message, sender: Optional["NovelAgentAdapter"] = None
    ) -> Optional[str]:
        """
        实现基类的消息处理方法

        Args:
            message: 接收到的消息
            sender: 消息发送者

        Returns:
            处理后的回复
        """
        content = message.content.lower()
        for pattern, handler in self._message_handlers.items():
            if pattern.lower() in content:
                response = await handler({"content": content}, sender)
                if isinstance(response, dict):
                    return response["content"]
                return response
        return None

    async def _write_story(
        self, message: Dict[str, Any], sender: Any
    ) -> Union[str, Dict[str, Any]]:
        """根据大纲进行写作"""
        self.log_activity("写作", "开始根据大纲创作故事")

        response_text = """作为故事写作者，我会：
1. 仔细分析大纲结构
2. 展开情节细节
3. 塑造生动的人物形象
4. 描绘丰富的场景
5. 打磨文字表达

开始进行写作..."""

        # 当需要详细元数据时返回字典
        if message.get("require_metadata"):
            return {
                "role": "assistant",
                "content": response_text,
                "metadata": {"action": "write_story", "status": "in_progress"},
            }

        # 默认返回字符串响应
        return response_text

    async def _revise_content(
        self, message: Dict[str, Any], sender: Any
    ) -> Union[str, Dict[str, Any]]:
        """修改和优化内容"""
        self.log_activity("修改", "开始修改和优化内容")

        response_text = """收到修改建议，我将：
1. 优化段落结构
2. 提升描写细节
3. 增强情节张力
4. 改进对话内容
5. 完善文字表达

开始进行修改..."""

        # 当需要详细元数据时返回字典
        if message.get("require_metadata"):
            return {
                "role": "assistant",
                "content": response_text,
                "metadata": {"action": "revise_content", "status": "in_progress"},
            }

        # 默认返回字符串响应
        return response_text

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行写作任务"""
        self.log_activity("执行", "写作者就绪")
        return {
            "status": "ready",
            "agent_type": "writer",
            "capabilities": ["story_writing", "content_revision"],
        }
