#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import json
from typing import Dict, Any


class AgentLogFormatter(logging.Formatter):
    """Agent日志格式化器"""

    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录

        Args:
            record: 日志记录对象

        Returns:
            str: 格式化后的日志字符串
        """
        # 获取基本日志信息
        log_data = {
            "timestamp": self.formatTime(record),
            "agent": record.name.split(".")[-1],
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # 添加异常信息（如果有）
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # 添加额外字段（如果有）
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        # 返回JSON格式的日志
        return json.dumps(log_data, ensure_ascii=False)


class NovelLogger:
    """小说创作系统日志管理器"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NovelLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._setup_logging()
            self._initialized = True

    def _setup_logging(self):
        """配置日志系统"""
        # 创建日志目录
        log_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "outputs", "logs"
        )
        os.makedirs(log_dir, exist_ok=True)

        # 创建根日志记录器
        root_logger = logging.getLogger("novelist")
        root_logger.setLevel(logging.INFO)

        # 配置控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            "%(asctime)s - %(name)s - [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(console_format)
        root_logger.addHandler(console_handler)

        # 配置文件处理器
        log_file = os.path.join(log_dir, f"novelist_{datetime.now():%Y%m%d}.log")
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(AgentLogFormatter())
        root_logger.addHandler(file_handler)

    def get_logger(self, name: str) -> logging.Logger:
        """
        获取命名的日志记录器

        Args:
            name: 日志记录器名称

        Returns:
            logging.Logger: 日志记录器实例
        """
        return logging.getLogger(f"novelist.{name}")

    def log_agent_activity(
        self,
        agent_name: str,
        action: str,
        message: str,
        extra_data: Dict[str, Any] = None,
    ) -> None:
        """
        记录Agent活动日志

        Args:
            agent_name: Agent名称
            action: 活动类型
            message: 活动描述
            extra_data: 额外数据
        """
        logger = self.get_logger(agent_name)

        # 构建日志消息
        log_message = f"[{action}] {message}"

        # 添加额外数据
        extra = {"extra_data": extra_data} if extra_data else {}

        # 记录日志
        logger.info(log_message, extra=extra)


def setup_logging():
    """初始化日志系统"""
    NovelLogger()
