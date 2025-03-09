#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import asyncio
import logging
from datetime import datetime
import yaml

from .core.workflow import WorkflowManager
from .core.llm_factory import LLMFactory
from .agents.creator_agent import CreatorAgent
from .agents.writer_agent import WriterAgent
from .agents.supervisor_agent import SupervisorAgent
from .agents.editor_agent import EditorAgent


def setup_logging():
    """配置日志系统"""
    # 确保日志目录存在
    log_dir = os.path.join(os.path.dirname(__file__), "outputs", "logs")
    os.makedirs(log_dir, exist_ok=True)

    # 配置日志格式
    log_format = "%(asctime)s - %(name)s - [%(levelname)s] %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # 创建文件处理器
    log_file = os.path.join(log_dir, f"novelist_{datetime.now():%Y%m%d_%H%M%S}.log")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(log_format, date_format))

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format, date_format))

    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def load_story_seed():
    """加载故事种子配置"""
    config_path = os.path.join(os.path.dirname(__file__), "configs", "story_seed.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


async def main():
    """主程序入口"""
    # 初始化日志系统
    setup_logging()
    logger = logging.getLogger("novelist.main")

    try:
        # 验证LLM配置
        LLMFactory.validate_config()

        # 加载故事种子
        story_seed = load_story_seed()

        # 创建并配置工作流
        workflow = WorkflowManager()
        workflow.update_context({"story_seed": story_seed})

        # 注册所有参与创作的Agents
        agents = {
            "creator": CreatorAgent(),  # 创意生成
            "writer": WriterAgent(),  # 写作
            "supervisor": SupervisorAgent(),  # 审核
            "editor": EditorAgent(),  # 编辑
        }

        for name, agent in agents.items():
            workflow.register_agent(name, agent)
            logger.info(f"已注册 {name} Agent")

        # 执行工作流
        logger.info("开始小说创作工作流")
        result = await workflow.run_workflow()

        if "final_draft" not in result:
            raise ValueError("工作流未生成最终作品")

        # 保存创作结果
        output_dir = os.path.join(os.path.dirname(__file__), "outputs", "drafts")
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(
            output_dir, f"{story_seed['title']}_{datetime.now():%Y%m%d_%H%M%S}.txt"
        )

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result["final_draft"])

        logger.info(f"创作完成，作品已保存至: {output_file}")

    except Exception as e:
        logger.error(f"程序执行失败: {str(e)}")
        raise


def run():
    """程序启动函数"""
    asyncio.run(main())
