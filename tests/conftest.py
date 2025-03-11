#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pytest
from typing import Dict, Any
from unittest.mock import AsyncMock, patch


# 设置测试环境变量
@pytest.fixture(autouse=True)
def setup_test_env():
    """设置测试环境变量"""
    os.environ["MAX_REVISION_CYCLES"] = "3"
    os.environ["MAX_EDITING_CYCLES"] = "2"
    os.environ["REVISION_SCORE_THRESHOLD"] = "80"
    os.environ["DEEPSEEK_API_KEY"] = "test-key"
    os.environ["DEEPSEEK_API_BASE"] = "https://test-api.example.com/v1"


@pytest.fixture
def mock_llm_response():
    """通用的LLM响应模拟"""
    return {"content": "这是一个测试响应", "role": "assistant", "status": "success"}


@pytest.fixture
def mock_generate_reply():
    """模拟generate_reply方法"""

    async def mock_reply(*args, **kwargs):
        return "模拟的回复内容"

    return AsyncMock(side_effect=mock_reply)


@pytest.fixture
def mock_execute():
    """模拟execute方法"""

    async def mock_exec(context: Dict[str, Any]):
        return {
            "content": "执行结果",
            "status": "success",
            "metadata": {"action": "test"},
        }

    return AsyncMock(side_effect=mock_exec)


# 测试用的上下文数据
@pytest.fixture
def test_context():
    """测试用的上下文数据"""
    return {
        "story_seed": {
            "title": "测试故事",
            "theme": "友情",
            "settings": {"time": "现代", "location": "城市", "season": "夏天"},
            "style_preferences": {
                "tone": "温暖",
                "pacing": "平缓",
                "narrative": "第三人称",
            },
        }
    }


# 测试输出目录准备
@pytest.fixture(autouse=True)
def setup_output_dirs(tmp_path):
    """准备测试用的输出目录"""
    outlines_dir = tmp_path / "novelist" / "outputs" / "outlines"
    drafts_dir = tmp_path / "novelist" / "outputs" / "drafts"
    logs_dir = tmp_path / "novelist" / "outputs" / "logs"

    for dir_path in [outlines_dir, drafts_dir, logs_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)

    return {
        "outlines_dir": outlines_dir,
        "drafts_dir": drafts_dir,
        "logs_dir": logs_dir,
    }


# 模拟LLM工厂
@pytest.fixture
def mock_llm_factory():
    """模拟LLM工厂"""
    with patch("novelist.core.llm_factory.LLMFactory") as mock:
        mock.get_agent_config.return_value = {
            "name": "测试Agent",
            "llm_config": {
                "model": "test-model",
                "temperature": 0.7,
                "max_tokens": 2048,
            },
            "role_prompt": "你是一个测试Agent",
        }
        yield mock


# 清理环境
@pytest.fixture(autouse=True)
def cleanup_env():
    """清理测试环境"""
    yield
    # 清理可能被修改的环境变量
    env_vars = [
        "MAX_REVISION_CYCLES",
        "MAX_EDITING_CYCLES",
        "REVISION_SCORE_THRESHOLD",
        "DEEPSEEK_API_KEY",
        "DEEPSEEK_API_BASE",
    ]
    for var in env_vars:
        if var in os.environ:
            del os.environ[var]
