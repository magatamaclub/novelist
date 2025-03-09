#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import Mock, patch
from novelist.agents.supervisor_agent import SupervisorAgent
from novelist.core.workflow import NovelAgent


@pytest.fixture
def supervisor_agent():
    """创建SupervisorAgent实例"""
    return SupervisorAgent()


@pytest.fixture
def mock_llm_response():
    """模拟LLM响应"""
    return """
    审核意见：
    1. 故事结构完整
    2. 人物性格鲜明
    3. 情节发展合理
    4. 建议优化：加强情感描写
    """


def test_supervisor_agent_initialization(supervisor_agent):
    """测试SupervisorAgent初始化"""
    assert isinstance(supervisor_agent, NovelAgent)
    assert supervisor_agent.name == "故事监制"


@patch("novelist.agents.supervisor_agent.SupervisorAgent.generate_reply")
async def test_review_content(mock_generate_reply, supervisor_agent, mock_llm_response):
    """测试内容审核功能"""
    mock_generate_reply.return_value = mock_llm_response
    message = {"role": "user", "content": "请审核"}
    response = await supervisor_agent._review_content(message, None)
    assert isinstance(response, str)
    assert "作为审核者" in response


@patch("novelist.agents.supervisor_agent.SupervisorAgent.generate_reply")
async def test_final_review(mock_generate_reply, supervisor_agent, mock_llm_response):
    """测试最终审核功能"""
    mock_generate_reply.return_value = mock_llm_response
    message = {"role": "user", "content": "最终审核"}
    response = await supervisor_agent._final_review(message, None)
    assert isinstance(response, str)
    assert "最终审核意见" in response


def test_format_feedback(supervisor_agent):
    """测试反馈格式化"""
    evaluation = {
        "structure": "完整",
        "characters": "鲜明",
        "plot": "合理",
        "style": "流畅",
        "overall": "良好",
    }
    feedback = supervisor_agent._format_feedback(evaluation)
    assert "结构完整性：完整" in feedback
    assert "总体评价：良好" in feedback


async def test_execute_method(supervisor_agent):
    """测试execute方法"""
    context = {"draft": "这是一个测试草稿"}
    result = await supervisor_agent.execute(context)
    assert result["status"] == "ready"
    assert "approved" in result


def test_trigger_registration(supervisor_agent):
    """测试触发词注册"""
    triggers = supervisor_agent._reply_functions_triggered_by_messages.keys()
    assert any("请审核" in trigger for trigger in triggers)
    assert any("最终审核" in trigger for trigger in triggers)


@pytest.mark.parametrize(
    "message_content,expected_phrase",
    [
        ("请审核", "开始审核"),
        ("评估内容", "开始审核"),
        ("检查质量", "开始审核"),
        ("最终审核", "最终审核意见"),
        ("终审", "最终审核意见"),
    ],
)
async def test_message_triggers(supervisor_agent, message_content, expected_phrase):
    """测试不同消息触发词的响应"""
    message = {"role": "user", "content": message_content}
    if "最终" in message_content or "终审" in message_content:
        response = await supervisor_agent._final_review(message, None)
    else:
        response = await supervisor_agent._review_content(message, None)
    assert expected_phrase in response
