#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any, List, Optional, Sequence
from abc import ABC, abstractmethod
import logging
import asyncio

try:
    import autogen_core
    from autogen_core import Agent, BaseAgent

    AgentBase = Agent or BaseAgent
except ImportError:
    raise ImportError("请先安装autogen-core==0.4.8.2")

from .llm_factory import LLMFactory


class NovelAgent(AgentBase, ABC):
    """小说创作Agent基类"""

    def __init__(self, agent_type: str):
        """初始化Agent"""
        # 获取Agent配置
        config = LLMFactory.get_agent_config(agent_type)

        # 先调用基类的基本初始化
        super().__init__()

        # 设置Agent属性
        self._name = config["name"]
        self._llm_config = config["llm_config"]
        self._system_message = config["role_prompt"]
        self._description = f"A {agent_type} agent for novel writing"

        # 设置日志记录器
        self.logger = logging.getLogger(f"novelist.{agent_type}")

        # 初始化消息处理函数映射
        self._message_handlers = {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def system_message(self) -> str:
        return self._system_message

    @property
    def llm_config(self) -> Optional[Dict[str, Any]]:
        return self._llm_config

    def register_reply(self, trigger: List[str], reply_func: callable) -> None:
        """注册消息触发回调"""
        for pattern in trigger:
            self._message_handlers[pattern] = reply_func

    async def _process_received_message(self, message: Dict[str, Any]) -> Optional[str]:
        """处理接收到的消息"""
        if not isinstance(message, dict) or "content" not in message:
            return None

        content = message["content"]
        for pattern, handler in self._message_handlers.items():
            if pattern.lower() in content.lower():
                try:
                    return await handler(message, self)
                except Exception as e:
                    self.logger.error(f"消息处理错误: {str(e)}")
                    return f"处理消息时出错: {str(e)}"
        return None

    def log_activity(self, action: str, message: str) -> None:
        """记录Agent活动日志"""
        self.logger.info(f"[{action}] {message}")

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行Agent的主要任务"""
        pass


class SimpleGroupChat:
    """简化的群聊实现"""

    def __init__(self, agents, messages=None, max_round=12):
        self.agents = agents
        self.messages = messages or []
        self.max_round = max_round


class SimpleGroupChatManager:
    """简化的群聊管理器实现"""

    def __init__(self, groupchat, name, llm_config=None, system_message=None):
        self.groupchat = groupchat
        self.name = name
        self.llm_config = llm_config
        self.system_message = system_message

    def run(self, prompt: str) -> str:
        """运行群聊"""
        return prompt  # 简化实现，直接返回输入


class WorkflowManager:
    """工作流管理器"""

    def __init__(self):
        self.agents: Dict[str, NovelAgent] = {}
        self.context: Dict[str, Any] = {}
        self.logger = logging.getLogger("novelist.workflow")
        self.group_chat = None
        self.manager = None

    def register_agent(self, name: str, agent: NovelAgent) -> None:
        """注册Agent"""
        self.agents[name] = agent
        self.logger.info(f"注册Agent: {name}")

    def update_context(self, data: Dict[str, Any]) -> None:
        """更新上下文数据"""
        self.context.update(data)
        self.logger.debug(f"更新上下文: {data.keys()}")

    def _setup_group_chat(self) -> None:
        """设置群聊环境"""
        # 按特定顺序设置参与者
        participants: Sequence[NovelAgent] = [
            self.agents["creator"],
            self.agents["writer"],
            self.agents["supervisor"],
            self.agents["editor"],
        ]

        # 创建群聊
        self.group_chat = SimpleGroupChat(
            agents=list(participants), messages=[], max_round=12
        )

        # 创建群聊管理器
        self.manager = SimpleGroupChatManager(
            groupchat=self.group_chat,
            name="小说创作组长",
            llm_config=LLMFactory.get_agent_config("manager")["llm_config"],
            system_message="""你是小说创作团队的组长。你的职责是:
1. 协调团队成员之间的合作
2. 确保创作过程按照既定流程进行
3. 在团队成员之间出现分歧时做出决策
4. 确保最终作品符合质量要求""",
        )

    def _format_story_prompt(self, story_seed: Dict[str, Any]) -> str:
        """格式化故事创作提示"""
        return f"""让我们开始创作一个新故事:

标题: {story_seed['title']}
主题: {story_seed['theme']}

场景设定:
- 时代背景: {story_seed['settings']['time']}
- 地点: {story_seed['settings']['location']}
- 季节: {story_seed['settings']['season']}

写作风格:
- 基调: {story_seed['style_preferences']['tone']}
- 节奏: {story_seed['style_preferences']['pacing']}
- 叙事视角: {story_seed['style_preferences']['narrative']}

请按照以下流程进行创作:
1. 创意生成者(creator)提出故事大纲
2. 写作者(writer)根据大纲进行写作
3. 审核者(supervisor)审查内容质量
4. 编辑(editor)进行最终润色

每位成员请按照自己的角色职责参与创作。"""

    async def run_workflow(self) -> Dict[str, Any]:
        """执行完整工作流"""
        try:
            self.logger.info("开始执行工作流")

            # 验证所需agent是否都已注册
            required_agents = {"creator", "writer", "supervisor", "editor"}
            if not all(agent in self.agents for agent in required_agents):
                raise ValueError("缺少必要的Agent")

            # 设置群聊
            self._setup_group_chat()

            # 获取故事种子
            story_seed = self.context.get("story_seed")
            if not story_seed:
                raise ValueError("未找到故事种子配置")

            # 启动群聊
            prompt = self._format_story_prompt(story_seed)
            if self.manager is None:
                raise ValueError("Group chat manager not initialized")

            chat_result = self.manager.run(prompt)

            # 从群聊结果中提取最终作品
            final_draft = self._extract_final_draft(chat_result)
            self.context["final_draft"] = final_draft

            self.logger.info("工作流执行完成")
            return self.context

        except Exception as e:
            self.logger.error(f"工作流执行失败: {str(e)}")
            raise

    def _extract_final_draft(self, chat_result: str) -> str:
        """从群聊结果中提取最终作品"""
        # TODO: 实现更复杂的结果提取逻辑
        return chat_result
