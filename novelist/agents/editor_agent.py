#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any, List, Optional, Union
from ..core.adapter import NovelAgentAdapter, Message


class EditorAgent(NovelAgentAdapter):
    """文章编辑者，负责最终的润色和完善"""

    def __init__(self):
        super().__init__("editor")

        # 注册消息处理回调
        self.register_reply(
            trigger=["润色文章", "完善内容", "编辑优化"],
            reply_func=self._polish_content,
        )
        self.register_reply(
            trigger=["最终审阅", "定稿确认", "完成编辑"],
            reply_func=self._finalize_content,
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

    async def _polish_content(
        self, message: Dict[str, Any], sender: Any
    ) -> Union[str, Dict[str, Any]]:
        """润色和完善内容"""
        self.log_activity("润色", "开始润色和完善内容")

        response_text = """作为编辑，我将：
1. 优化文字表达
2. 改进句式结构
3. 调整段落布局
4. 增强文章流畅度
5. 提升整体质感

开始进行润色..."""

        # 当需要详细元数据时返回字典
        if message.get("require_metadata"):
            return {
                "role": "assistant",
                "content": response_text,
                "metadata": {"action": "polish_content", "status": "in_progress"},
            }

        # 默认返回字符串响应
        return response_text

    async def _finalize_content(
        self, message: Dict[str, Any], sender: Any
    ) -> Union[str, Dict[str, Any]]:
        """最终审阅和定稿"""
        self.log_activity("定稿", "进行最终审阅和定稿")

        response_text = """最终审阅工作包括：
1. 全文完整性检查
2. 文字错误核对
3. 格式规范确认
4. 风格一致性验证
5. 整体效果评估

开始最终审阅..."""

        # 当需要详细元数据时返回字典
        if message.get("require_metadata"):
            return {
                "role": "assistant",
                "content": response_text,
                "metadata": {"action": "finalize_content", "status": "completed"},
            }

        # 默认返回字符串响应
        return response_text

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行编辑任务"""
        self.log_activity("执行", "编辑者就绪")
        return {
            "status": "ready",
            "agent_type": "editor",
            "capabilities": ["content_polishing", "final_review"],
        }
