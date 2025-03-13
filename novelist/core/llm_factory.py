#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from typing import Dict, Any
import yaml
from dotenv import load_dotenv


from typing_extensions import TypedDict


class LLMConfig(TypedDict):
    model: str
    api_key: str
    api_base: str
    temperature: float
    max_tokens: int


class AgentConfig(TypedDict):
    name: str
    llm_config: LLMConfig
    role_prompt: str


class LLMFactory:
    """LLM配置管理工厂"""

    _instance = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMFactory, cls).__new__(cls)
            cls._instance._load_config()  # 在创建实例时加载配置
        return cls._instance

    def __init__(self):
        pass  # 配置加载移到 __new__ 中

    def _load_config(self):
        """加载LLM配置"""
        # 加载环境变量
        load_dotenv()

        # 读取配置文件
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "configs", "llm_config.yaml"
        )

        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # 处理环境变量替换
        self._config = self._process_env_vars(config)

    def _process_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """处理配置中的环境变量引用"""
        if isinstance(config, dict):
            return {key: self._process_env_vars(value) for key, value in config.items()}
        elif isinstance(config, list):
            return [self._process_env_vars(item) for item in config]
        elif (
            isinstance(config, str) and config.startswith("${") and config.endswith("}")
        ):
            env_var = config[2:-1]
            return os.getenv(env_var)
        return config

    @classmethod
    def get_agent_config(cls, agent_type: str) -> Dict[str, Any]:
        """
        获取指定Agent的LLM配置

        Args:
            agent_type: Agent类型名称

        Returns:
            Dict[str, Any]: Agent的配置信息
        """
        instance = cls()

        # 获取默认配置
        default_config = instance._config.get("default_config", {})

        # 获取具体Agent配置并与默认配置合并
        agent_config = instance._config.get("agents", {}).get(agent_type, {})
        if not agent_config:
            raise ValueError(f"未找到Agent类型 '{agent_type}' 的配置")

        # 合并LLM配置
        llm_config = default_config.copy()
        llm_config.update(agent_config.get("llm_config", {}))
        agent_config["llm_config"] = llm_config

        return agent_config

    @classmethod
    def validate_config(cls) -> bool:
        """
        验证配置的完整性和有效性

        Returns:
            bool: 配置是否有效
        """
        instance = cls()

        # 检查必要的环境变量
        required_env_vars = ["DEEPSEEK_API_KEY", "DEEPSEEK_API_BASE"]
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"缺少必要的环境变量: {', '.join(missing_vars)}")

        # 检查每个Agent的配置完整性
        for agent_type, config in instance._config.get("agents", {}).items():
            if not all(key in config for key in ["name", "llm_config", "role_prompt"]):
                raise ValueError(f"Agent '{agent_type}' 配置不完整")

            llm_config = config["llm_config"]
            if not all(key in llm_config for key in ["model", "api_key", "api_base"]):
                raise ValueError(f"Agent '{agent_type}' 的LLM配置不完整")

        return True
