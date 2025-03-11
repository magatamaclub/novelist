#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import Mock, patch, AsyncMock
from novelist.core.workflow import WorkflowManager
from novelist.agents.creator_agent import CreatorAgent
from novelist.agents.writer_agent import WriterAgent
from novelist.agents.supervisor_agent import SupervisorAgent
from novelist.agents.editor_agent import EditorAgent


@pytest.fixture
def workflow_manager():
    """创建工作流管理器实例"""
    return WorkflowManager()


@pytest.fixture
def mock_story_seed():
    """模拟故事种子数据"""
    return {
        "title": "测试故事",
        "theme": "友情",
        "settings": {"time": "现代", "location": "城市", "season": "夏天"},
        "style_preferences": {
            "tone": "温暖",
            "pacing": "平缓",
            "narrative": "第三人称",
        },
    }


@pytest.fixture
def mock_agents(workflow_manager):
    """模拟所有必要的agents"""
    workflow_manager.register_agent("creator", CreatorAgent())
    workflow_manager.register_agent("writer", WriterAgent())
    workflow_manager.register_agent("supervisor", SupervisorAgent())
    workflow_manager.register_agent("editor", EditorAgent())
    return workflow_manager


@pytest.mark.asyncio
async def test_workflow_initialization(workflow_manager, mock_story_seed):
    """测试工作流初始化"""
    workflow_manager.update_context({"story_seed": mock_story_seed})
    assert workflow_manager.context["story_seed"] == mock_story_seed
    assert workflow_manager.max_revision_cycles == 3
    assert workflow_manager.max_editing_cycles == 2
    assert workflow_manager.revision_threshold == 80


@pytest.mark.asyncio
async def test_evaluate_content_empty_input(workflow_manager, mock_agents):
    """测试评估空内容的情况"""
    score, feedback = await workflow_manager.evaluate_content(None, None)
    assert score == 0.0
    assert "内容或大纲为空" in feedback


@pytest.mark.asyncio
@patch("novelist.agents.supervisor_agent.SupervisorAgent.execute")
async def test_evaluate_content_valid_input(
    mock_execute, workflow_manager, mock_agents
):
    """测试评估有效内容"""
    mock_execute.return_value = {"content": "分数：85\n建议：很好"}
    score, feedback = await workflow_manager.evaluate_content(
        "test outline", "test content"
    )
    assert score == 85
    assert "很好" in feedback


@pytest.mark.asyncio
async def test_save_draft_empty_content(workflow_manager):
    """测试保存空草稿"""
    with pytest.raises(ValueError, match="草稿内容不能为空或None"):
        workflow_manager._save_draft(None)
    with pytest.raises(ValueError, match="草稿内容不能为空或None"):
        workflow_manager._save_draft("")


@pytest.mark.asyncio
@patch("builtins.open")
async def test_save_draft_valid_content(mock_open, workflow_manager, mock_story_seed):
    """测试保存有效草稿"""
    workflow_manager.update_context({"story_seed": mock_story_seed})
    result = workflow_manager._save_draft("测试内容")
    assert "outlines" in result
    assert mock_story_seed["title"] in result


@pytest.mark.asyncio
@patch("novelist.agents.creator_agent.CreatorAgent.execute")
@patch("novelist.agents.writer_agent.WriterAgent.execute")
@patch("novelist.agents.supervisor_agent.SupervisorAgent.execute")
@patch("novelist.agents.editor_agent.EditorAgent.execute")
async def test_full_workflow_success(
    mock_editor_execute,
    mock_supervisor_execute,
    mock_writer_execute,
    mock_creator_execute,
    workflow_manager,
    mock_agents,
    mock_story_seed,
):
    """测试完整工作流程成功的情况"""
    # 设置模拟响应
    mock_creator_execute.return_value = {"content": "故事大纲"}
    mock_writer_execute.return_value = {"content": "故事内容"}
    mock_supervisor_execute.return_value = {"content": "分数：85\n建议：很好"}
    mock_editor_execute.return_value = {"content": "修改后的内容"}

    # 更新上下文
    workflow_manager.update_context({"story_seed": mock_story_seed})

    # 运行工作流
    result = await workflow_manager.run_workflow()

    # 验证结果
    assert "final_draft" in result
    assert isinstance(result["final_draft"], str)
    assert workflow_manager.revision_count >= 0
    assert workflow_manager.editing_count >= 0


@pytest.mark.asyncio
@patch("novelist.agents.supervisor_agent.SupervisorAgent.execute")
async def test_zero_score_handling(
    mock_supervisor_execute, workflow_manager, mock_agents, mock_story_seed
):
    """测试评分为0时的处理逻辑"""
    # 设置评分为0的响应
    mock_supervisor_execute.return_value = {"content": "分数：0\n建议：需要重写"}

    # 评估内容
    score, feedback = await workflow_manager.evaluate_content("outline", "content")

    # 验证结果
    assert score == 0
    assert workflow_manager.current_draft is None


@pytest.mark.asyncio
async def test_missing_required_agents(workflow_manager):
    """测试缺少必要Agent时的错误处理"""
    workflow_manager.update_context({"story_seed": {}})
    with pytest.raises(ValueError, match="缺少必要的Agent"):
        await workflow_manager.run_workflow()


@pytest.mark.asyncio
async def test_missing_story_seed(mock_agents):
    """测试缺少故事种子时的错误处理"""
    with pytest.raises(ValueError, match="未找到故事种子配置"):
        await mock_agents.run_workflow()
