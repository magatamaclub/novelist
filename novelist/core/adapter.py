#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

try:
    import autogen_core
    from autogen_core import Agent, BaseAgent

    AgentBase = Agent or BaseAgent
    Message = Dict[str, Any]
except ImportError:
    raise ImportError("请先安装autogen-core==0.4.8.2")

from .logging import NovelLogger

logger = NovelLogger().get_logger(__name__)


class NovelAgentAdapter(AgentBase, ABC):
    """
    适配层：将现有的NovelAgent接口适配到autogen.core.Agent
    """

    def __init__(
        self, name: str, llm_config: Optional[Dict[str, Any]] = None, **kwargs
    ):
        """
        初始化适配器

        Args:
            name: agent名称
            llm_config: LLM配置
            **kwargs: 其他参数
        """
        # AgentBase可能不支持这些参数，所以我们保存它们但不传递给父类
        self._name = name
        self._llm_config = llm_config
        self._system_message = f"你是一个专业的小说创作{name}。"

        # 只调用基类的基本初始化
        super().__init__()

        self._message_handlers = {}
        logger.info(f"创建了{name} Agent")

    @property
    def name(self) -> str:
        return self._name

    @property
    def system_message(self) -> str:
        return self._system_message

    @property
    def llm_config(self) -> Optional[Dict[str, Any]]:
        return self._llm_config

    def register_reply(self, trigger: List[str], reply_func: Any) -> None:
        """
        注册消息处理函数

        Args:
            trigger: 触发词列表
            reply_func: 处理函数
        """
        for pattern in trigger:
            self._message_handlers[pattern] = reply_func

    @abstractmethod
    async def handle_message(
        self, message: Message, sender: Optional["AgentBase"] = None
    ) -> Optional[str]:
        """
        处理接收到的消息

        Args:
            message: 接收到的消息
            sender: 消息发送者

        Returns:
            Optional[str]: 回复内容
        """
        pass

    async def generate_response(
        self, message: Dict[str, Any], sender: Any
    ) -> Optional[str]:
        """
        生成回复（兼容autogen.core.Agent接口）

        Args:
            message: 消息内容
            sender: 发送者

        Returns:
            回复内容
        """
        content = message.get("content", "").lower()

        for pattern, handler in self._message_handlers.items():
            if pattern.lower() in content:
                response = await handler(message, sender)
                if isinstance(response, dict):
                    return response["content"]
                return response

        return None

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行任务（兼容旧接口）

        Args:
            context: 上下文信息

        Returns:
            执行结果
        """
        logger.info(f"{self.name} 开始执行任务")
        return {
            "status": "ready",
            "agent_type": self.name,
            "capabilities": ["conversation", "task_execution"],
        }

    async def get_response(
        self,
        message: Message,
        sender: Optional["AgentBase"] = None,
        **kwargs,
    ) -> Optional[str]:
        """
        实现autogen.core.Agent的响应生成接口
        """
        return await self.handle_message(message, sender)
