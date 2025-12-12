"""
日志配置模块
提供统一的日志配置和管理
"""

import os
import sys
from pathlib import Path
from typing import Optional
from loguru import logger

from src.config.settings import config


def setup_logging(
    log_level: str = None,
    log_file: str = None,
    max_size: int = None,
    backup_count: int = None,
    enable_console: bool = True
):
    """
    设置日志配置
    
    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径
        max_size: 日志文件最大大小（字节）
        backup_count: 备份文件数量
        enable_console: 是否启用控制台输出
    """
    # 使用配置或默认值
    log_level = log_level or config.log_level
    log_file = log_file or config.log_file
    max_size = max_size or config.log_max_size
    backup_count = backup_count or config.log_backup_count
    
    # 清除默认配置
    logger.remove()
    
    # 控制台输出
    if enable_console:
        logger.add(
            sys.stderr,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                   "<level>{message}</level>",
            colorize=True,
            backtrace=True,
            diagnose=True
        )
    
    # 文件输出
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_file,
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation=max_size,
            retention=backup_count,
            compression="zip",
            backtrace=True,
            diagnose=True,
            enqueue=True  # 异步写入
        )
    
    logger.info(f"日志配置完成 - 级别: {log_level}, 文件: {log_file}")


def get_logger(name: str = None):
    """
    获取logger实例
    
    Args:
        name: 模块名称
        
    Returns:
        logger实例
    """
    if name:
        return logger.bind(module=name)
    return logger


def log_request_info(request_info: dict):
    """
    记录请求信息
    
    Args:
        request_info: 请求信息字典
    """
    logger.info(
        "API请求 - 方法: {method}, 路径: {path}, 状态: {status}, 耗时: {duration:.2f}s, IP: {client_ip}",
        **request_info
    )


def log_error_info(error_info: dict):
    """
    记录错误信息
    
    Args:
        error_info: 错误信息字典
    """
    logger.error(
        "错误发生 - 类型: {error_type}, 消息: {error_message}, 位置: {location}",
        **error_info
    )


def log_performance_info(perf_info: dict):
    """
    记录性能信息
    
    Args:
        perf_info: 性能信息字典
    """
    logger.info(
        "性能指标 - 操作: {operation}, 耗时: {duration:.3f}s, 内存使用: {memory_usage}MB",
        **perf_info
    )


# 初始化日志
if not logger._core.handlers:
    setup_logging()