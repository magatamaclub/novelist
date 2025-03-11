#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any, List, Optional, Sequence, Tuple
from abc import ABC, abstractmethod
import logging
import asyncio
import os
from datetime import datetime

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

        # 循环控制
        self.revision_count = 0
        self.editing_count = 0
        self.max_revision_cycles = int(os.getenv("MAX_REVISION_CYCLES", 3))
        self.max_editing_cycles = int(os.getenv("MAX_EDITING_CYCLES", 2))
        self.revision_threshold = float(os.getenv("REVISION_SCORE_THRESHOLD", 80))

        # 创作过程数据
        self.original_outline: Optional[str] = None  # 原始故事大纲
        self.current_draft: Optional[str] = None  # 当前草稿内容

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

    def _save_draft(self, draft_content: Optional[str]) -> str:
        """保存草稿到outlines目录"""
        if not isinstance(draft_content, str) or not draft_content.strip():
            raise ValueError("草稿内容不能为空或None")

        # 确保outlines目录存在
        outlines_dir = "novelist/outputs/outlines"
        os.makedirs(outlines_dir, exist_ok=True)

        # 获取标题和时间戳
        story_seed = self.context.get("story_seed", {})
        title = story_seed.get("title", "untitled")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 生成文件路径
        outline_path = os.path.join(outlines_dir, f"{title}_{timestamp}.txt")

        # 保存文件
        with open(outline_path, "w", encoding="utf-8") as f:
            f.write(draft_content)

        self.logger.info(f"稿件已保存到: {outline_path}")
        return outline_path

    def log_prompt(self, agent_type: str, prompt: str, result: str) -> None:
        """记录Agent的prompt和结果"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logger.info(f"\n{'='*50}\n{timestamp} - {agent_type}执行记录\n{'='*50}")
        self.logger.info(f"[PROMPT]\n{prompt}")
        self.logger.info(f"[RESULT]\n{result}\n{'='*50}\n")

    async def evaluate_content(
        self, outline: Optional[str], content: Optional[str]
    ) -> Tuple[float, str]:
        """评估内容质量"""
        if not outline or not content:
            return 0.0, "内容或大纲为空，无法评估"

        supervisor = self.agents["supervisor"]
        evaluation_prompt = f"""
请对照故事大纲评估内容的质量，给出0-100的评分和具体的修改建议。

原始大纲：
{outline}

当前内容：
{content}

评估要点：
1. 内容是否忠实遵循原始大纲的设定
2. 故事情节是否合理连贯
3. 人物塑造是否符合大纲定位
4. 整体创作质量评估

请按以下格式返回：
分数：[评分]（0分表示完全偏离大纲需要重写，100分表示完全符合要求）
合理性：[分析内容与大纲的契合度]
建议：[具体修改建议]
"""
        response = await supervisor.execute({"prompt": evaluation_prompt})

        # 解析评分和建议
        response_text = response.get("content", "")
        try:
            score_line = [
                line for line in response_text.split("\n") if "分数：" in line
            ][0]
            score = float(score_line.split("：")[1].strip())
            return score, response_text
        except (IndexError, ValueError):
            return 0.0, response_text

    async def run_workflow(self) -> Dict[str, Any]:
        """执行完整工作流"""
        try:
            self.logger.info(f"\n{'#'*80}\n开始执行工作流\n{'#'*80}")

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

            # 创建初始提示
            prompt = self._format_story_prompt(story_seed)

            while self.revision_count < self.max_revision_cycles:
                self.logger.info(f"\n---开始第{self.revision_count + 1}轮创作修订---")

                # 如果是首轮或需要重写
                if self.current_draft is None:
                    # 创作者生成大纲
                    creator_prompt = prompt + "\n请生成详细的故事大纲。"
                    creator_result = await self.agents["creator"].execute(
                        {"prompt": creator_prompt}
                    )
                    outline_content = creator_result.get("content", "")
                    self.original_outline = outline_content  # 保存原始大纲
                    self.log_prompt("creator", creator_prompt, outline_content)

                    # 写作者根据大纲创作
                    writer_prompt = f"请根据以下大纲进行创作：\n{outline_content}"
                    writer_result = await self.agents["writer"].execute(
                        {"prompt": writer_prompt}
                    )
                    self.log_prompt(
                        "writer", writer_prompt, writer_result.get("content", "")
                    )
                    self.current_draft = writer_result.get("content", "")

                # 编辑循环
                self.editing_count = 0
                while self.editing_count < self.max_editing_cycles:
                    self.logger.info(
                        f"\n---开始第{self.editing_count + 1}轮编辑润色---"
                    )

                    # 编辑检查错别字和润色
                    editor_prompt = f"""请对以下内容进行详细的错别字检查和文字润色：

{self.current_draft}

审查要点：
1. 检查所有可能的错别字
2. 检查病句和不通顺的表达
3. 检查标点符号使用是否规范
4. 保持作者的写作风格，仅修正错误
5. 改进不通顺的表达，但保持原意

请返回修改后的内容，并列出所有发现的问题。"""

                    editor_result = await self.agents["editor"].execute(
                        {"prompt": editor_prompt}
                    )
                    self.log_prompt(
                        "editor", editor_prompt, editor_result.get("content", "")
                    )
                    self.current_draft = editor_result.get("content", "")

                    # 评估内容质量和合理性
                    score, evaluation = await self.evaluate_content(
                        self.original_outline, self.current_draft
                    )
                    self.logger.info(f"\n当前评分：{score}\n评估意见：\n{evaluation}")

                    # 如果评分为0，需要退回给创作者重新创作
                    if score == 0:
                        self.logger.info(
                            "评分为0（内容严重偏离大纲），退回给创作者重新创作"
                        )
                        self.current_draft = None
                        break

                    if score >= self.revision_threshold:
                        self.logger.info("内容质量达标，完成创作")
                        self.context["final_draft"] = self.current_draft
                        # 保存最终稿件
                        self._save_draft(self.current_draft)
                        self.logger.info(
                            f"共经过{self.revision_count + 1}轮修订，{self.editing_count + 1}次润色"
                        )
                        return self.context

                    self.editing_count += 1

                # 如果current_draft为None，说明需要重新创作
                if self.current_draft is None:
                    continue

                # 如果编辑轮次用完仍未达标，让写作者基于当前版本和评审意见改进
                self.revision_count += 1
                if self.revision_count < self.max_revision_cycles:
                    self.logger.info("开始新一轮修改")

                    # 重新进行一次评估以获取最新意见
                    score, latest_evaluation = await self.evaluate_content(
                        self.original_outline, self.current_draft
                    )
                    self.logger.info(
                        f"\n新一轮评分：{score}\n评估意见：\n{latest_evaluation}"
                    )

                    writer_prompt = f"""请根据评审意见对当前版本进行全面改进。

评审意见：
{latest_evaluation}

原始大纲：
{self.original_outline}

要求：
1. 确保严格遵循原始大纲设定
2. 认真分析评审意见指出的问题
3. 保留原文的优点，重点改进不足之处
4. 确保故事情节的连贯性和完整性
5. 提升文字表达的质量

当前内容：
{self.current_draft}"""

                    writer_result = await self.agents["writer"].execute(
                        {"prompt": writer_prompt}
                    )
                    self.log_prompt(
                        "writer", writer_prompt, writer_result.get("content", "")
                    )
                    if writer_result.get("content"):
                        self.current_draft = writer_result.get("content")
                    else:
                        self.logger.error("写作者未返回有效内容，保持使用当前版本")

            self.logger.info("达到最大修订次数，使用最新版本作为最终稿")
            self.context["final_draft"] = self.current_draft
            # 即使未达到理想分数，也保存最终版本（如果有内容）
            if isinstance(self.current_draft, str) and self.current_draft.strip():
                self._save_draft(self.current_draft)
            else:
                self.logger.error("最终稿为空，无法保存")
            return self.context

        except Exception as e:
            self.logger.error(f"工作流执行失败: {str(e)}")
            raise

    def _extract_final_draft(self, chat_result: str) -> str:
        """从群聊结果中提取最终作品"""
        # TODO: 实现更复杂的结果提取逻辑
        return chat_result
