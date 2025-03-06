#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any, Optional
import autogen
from abc import ABC, abstractmethod
import logging

from .llm_factory import LLMFactory


class NovelAgent(autogen.ConversableAgent, ABC):
    """小说创作Agent基类"""

    def __init__(self, agent_type: str):
        """
        初始化Agent

        Args:
            agent_type: Agent类型标识，用于获取对应配置
        """
        # 获取Agent配置
        config = LLMFactory.get_agent_config(agent_type)

        # 初始化AutoGen基类
        super().__init__(
            name=config["name"],
            system_message=config["role_prompt"],
            llm_config=config["llm_config"],
        )

        # 设置日志记录器
        self.logger = logging.getLogger(f"novelist.{agent_type}")

    def log_activity(self, action: str, message: str) -> None:
        """
        记录Agent活动日志

        Args:
            action: 活动类型
            message: 活动详情
        """
        self.logger.info(f"[{action}] {message}")

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行Agent的主要任务

        Args:
            context: 任务上下文

        Returns:
            Dict[str, Any]: 任务执行结果
        """
        pass


class WorkflowManager:
    """工作流管理器"""

    def __init__(self):
        self.agents = {}
        self.context = {}
        self.logger = logging.getLogger("novelist.workflow")

    def register_agent(self, name: str, agent: NovelAgent) -> None:
        """
        注册Agent

        Args:
            name: Agent名称
            agent: Agent实例
        """
        self.agents[name] = agent
        self.logger.info(f"注册Agent: {name}")

    def update_context(self, data: Dict[str, Any]) -> None:
        """
        更新上下文数据

        Args:
            data: 要更新的数据
        """
        self.context.update(data)
        self.logger.debug(f"更新上下文: {data.keys()}")

    async def run_agent(self, name: str) -> Optional[Dict[str, Any]]:
        """
        运行指定的Agent

        Args:
            name: Agent名称

        Returns:
            Optional[Dict[str, Any]]: Agent执行结果
        """
        agent = self.agents.get(name)
        if not agent:
            self.logger.error(f"未找到Agent: {name}")
            return None

        try:
            self.logger.info(f"开始执行Agent: {name}")
            result = await agent.execute(self.context)
            self.update_context(result)
            self.logger.info(f"Agent {name} 执行完成")
            return result
        except Exception as e:
            self.logger.error(f"Agent {name} 执行失败: {str(e)}")
            raise

    async def run_workflow(self) -> Dict[str, Any]:
        """
        按顺序执行完整工作流

        Returns:
            Dict[str, Any]: 工作流执行结果
        """
        try:
            self.logger.info("开始执行工作流")

            # 依次执行各个Agent
            await self.run_agent("creator")  # 创意生成

            while True:  # 写作-审核循环
                await self.run_agent("writer")  # 写作创作
                supervisor_result = await self.run_agent("supervisor")  # 审核把关

                if supervisor_result.get("approved", False):
                    break  # 通过审核，退出循环

                self.logger.info("需要修改，继续写作循环")

            await self.run_agent("editor")  # 最终编辑

            self.logger.info("工作流执行完成")
            return self.context

        except Exception as e:
            self.logger.error(f"工作流执行失败: {str(e)}")
            raise
