"""
FastMCP资源管理模块

包含静态数据、动态数据、用户数据、配置数据等各种资源类型的示例，
展示如何有效地管理和提供数据资源。
"""

from .static_resources import StaticResources
from .dynamic_resources import DynamicResources
from .user_resources import UserResources
from .config_resources import ConfigResources

__all__ = ["StaticResources", "DynamicResources", "UserResources", "ConfigResources"]