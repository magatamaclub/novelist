#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import Mock, patch
from novelist.agents.writer_agent import WriterAgent
from novelist.core.workflow import NovelAgent


@pytest.fixture
def writer_agent():
    """创建WriterAgent实例"""
    return WriterAgent()


@pytest.fixture
def mock_llm_response():
    """模拟LLM响应"""
    return """
    第一章：
    清晨的阳光洒在窗台上，微风轻拂着窗帘。小明睁开眼睛，
    今天将是一个不平凡的日子...
    """


def test_writer_agent_initialization(writer_agent):
    """测试WriterAgent初始化"""
    assert isinstance(writer_agent, NovelAgent)
    assert writer_agent.name == "小说作家"


@patch("novelist.agents.writer_agent.WriterAgent.generate_reply")
async def test_write_content(mock_generate_reply, writer_agent, mock_llm_response):
    """测试内容创作功能"""
    mock_generate_reply.return_value = mock_llm_response
    message = {"role": "user", "content": "开始写作"}
    response = await writer_agent._write_content(message, None)
    assert isinstance(response, str)
    assert "作为故事写作者" in response


@patch("novelist.agents.writer_agent.WriterAgent.generate_reply")
async def test_revise_content(mock_generate_reply, writer_agent, mock_llm_response):
    """测试内容修改功能"""
    mock_generate_reply.return_value = mock_llm_response
    message = {"role": "user", "content": "修改内容"}
    response = await writer_agent._revise_content(message, None)
    assert isinstance(response, str)
    assert "收到修改建议" in response


async def test_execute_method(writer_agent):
    """测试execute方法"""
    context = {"outline": {"title": "测试故事", "chapters": []}}
    result = await writer_agent.execute(context)
    assert result["status"] == "ready"


def test_trigger_registration(writer_agent):
    """测试触发词注册"""
    triggers = writer_agent._reply_functions_triggered_by_messages.keys()
    assert any("开始写作" in trigger for trigger in triggers)
    assert any("修改内容" in trigger for trigger in triggers)


@pytest.mark.parametrize(
    "message_content,expected_word",
    [
        ("开始写作", "写作"),
        ("根据大纲创作", "写作"),
        ("生成故事内容", "写作"),
        ("修改内容", "修改"),
        ("根据反馈修改", "修改"),
        ("重写章节", "修改"),
    ],
)
async def test_message_triggers(writer_agent, message_content, expected_word):
    """测试不同消息触发词的响应"""
    message = {"role": "user", "content": message_content}
    context = {}

    # 根据消息内容判断应该触发哪个方法
    if "修改" in message_content:
        response = await writer_agent._revise_content(message, context)
        assert expected_word in response.lower()
    else:
        response = await writer_agent._write_content(message, context)
        assert expected_word in response.lower()
