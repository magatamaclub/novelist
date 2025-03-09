#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any, List, Optional, Union
from ..core.adapter import NovelAgentAdapter, Message


class CreatorAgent(NovelAgentAdapter):
    """故事创意生成器，负责构思故事大纲和创意方向"""

    def __init__(self):
        super().__init__("creator")

        # 注册消息处理回调
        self.register_reply(
            trigger=["我们开始创作一个新故事", "需要一个故事大纲"],
            reply_func=self._generate_outline,
        )
        self.register_reply(
            trigger=["修改大纲", "调整故事方向"],
            reply_func=self._revise_outline,
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

    async def _generate_outline(
        self, message: Dict[str, Any], sender: Any
    ) -> Union[str, Dict[str, Any]]:
        """生成初始故事大纲"""
        self.log_activity("开始", "正在构思故事大纲")

        response_text = """作为创意生成者，我将：
1. 分析故事主题和核心要素
2. 设计引人入胜的情节架构
3. 规划故事的起承转合
4. 设计关键场景和转折点
5. 确保故事结构的完整性

让我们开始构思这个故事..."""

        # 当需要详细元数据时返回字典
        if message.get("require_metadata"):
            return {
                "role": "assistant",
                "content": response_text,
                "metadata": {"action": "generate_outline", "status": "completed"},
            }

        # 默认返回字符串响应
        return response_text

    async def _revise_outline(
        self, message: Dict[str, Any], sender: Any
    ) -> Union[str, Dict[str, Any]]:
        """根据反馈修改大纲"""
        self.log_activity("修改", "正在调整故事大纲")

        response_text = """基于反馈意见，我将：
1. 重新审视故事结构
2. 调整情节发展
3. 优化人物设定
4. 加强故事主题
5. 完善细节描写

开始修改大纲..."""

        # 当需要详细元数据时返回字典
        if message.get("require_metadata"):
            return {
                "role": "assistant",
                "content": response_text,
                "metadata": {"action": "revise_outline", "status": "completed"},
            }

        # 默认返回字符串响应
        return response_text

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行创意生成任务"""
        self.log_activity("执行", "创意生成器就绪")
        return {
            "status": "ready",
            "agent_type": "creator",
            "capabilities": ["outline_generation", "story_planning"],
        }
