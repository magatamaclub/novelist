#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import Mock, patch
from novelist.agents.creator_agent import CreatorAgent
from novelist.core.workflow import NovelAgent


@pytest.fixture
def creator_agent():
    """创建CreatorAgent实例"""
    return CreatorAgent()


@pytest.fixture
def mock_llm_response():
    """模拟LLM响应"""
    return """
    故事大纲：
    1. 主线情节
    2. 人物设定
    3. 场景描写
    """


def test_creator_agent_initialization(creator_agent):
    """测试CreatorAgent初始化"""
    assert isinstance(creator_agent, NovelAgent)
    assert creator_agent.name == "故事创意生成器"


@patch("novelist.agents.creator_agent.CreatorAgent.generate_reply")
async def test_generate_outline(mock_generate_reply, creator_agent, mock_llm_response):
    """测试大纲生成功能"""
    mock_generate_reply.return_value = mock_llm_response
    message = {"role": "user", "content": "我们开始创作一个新故事"}
    response = await creator_agent._generate_outline(message, None)
    assert isinstance(response, str)
    assert "作为创意生成者" in response


@patch("novelist.agents.creator_agent.CreatorAgent.generate_reply")
async def test_revise_outline(mock_generate_reply, creator_agent, mock_llm_response):
    """测试大纲修改功能"""
    mock_generate_reply.return_value = mock_llm_response
    message = {"role": "user", "content": "修改大纲"}
    response = await creator_agent._revise_outline(message, None)
    assert isinstance(response, str)
    assert "根据反馈意见" in response


async def test_execute_method(creator_agent):
    """测试execute方法"""
    context = {"story_seed": {"title": "测试故事"}}
    result = await creator_agent.execute(context)
    assert result["status"] == "ready"


def test_trigger_registration(creator_agent):
    """测试触发词注册"""
    triggers = creator_agent._reply_functions_triggered_by_messages.keys()
    assert any("开始创作一个新故事" in trigger for trigger in triggers)
    assert any("修改大纲" in trigger for trigger in triggers)
