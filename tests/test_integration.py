#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import patch, AsyncMock
from novelist.core.workflow import WorkflowManager, NovelAgent
from novelist.agents.creator_agent import CreatorAgent
from novelist.agents.writer_agent import WriterAgent
from novelist.agents.supervisor_agent import SupervisorAgent
from novelist.agents.editor_agent import EditorAgent


@pytest.fixture
def workflow():
    """创建工作流实例"""
    return WorkflowManager()


@pytest.fixture
def story_seed():
    """创建测试用的故事种子"""
    return {
        "title": "测试故事",
        "theme": "友情与成长",
        "settings": {"time": "现代", "location": "大学校园", "season": "春季"},
        "style_preferences": {
            "tone": "温暖",
            "pacing": "中等",
            "narrative": "第三人称",
            "focus": "人物成长",
        },
    }


@pytest.fixture
def mock_agents():
    """创建各个模拟Agent"""
    agents = {
        "creator": CreatorAgent(),
        "writer": WriterAgent(),
        "supervisor": SupervisorAgent(),
        "editor": EditorAgent(),
    }
    return agents


@patch("novelist.core.workflow.GroupChat")
@patch("novelist.core.workflow.GroupChatManager")
async def test_complete_workflow(
    mock_chat_manager, mock_group_chat, workflow, story_seed, mock_agents
):
    """测试完整的工作流程"""
    # 配置模拟对象
    mock_chat_manager.return_value.arun = AsyncMock(
        return_value="这是最终的故事内容..."
    )

    # 注册所有agents
    for name, agent in mock_agents.items():
        workflow.register_agent(name, agent)

    # 设置上下文
    workflow.update_context({"story_seed": story_seed})

    # 执行工作流
    result = await workflow.run_workflow()

    # 验证工作流结果
    assert "final_draft" in result
    assert isinstance(result["final_draft"], str)
    assert len(result["final_draft"]) > 0

    # 验证各个步骤都被执行
    mock_chat_manager.return_value.arun.assert_called_once()
    assert mock_group_chat.called


@pytest.mark.parametrize("missing_agent", ["creator", "writer", "supervisor", "editor"])
async def test_workflow_missing_agent(workflow, missing_agent):
    """测试缺少Agent时的错误处理"""
    # 注册除了specified_missing_agent之外的所有agents
    for name in ["creator", "writer", "supervisor", "editor"]:
        if name != missing_agent:
            workflow.register_agent(name, eval(f"{name.capitalize()}Agent")())

    with pytest.raises(ValueError) as exc_info:
        await workflow.run_workflow()
    assert "缺少必要的Agent" in str(exc_info.value)


async def test_workflow_missing_context(workflow, mock_agents):
    """测试缺少上下文数据时的错误处理"""
    # 注册所有agents
    for name, agent in mock_agents.items():
        workflow.register_agent(name, agent)

    with pytest.raises(ValueError) as exc_info:
        await workflow.run_workflow()
    assert "未找到故事种子配置" in str(exc_info.value)


@pytest.mark.parametrize("agent_type", ["creator", "writer", "supervisor", "editor"])
def test_agent_registration(workflow, agent_type):
    """测试Agent注册功能"""
    agent = eval(f"{agent_type.capitalize()}Agent")()
    workflow.register_agent(agent_type, agent)
    assert agent_type in workflow.agents
    assert isinstance(workflow.agents[agent_type], NovelAgent)
