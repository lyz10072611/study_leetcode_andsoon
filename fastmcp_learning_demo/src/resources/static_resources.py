"""
静态资源示例

这个模块展示了如何创建和管理静态数据资源，包括配置文件、
文档数据、参考信息等不经常变化的数据。
"""

from fastmcp import FastMCP
from typing import Dict, List, Any, Optional
import json
from datetime import datetime


class StaticResources:
    """静态资源管理类，提供各种静态数据资源"""
    
    def __init__(self, mcp: FastMCP):
        """
        初始化静态资源
        
        Args:
            mcp: FastMCP服务器实例
        """
        self.mcp = mcp
        self._register_resources()
        self._initialize_static_data()
    
    def _register_resources(self):
        """注册所有静态资源"""
        # 配置相关资源
        self.mcp.resource("/config/app-settings")(self.get_app_settings)
        self.mcp.resource("/config/database-config")(self.get_database_config)
        self.mcp.resource("/config/api-endpoints")(self.get_api_endpoints)
        
        # 文档和参考资源
        self.mcp.resource("/docs/mcp-guide")(self.get_mcp_guide)
        self.mcp.resource("/docs/api-reference")(self.get_api_reference)
        self.mcp.resource("/docs/best-practices")(self.get_best_practices)
        
        # 静态数据资源
        self.mcp.resource("/data/countries")(self.get_countries)
        self.mcp.resource("/data/currencies")(self.get_currencies)
        self.mcp.resource("/data/timezones")(self.get_timezones)
        self.mcp.resource("/data/programming-languages")(self.get_programming_languages)
        
        # 模板和示例资源
        self.mcp.resource("/templates/code-examples")(self.get_code_examples)
        self.mcp.resource("/templates/error-messages")(self.get_error_messages)
        self.mcp.resource("/templates/response-formats")(self.get_response_formats)
        
        # 系统信息资源
        self.mcp.resource("/system/info")(self.get_system_info)
        self.mcp.resource("/system/health")(self.get_system_health)
        self.mcp.resource("/system/metrics")(self.get_system_metrics)
    
    def _initialize_static_data(self):
        """初始化静态数据"""
        # 应用程序设置
        self.app_settings = {
            "app_name": "FastMCP Learning Demo",
            "version": "0.1.0",
            "environment": "development",
            "debug_mode": True,
            "max_request_size": "10MB",
            "rate_limit": {
                "requests_per_minute": 100,
                "requests_per_hour": 1000
            },
            "features": {
                "async_support": True,
                "sse_support": True,
                "authentication": True,
                "caching": True,
                "logging": True
            },
            "supported_formats": ["json", "xml", "csv", "yaml"],
            "last_updated": datetime.now().isoformat()
        }
        
        # 数据库配置
        self.database_config = {
            "default": {
                "engine": "postgresql",
                "host": "localhost",
                "port": 5432,
                "database": "fastmcp_demo",
                "username": "demo_user",
                "password": "demo_password",
                "ssl_mode": "prefer",
                "connection_pool": {
                    "min_connections": 5,
                    "max_connections": 20,
                    "connection_timeout": 30
                }
            },
            "redis": {
                "host": "localhost",
                "port": 6379,
                "database": 0,
                "password": None,
                "ssl": False,
                "connection_pool": {
                    "max_connections": 50,
                    "connection_timeout": 10
                }
            }
        }
        
        # API端点配置
        self.api_endpoints = {
            "tools": {
                "base_path": "/tools",
                "methods": ["POST"],
                "description": "工具调用端点"
            },
            "resources": {
                "base_path": "/resources",
                "methods": ["GET"],
                "description": "资源访问端点"
            },
            "prompts": {
                "base_path": "/prompts",
                "methods": ["GET", "POST"],
                "description": "提示模板端点"
            },
            "sse": {
                "base_path": "/sse",
                "methods": ["GET"],
                "description": "服务器发送事件端点"
            },
            "health": {
                "base_path": "/health",
                "methods": ["GET"],
                "description": "健康检查端点"
            }
        }
        
        # MCP指南文档
        self.mcp_guide = {
            "title": "FastMCP 开发指南",
            "sections": [
                {
                    "title": "快速开始",
                    "content": """
                    FastMCP 是一个基于 Python 的高效框架，用于构建符合 Model Context Protocol (MCP) 规范的服务器和客户端。
                    
                    主要特点：
                    - 协议隐形化：将复杂的 MCP 协议抽象为简洁的装饰器语法
                    - 开发闪电化：显著减少开发工作量，工具开发代码量可减少 90%
                    - 生产就绪化：内置 OAuth 安全校验、资源缓存、多协议传输等企业级特性
                    - Pythonic 设计：充分利用 Python 的语言特性
                    """
                },
                {
                    "title": "核心概念",
                    "content": """
                    FastMCP 主要包含三个核心组件：
                    
                    1. Tools（工具）：用于执行特定操作，如计算、数据处理等
                    2. Resources（资源）：用于提供结构化数据访问
                    3. Prompts（提示模板）：用于定义可重用的交互模式
                    
                    通过这些组件，LLM 能够安全地访问本地工具、私有数据和外部服务。
                    """
                },
                {
                    "title": "最佳实践",
                    "content": """
                    - 使用明确的函数签名和详细的文档字符串
                    - 妥善处理错误情况，抛出有意义的异常
                    - 对于需要跨调用维护状态的工具，使用上下文对象
                    - 尽可能使工具函数具有幂等性
                    - 采用 RESTful 风格设计资源路径
                    - 对于敏感资源，实施适当的认证和授权机制
                    """
                }
            ],
            "last_updated": "2024-01-15"
        }
        
        # API参考文档
        self.api_reference = {
            "version": "v1.0",
            "base_url": "http://localhost:8000",
            "endpoints": [
                {
                    "path": "/tools/{tool_name}",
                    "method": "POST",
                    "description": "调用指定工具",
                    "parameters": {
                        "tool_name": "工具名称（路径参数）",
                        "request_body": "工具参数（JSON格式）"
                    },
                    "response": {
                        "success": "工具执行结果",
                        "error": "错误信息"
                    }
                },
                {
                    "path": "/resources/{resource_path}",
                    "method": "GET",
                    "description": "获取资源数据",
                    "parameters": {
                        "resource_path": "资源路径（路径参数）"
                    },
                    "response": {
                        "success": "资源数据",
                        "error": "错误信息"
                    }
                }
            ],
            "authentication": {
                "type": "Bearer Token",
                "header": "Authorization: Bearer {token}",
                "description": "需要有效的访问令牌"
            }
        }
        
        # 最佳实践文档
        self.best_practices = {
            "tool_design": {
                "title": "工具设计最佳实践",
                "items": [
                    "使用明确的函数签名和类型注解",
                    "提供详细的文档字符串",
                    "妥善处理错误情况",
                    "使用上下文对象进行状态管理",
                    "确保工具函数的幂等性"
                ]
            },
            "resource_design": {
                "title": "资源设计最佳实践",
                "items": [
                    "采用 RESTful 风格设计资源路径",
                    "实施适当的认证和授权机制",
                    "对大量数据实现分页机制",
                    "使用缓存提高性能",
                    "提供丰富的错误信息"
                ]
            },
            "security": {
                "title": "安全最佳实践",
                "items": [
                    "实施输入验证和清理",
                    "使用安全的认证机制",
                    "限制资源访问权限",
                    "记录安全事件",
                    "定期更新依赖包"
                ]
            }
        }
        
        # 国家数据
        self.countries = [
            {"code": "US", "name": "United States", "continent": "North America", "population": 331900000},
            {"code": "CN", "name": "China", "continent": "Asia", "population": 1412000000},
            {"code": "IN", "name": "India", "continent": "Asia", "population": 1380000000},
            {"code": "JP", "name": "Japan", "continent": "Asia", "population": 125800000},
            {"code": "DE", "name": "Germany", "continent": "Europe", "population": 83200000},
            {"code": "GB", "name": "United Kingdom", "continent": "Europe", "population": 67500000},
            {"code": "FR", "name": "France", "continent": "Europe", "population": 67400000},
            {"code": "BR", "name": "Brazil", "continent": "South America", "population": 213900000},
            {"code": "CA", "name": "Canada", "continent": "North America", "population": 38000000},
            {"code": "AU", "name": "Australia", "continent": "Oceania", "population": 25700000}
        ]
        
        # 货币数据
        self.currencies = [
            {"code": "USD", "name": "US Dollar", "symbol": "$", "country": "United States"},
            {"code": "EUR", "name": "Euro", "symbol": "€", "country": "Eurozone"},
            {"code": "GBP", "name": "British Pound", "symbol": "£", "country": "United Kingdom"},
            {"code": "JPY", "name": "Japanese Yen", "symbol": "¥", "country": "Japan"},
            {"code": "CNY", "name": "Chinese Yuan", "symbol": "¥", "country": "China"},
            {"code": "INR", "name": "Indian Rupee", "symbol": "₹", "country": "India"},
            {"code": "CAD", "name": "Canadian Dollar", "symbol": "C$", "country": "Canada"},
            {"code": "AUD", "name": "Australian Dollar", "symbol": "A$", "country": "Australia"},
            {"code": "CHF", "name": "Swiss Franc", "symbol": "CHF", "country": "Switzerland"},
            {"code": "BRL", "name": "Brazilian Real", "symbol": "R$", "country": "Brazil"}
        ]
        
        # 时区数据
        self.timezones = [
            {"name": "UTC", "offset": "+00:00", "description": "Coordinated Universal Time"},
            {"name": "America/New_York", "offset": "-05:00", "description": "Eastern Time (US)"},
            {"name": "America/Los_Angeles", "offset": "-08:00", "description": "Pacific Time (US)"},
            {"name": "Europe/London", "offset": "+00:00", "description": "Greenwich Mean Time"},
            {"name": "Europe/Paris", "offset": "+01:00", "description": "Central European Time"},
            {"name": "Asia/Tokyo", "offset": "+09:00", "description": "Japan Standard Time"},
            {"name": "Asia/Shanghai", "offset": "+08:00", "description": "China Standard Time"},
            {"name": "Asia/Kolkata", "offset": "+05:30", "description": "India Standard Time"},
            {"name": "Australia/Sydney", "offset": "+11:00", "description": "Australian Eastern Time"},
            {"name": "Brazil/East", "offset": "-03:00", "description": "Brazil Eastern Time"}
        ]
        
        # 编程语言数据
        self.programming_languages = [
            {
                "name": "Python",
                "type": "Interpreted",
                "paradigm": ["Object-oriented", "Procedural", "Functional"],
                "year_created": 1991,
                "creator": "Guido van Rossum",
                "use_cases": ["Web Development", "Data Science", "AI/ML", "Automation"],
                "popularity_rank": 1
            },
            {
                "name": "JavaScript",
                "type": "Interpreted",
                "paradigm": ["Object-oriented", "Functional", "Event-driven"],
                "year_created": 1995,
                "creator": "Brendan Eich",
                "use_cases": ["Web Development", "Mobile Apps", "Server-side", "Desktop Apps"],
                "popularity_rank": 2
            },
            {
                "name": "Java",
                "type": "Compiled",
                "paradigm": ["Object-oriented", "Procedural"],
                "year_created": 1995,
                "creator": "James Gosling",
                "use_cases": ["Enterprise Applications", "Android Development", "Web Services"],
                "popularity_rank": 3
            },
            {
                "name": "C++",
                "type": "Compiled",
                "paradigm": ["Object-oriented", "Procedural", "Generic"],
                "year_created": 1985,
                "creator": "Bjarne Stroustrup",
                "use_cases": ["System Programming", "Game Development", "Embedded Systems"],
                "popularity_rank": 4
            },
            {
                "name": "Go",
                "type": "Compiled",
                "paradigm": ["Procedural", "Concurrent"],
                "year_created": 2009,
                "creator": "Robert Griesemer, Rob Pike, Ken Thompson",
                "use_cases": ["Cloud Services", "Microservices", "Network Programming"],
                "popularity_rank": 5
            }
        ]
        
        # 代码示例模板
        self.code_examples = {
            "basic_tools": {
                "title": "基础工具示例",
                "examples": [
                    {
                        "name": "计算器工具",
                        "description": "简单的数学计算工具",
                        "code": """
@mcp.tool()
def add(a: int, b: int) -> int:
    \"\"\"将两个数字相加\"\"\"
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    \"\"\"将两个数字相乘\"\"\"
    return a * b
                        """
                    },
                    {
                        "name": "字符串处理工具",
                        "description": "文本处理功能",
                        "code": """
@mcp.tool()
def reverse_text(text: str) -> str:
    \"\"\"反转文本\"\"\"
    return text[::-1]

@mcp.tool()
def count_words(text: str) -> int:
    \"\"\"统计单词数量\"\"\"
    return len(text.split())
                        """
                    }
                ]
            },
            "advanced_tools": {
                "title": "高级工具示例",
                "examples": [
                    {
                        "name": "异步处理工具",
                        "description": "展示异步处理能力",
                        "code": """
@mcp.tool()
async def async_data_processor(data: List[Any], operation: str) -> Dict[str, Any]:
    \"\"\"异步数据处理\"\"\"
    await asyncio.sleep(0.1)  # 模拟异步操作
    # 处理逻辑...
    return {"result": processed_data}
                        """
                    },
                    {
                        "name": "图片处理工具",
                        "description": "图片格式转换和处理",
                        "code": """
@mcp.tool()
def resize_image(image_data: str, width: int, height: int) -> Dict[str, Any]:
    \"\"\"调整图片大小\"\"\"
    # 图片处理逻辑...
    return {"resized_image": result}
                        """
                    }
                ]
            }
        }
        
        # 错误消息模板
        self.error_messages = {
            "validation_errors": {
                "missing_parameter": "缺少必需参数: {param}",
                "invalid_type": "参数 {param} 类型错误，期望 {expected_type}，得到 {actual_type}",
                "out_of_range": "参数 {param} 超出有效范围 [{min}, {max}]",
                "invalid_format": "参数 {param} 格式无效"
            },
            "execution_errors": {
                "tool_not_found": "工具 {tool_name} 不存在",
                "resource_not_found": "资源 {resource_path} 不存在",
                "execution_failed": "工具执行失败: {error}",
                "timeout": "工具执行超时（超过 {timeout} 秒）"
            },
            "system_errors": {
                "internal_error": "内部服务器错误",
                "service_unavailable": "服务暂时不可用",
                "rate_limit_exceeded": "请求频率超限，请稍后再试"
            }
        }
        
        # 响应格式模板
        self.response_formats = {
            "success_response": {
                "status": "success",
                "data": {},
                "timestamp": "ISO 8601 格式时间戳",
                "request_id": "唯一请求标识符"
            },
            "error_response": {
                "status": "error",
                "error": {
                    "code": "错误代码",
                    "message": "错误消息",
                    "details": "详细错误信息"
                },
                "timestamp": "ISO 8601 格式时间戳",
                "request_id": "唯一请求标识符"
            },
            "validation_error": {
                "status": "validation_error",
                "errors": [
                    {
                        "field": "字段名",
                        "message": "验证错误消息"
                    }
                ],
                "timestamp": "ISO 8601 格式时间戳"
            }
        }
    
    # ===== 配置相关资源 =====
    
    def get_app_settings(self) -> Dict[str, Any]:
        """
        获取应用程序设置
        
        Returns:
            应用程序配置设置
            
        Example:
            >>> get_app_settings()
            {
                "app_name": "FastMCP Learning Demo",
                "version": "0.1.0",
                "environment": "development",
                "debug_mode": True,
                "max_request_size": "10MB",
                "rate_limit": {
                    "requests_per_minute": 100,
                    "requests_per_hour": 1000
                }
            }
        """
        return self.app_settings.copy()
    
    def get_database_config(self) -> Dict[str, Any]:
        """
        获取数据库配置
        
        Returns:
            数据库连接和配置信息
            
        Example:
            >>> get_database_config()
            {
                "default": {
                    "engine": "postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "database": "fastmcp_demo",
                    "connection_pool": {
                        "min_connections": 5,
                        "max_connections": 20
                    }
                }
            }
        """
        return self.database_config.copy()
    
    def get_api_endpoints(self) -> Dict[str, Any]:
        """
        获取API端点配置
        
        Returns:
            API端点信息和描述
            
        Example:
            >>> get_api_endpoints()
            {
                "tools": {
                    "base_path": "/tools",
                    "methods": ["POST"],
                    "description": "工具调用端点"
                },
                "resources": {
                    "base_path": "/resources",
                    "methods": ["GET"],
                    "description": "资源访问端点"
                }
            }
        """
        return self.api_endpoints.copy()
    
    # ===== 文档和参考资源 =====
    
    def get_mcp_guide(self) -> Dict[str, Any]:
        """
        获取MCP开发指南
        
        Returns:
            FastMCP开发指南和文档
            
        Example:
            >>> get_mcp_guide()
            {
                "title": "FastMCP 开发指南",
                "sections": [
                    {
                        "title": "快速开始",
                        "content": "FastMCP 是一个基于 Python 的高效框架..."
                    }
                ],
                "last_updated": "2024-01-15"
            }
        """
        return self.mcp_guide.copy()
    
    def get_api_reference(self) -> Dict[str, Any]:
        """
        获取API参考文档
        
        Returns:
            API接口参考文档
            
        Example:
            >>> get_api_reference()
            {
                "version": "v1.0",
                "base_url": "http://localhost:8000",
                "endpoints": [
                    {
                        "path": "/tools/{tool_name}",
                        "method": "POST",
                        "description": "调用指定工具"
                    }
                ]
            }
        """
        return self.api_reference.copy()
    
    def get_best_practices(self) -> Dict[str, Any]:
        """
        获取最佳实践指南
        
        Returns:
            开发最佳实践和建议
            
        Example:
            >>> get_best_practices()
            {
                "tool_design": {
                    "title": "工具设计最佳实践",
                    "items": [
                        "使用明确的函数签名和类型注解",
                        "提供详细的文档字符串"
                    ]
                }
            }
        """
        return self.best_practices.copy()
    
    # ===== 静态数据资源 =====
    
    def get_countries(self, continent: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取国家列表
        
        Args:
            continent: 大洲过滤器（可选）
            
        Returns:
            国家信息列表
            
        Example:
            >>> get_countries("Asia")
            [
                {"code": "CN", "name": "China", "continent": "Asia", "population": 1412000000},
                {"code": "JP", "name": "Japan", "continent": "Asia", "population": 125800000}
            ]
        """
        countries = self.countries.copy()
        
        if continent:
            countries = [country for country in countries if country["continent"] == continent]
        
        return countries
    
    def get_currencies(self, country: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取货币列表
        
        Args:
            country: 国家过滤器（可选）
            
        Returns:
            货币信息列表
            
        Example:
            >>> get_currencies("United States")
            [{"code": "USD", "name": "US Dollar", "symbol": "$", "country": "United States"}]
        """
        currencies = self.currencies.copy()
        
        if country:
            currencies = [currency for currency in currencies if currency["country"] == country]
        
        return currencies
    
    def get_timezones(self, offset: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取时区列表
        
        Args:
            offset: 时区偏移过滤器（可选），如"+08:00"
            
        Returns:
            时区信息列表
            
        Example:
            >>> get_timezones("+08:00")
            [{"name": "Asia/Shanghai", "offset": "+08:00", "description": "China Standard Time"}]
        """
        timezones = self.timezones.copy()
        
        if offset:
            timezones = [tz for tz in timezones if tz["offset"] == offset]
        
        return timezones
    
    def get_programming_languages(self, paradigm: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取编程语言列表
        
        Args:
            paradigm: 编程范式过滤器（可选）
            
        Returns:
            编程语言信息列表
            
        Example:
            >>> get_programming_languages("Object-oriented")
            [
                {
                    "name": "Python",
                    "type": "Interpreted",
                    "paradigm": ["Object-oriented", "Procedural", "Functional"],
                    "year_created": 1991
                }
            ]
        """
        languages = self.programming_languages.copy()
        
        if paradigm:
            languages = [lang for lang in languages if paradigm in lang["paradigm"]]
        
        return languages
    
    # ===== 模板和示例资源 =====
    
    def get_code_examples(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        获取代码示例
        
        Args:
            category: 示例类别（可选）
            
        Returns:
            代码示例和模板
            
        Example:
            >>> get_code_examples("basic_tools")
            {
                "title": "基础工具示例",
                "examples": [
                    {
                        "name": "计算器工具",
                        "description": "简单的数学计算工具",
                        "code": "@mcp.tool()\\ndef add(a: int, b: int) -> int:..."
                    }
                ]
            }
        """
        examples = self.code_examples.copy()
        
        if category and category in examples:
            return {category: examples[category]}
        
        return examples
    
    def get_error_messages(self, error_type: Optional[str] = None) -> Dict[str, Any]:
        """
        获取错误消息模板
        
        Args:
            error_type: 错误类型（可选）
            
        Returns:
            错误消息模板
            
        Example:
            >>> get_error_messages("validation_errors")
            {
                "missing_parameter": "缺少必需参数: {param}",
                "invalid_type": "参数 {param} 类型错误..."
            }
        """
        messages = self.error_messages.copy()
        
        if error_type and error_type in messages:
            return {error_type: messages[error_type]}
        
        return messages
    
    def get_response_formats(self, format_type: Optional[str] = None) -> Dict[str, Any]:
        """
        获取响应格式模板
        
        Args:
            format_type: 格式类型（可选）
            
        Returns:
            响应格式模板
            
        Example:
            >>> get_response_formats("success_response")
            {
                "status": "success",
                "data": {},
                "timestamp": "ISO 8601 格式时间戳",
                "request_id": "唯一请求标识符"
            }
        """
        formats = self.response_formats.copy()
        
        if format_type and format_type in formats:
            return {format_type: formats[format_type]}
        
        return formats
    
    # ===== 系统信息资源 =====
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        获取系统信息
        
        Returns:
            系统环境和配置信息
            
        Example:
            >>> get_system_info()
            {
                "server_name": "FastMCP Learning Demo",
                "version": "0.1.0",
                "python_version": "3.10.0",
                "platform": "Linux-5.4.0-x86_64",
                "start_time": "2024-01-15T10:30:00Z",
                "uptime_seconds": 3600
            }
        """
        import platform
        import sys
        
        return {
            "server_name": self.app_settings["app_name"],
            "version": self.app_settings["version"],
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "start_time": getattr(self, 'start_time', datetime.now()).isoformat(),
            "current_time": datetime.now().isoformat(),
            "uptime_seconds": (datetime.now() - getattr(self, 'start_time', datetime.now())).total_seconds()
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        获取系统健康状态
        
        Returns:
            系统健康检查结果
            
        Example:
            >>> get_system_health()
            {
                "status": "healthy",
                "checks": {
                    "memory": {"status": "ok", "usage_percent": 45},
                    "disk": {"status": "ok", "usage_percent": 62}
                },
                "last_check": "2024-01-15T10:30:00Z"
            }
        """
        import psutil
        
        health_status = "healthy"
        checks = {}
        
        try:
            # 内存检查
            memory = psutil.virtual_memory()
            checks["memory"] = {
                "status": "ok" if memory.percent < 90 else "warning",
                "usage_percent": memory.percent,
                "available_gb": round(memory.available / (1024**3), 2)
            }
            
            if memory.percent >= 90:
                health_status = "warning"
            
            # 磁盘检查
            disk = psutil.disk_usage('/')
            checks["disk"] = {
                "status": "ok" if disk.percent < 85 else "warning",
                "usage_percent": disk.percent,
                "free_gb": round(disk.free / (1024**3), 2)
            }
            
            if disk.percent >= 85:
                health_status = "warning"
            
            # CPU检查
            cpu_percent = psutil.cpu_percent(interval=1)
            checks["cpu"] = {
                "status": "ok" if cpu_percent < 80 else "warning",
                "usage_percent": cpu_percent,
                "core_count": psutil.cpu_count()
            }
            
            if cpu_percent >= 80:
                health_status = "warning"
            
        except Exception as e:
            health_status = "error"
            checks["system"] = {
                "status": "error",
                "error": str(e)
            }
        
        return {
            "status": health_status,
            "checks": checks,
            "last_check": datetime.now().isoformat()
        }
    
    def get_system_metrics(self, duration: str = "1h") -> Dict[str, Any]:
        """
        获取系统指标
        
        Args:
            duration: 指标时间范围，如"1h", "24h", "7d"
            
        Returns:
            系统性能指标
            
        Example:
            >>> get_system_metrics("1h")
            {
                "requests": {"total": 1000, "successful": 950, "failed": 50},
                "response_times": {"avg_ms": 150, "max_ms": 2000, "min_ms": 50},
                "resource_usage": {"cpu_avg": 25, "memory_avg": 60}
            }
        """
        import psutil
        
        # 这里应该连接到真实的指标存储系统
        # 现在返回模拟数据
        
        if duration == "1h":
            return {
                "requests": {
                    "total": 1000,
                    "successful": 950,
                    "failed": 50,
                    "success_rate": 95.0
                },
                "response_times": {
                    "avg_ms": 150,
                    "max_ms": 2000,
                    "min_ms": 50,
                    "p95_ms": 500,
                    "p99_ms": 1200
                },
                "resource_usage": {
                    "cpu_avg": 25,
                    "cpu_max": 80,
                    "memory_avg": 60,
                    "memory_max": 75,
                    "disk_io_mb": 150
                },
                "time_range": {
                    "start": (datetime.now() - timedelta(hours=1)).isoformat(),
                    "end": datetime.now().isoformat(),
                    "duration": "1h"
                }
            }
        
        elif duration == "24h":
            return {
                "requests": {
                    "total": 24000,
                    "successful": 22800,
                    "failed": 1200,
                    "success_rate": 95.0
                },
                "response_times": {
                    "avg_ms": 145,
                    "max_ms": 3000,
                    "min_ms": 45,
                    "p95_ms": 480,
                    "p99_ms": 1100
                },
                "resource_usage": {
                    "cpu_avg": 28,
                    "cpu_max": 85,
                    "memory_avg": 58,
                    "memory_max": 78,
                    "disk_io_mb": 3600
                },
                "time_range": {
                    "start": (datetime.now() - timedelta(days=1)).isoformat(),
                    "end": datetime.now().isoformat(),
                    "duration": "24h"
                }
            }
        
        else:  # 7d
            return {
                "requests": {
                    "total": 168000,
                    "successful": 159600,
                    "failed": 8400,
                    "success_rate": 95.0
                },
                "response_times": {
                    "avg_ms": 142,
                    "max_ms": 3500,
                    "min_ms": 40,
                    "p95_ms": 460,
                    "p99_ms": 1050
                },
                "resource_usage": {
                    "cpu_avg": 26,
                    "cpu_max": 88,
                    "memory_avg": 59,
                    "memory_max": 82,
                    "disk_io_mb": 25200
                },
                "time_range": {
                    "start": (datetime.now() - timedelta(days=7)).isoformat(),
                    "end": datetime.now().isoformat(),
                    "duration": "7d"
                }
            }