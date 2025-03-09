#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any, List, Optional, Union
from ..core.adapter import NovelAgentAdapter, Message


class SupervisorAgent(NovelAgentAdapter):
    """故事审核者，负责审查故事质量和提供修改建议"""

    def __init__(self):
        super().__init__("supervisor")

        # 注册消息处理回调
        self.register_reply(
            trigger=["审查内容", "评估故事", "检查质量"],
            reply_func=self._review_content,
        )
        self.register_reply(
            trigger=["提供建议", "改进建议", "修改意见"],
            reply_func=self._provide_feedback,
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

    async def _review_content(
        self, message: Dict[str, Any], sender: Any
    ) -> Union[str, Dict[str, Any]]:
        """审查故事内容"""
        self.log_activity("审查", "开始审查故事内容")

        response_text = """作为故事审核者，我将：
1. 评估故事结构完整性
2. 检查情节发展合理性
3. 审查人物塑造深度
4. 评价主题表达效果
5. 分析写作技巧运用

开始进行审查..."""

        # 当需要详细元数据时返回字典
        if message.get("require_metadata"):
            return {
                "role": "assistant",
                "content": response_text,
                "metadata": {"action": "review_content", "status": "in_progress"},
            }

        # 默认返回字符串响应
        return response_text

    async def _provide_feedback(
        self, message: Dict[str, Any], sender: Any
    ) -> Union[str, Dict[str, Any]]:
        """提供改进建议"""
        self.log_activity("反馈", "正在提供改进建议")

        response_text = """基于审查结果，我建议：
1. 故事结构方面
2. 情节发展方面
3. 人物塑造方面
4. 主题表达方面
5. 写作技巧方面

具体建议如下..."""

        # 当需要详细元数据时返回字典
        if message.get("require_metadata"):
            return {
                "role": "assistant",
                "content": response_text,
                "metadata": {"action": "provide_feedback", "status": "completed"},
            }

        # 默认返回字符串响应
        return response_text

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行审核任务"""
        self.log_activity("执行", "审核者就绪")
        return {
            "status": "ready",
            "agent_type": "supervisor",
            "capabilities": ["content_review", "feedback_provision"],
        }
