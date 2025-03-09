#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import Mock, patch
from novelist.agents.editor_agent import EditorAgent
from novelist.core.workflow import NovelAgent


@pytest.fixture
def editor_agent():
    """创建EditorAgent实例"""
    return EditorAgent()


@pytest.fixture
def mock_llm_response():
    """模拟LLM响应"""
    return """
    修改建议：
    1. 调整段落结构
    2. 优化词句表达
    3. 统一标点使用
    4. 校对文字错误
    """


def test_editor_agent_initialization(editor_agent):
    """测试EditorAgent初始化"""
    assert isinstance(editor_agent, NovelAgent)
    assert editor_agent.name == "文字编辑"


@patch("novelist.agents.editor_agent.EditorAgent.generate_reply")
async def test_polish_content(mock_generate_reply, editor_agent, mock_llm_response):
    """测试文本润色功能"""
    mock_generate_reply.return_value = mock_llm_response
    message = {"role": "user", "content": "开始编辑"}
    response = await editor_agent._polish_content(message, None)
    assert isinstance(response, str)
    assert "作为编辑" in response


@patch("novelist.agents.editor_agent.EditorAgent.generate_reply")
async def test_finalize_draft(mock_generate_reply, editor_agent, mock_llm_response):
    """测试最终定稿功能"""
    mock_generate_reply.return_value = mock_llm_response
    message = {"role": "user", "content": "最终定稿"}
    response = await editor_agent._finalize_draft(message, None)
    assert isinstance(response, str)
    assert "最终编辑工作" in response


def test_style_guide(editor_agent):
    """测试编辑风格指南"""
    style_guide = editor_agent._get_style_guide()
    assert isinstance(style_guide, dict)
    assert "paragraphs" in style_guide
    assert "punctuation" in style_guide
    assert "format" in style_guide
    assert "typography" in style_guide
    # 验证指南内容的完整性
    assert all(isinstance(value, str) for value in style_guide.values())
    assert all(len(value) > 0 for value in style_guide.values())


async def test_execute_method(editor_agent):
    """测试execute方法"""
    context = {"draft": "这是最终草稿"}
    result = await editor_agent.execute(context)
    assert result["status"] == "ready"


def test_trigger_registration(editor_agent):
    """测试触发词注册"""
    triggers = editor_agent._reply_functions_triggered_by_messages.keys()
    assert any("开始编辑" in trigger for trigger in triggers)
    assert any("最终定稿" in trigger for trigger in triggers)


@pytest.mark.parametrize(
    "message_content,expected_word",
    [
        ("开始编辑", "润色"),
        ("润色文章", "润色"),
        ("格式调整", "润色"),
        ("最终定稿", "定稿"),
        ("完成编辑", "定稿"),
    ],
)
async def test_message_triggers(editor_agent, message_content, expected_word):
    """测试不同消息触发词的响应"""
    message = {"role": "user", "content": message_content}

    if "最终" in message_content or "完成" in message_content:
        response = await editor_agent._finalize_draft(message, None)
    else:
        response = await editor_agent._polish_content(message, None)
    assert expected_word in response.lower()


@pytest.mark.parametrize(
    "style_key", ["paragraphs", "punctuation", "format", "spacing", "typography"]
)
def test_style_guide_completeness(editor_agent, style_key):
    """测试风格指南的完整性"""
    style_guide = editor_agent._get_style_guide()
    assert style_key in style_guide
    assert len(style_guide[style_key]) > 0
    assert isinstance(style_guide[style_key], str)
