"""
FastMCP学习演示服务器

这是一个完整的FastMCP服务器实现，展示了所有核心功能和高级特性。
服务器包含基础工具、高级工具、静态资源、动态资源、提示模板等。
"""

from fastmcp import FastMCP, Context
from typing import Dict, Any, Optional, List
import asyncio
import logging
from datetime import datetime
import json
import os
from pathlib import Path

# 导入工具模块
from .tools.basic_tools import BasicTools
from .tools.text_tools import TextTools
from .tools.advanced_tools import AdvancedTools

# 导入资源模块
from .resources.static_resources import StaticResources
from .resources.dynamic_resources import DynamicResources
from .resources.user_resources import UserResources
from .resources.config_resources import ConfigResources

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FastMCPLearningServer:
    """FastMCP学习演示服务器"""
    
    def __init__(self):
        """初始化服务器"""
        self.start_time = datetime.now()
        self.request_count = 0
        
        # 创建FastMCP服务器实例
        self.mcp = FastMCP(
            "FastMCPLearningDemo",
            version="0.1.0",
            description="一个全面的FastMCP学习演示项目"
        )
        
        # 初始化各个模块
        self._initialize_modules()
        
        # 注册自定义资源
        self._register_custom_resources()
        
        # 注册提示模板
        self._register_prompts()
        
        logger.info("FastMCP学习演示服务器初始化完成")
    
    def _initialize_modules(self):
        """初始化各个功能模块"""
        logger.info("初始化功能模块...")
        
        # 初始化工具模块
        self.basic_tools = BasicTools(self.mcp)
        self.text_tools = TextTools(self.mcp)
        self.advanced_tools = AdvancedTools(self.mcp)
        
        # 初始化资源模块
        self.static_resources = StaticResources(self.mcp)
        self.dynamic_resources = DynamicResources(self.mcp)
        self.user_resources = UserResources(self.mcp)
        self.config_resources = ConfigResources(self.mcp)
        
        logger.info("所有功能模块初始化完成")
    
    def _register_custom_resources(self):
        """注册自定义资源"""
        logger.info("注册自定义资源...")
        
        # 系统信息资源
        @self.mcp.resource("/system/status")
        def get_system_status() -> Dict[str, Any]:
            """获取系统状态信息"""
            uptime = datetime.now() - self.start_time
            return {
                "server_name": "FastMCP Learning Demo",
                "version": "0.1.0",
                "status": "running",
                "start_time": self.start_time.isoformat(),
                "uptime_seconds": uptime.total_seconds(),
                "uptime_human": str(uptime).split('.')[0],  # 移除微秒
                "request_count": self.request_count,
                "modules_loaded": {
                    "basic_tools": True,
                    "text_tools": True,
                    "advanced_tools": True,
                    "static_resources": True,
                    "dynamic_resources": True,
                    "user_resources": True,
                    "config_resources": True
                }
            }
        
        # 可用工具列表资源
        @self.mcp.resource("/tools/list")
        def get_available_tools() -> Dict[str, Any]:
            """获取所有可用工具列表"""
            # 这里应该动态获取工具列表，现在返回示例数据
            return {
                "tools": [
                    {
                        "name": "add",
                        "category": "basic_tools",
                        "description": "将两个数字相加",
                        "parameters": ["a", "b"],
                        "return_type": "number"
                    },
                    {
                        "name": "analyze_text",
                        "category": "text_tools",
                        "description": "全面分析文本",
                        "parameters": ["text"],
                        "return_type": "object"
                    },
                    {
                        "name": "resize_image",
                        "category": "advanced_tools",
                        "description": "调整图片大小",
                        "parameters": ["image_data", "width", "height"],
                        "return_type": "object"
                    }
                ],
                "total_count": 50,  # 示例数量
                "categories": ["basic_tools", "text_tools", "advanced_tools"]
            }
        
        # 可用资源列表资源
        @self.mcp.resource("/resources/list")
        def get_available_resources() -> Dict[str, Any]:
            """获取所有可用资源列表"""
            return {
                "resources": [
                    {
                        "path": "/config/app-settings",
                        "category": "static_resources",
                        "description": "应用程序设置"
                    },
                    {
                        "path": "/data/countries",
                        "category": "static_resources",
                        "description": "国家数据列表"
                    },
                    {
                        "path": "/system/status",
                        "category": "system",
                        "description": "系统状态信息"
                    }
                ],
                "total_count": 25,  # 示例数量
                "categories": ["static_resources", "dynamic_resources", "system"]
            }
        
        # 学习路径资源
        @self.mcp.resource("/learning/paths")
        def get_learning_paths() -> Dict[str, Any]:
            """获取学习路径指南"""
            return {
                "paths": [
                    {
                        "id": "beginner",
                        "name": "初学者路径",
                        "description": "适合FastMCP新手的入门路径",
                        "estimated_time": "2-3小时",
                        "modules": [
                            {
                                "name": "基础概念",
                                "topics": ["MCP协议简介", "FastMCP特点", "核心组件"]
                            },
                            {
                                "name": "环境搭建",
                                "topics": ["安装FastMCP", "创建第一个服务器", "运行示例"]
                            },
                            {
                                "name": "基础工具",
                                "topics": ["数学计算工具", "字符串处理工具", "工具设计原则"]
                            }
                        ]
                    },
                    {
                        "id": "intermediate",
                        "name": "进阶路径",
                        "description": "深入学习FastMCP高级功能",
                        "estimated_time": "4-5小时",
                        "prerequisites": ["完成初学者路径"],
                        "modules": [
                            {
                                "name": "高级工具",
                                "topics": ["异步处理", "图片处理", "网络请求"]
                            },
                            {
                                "name": "资源管理",
                                "topics": ["静态资源", "动态资源", "资源设计最佳实践"]
                            },
                            {
                                "name": "企业级特性",
                                "topics": ["认证授权", "日志监控", "性能优化"]
                            }
                        ]
                    },
                    {
                        "id": "advanced",
                        "name": "专家路径",
                        "description": "掌握FastMCP高级技巧和最佳实践",
                        "estimated_time": "6-8小时",
                        "prerequisites": ["完成进阶路径"],
                        "modules": [
                            {
                                "name": "架构设计",
                                "topics": ["微服务架构", "分布式部署", "高可用性设计"]
                            },
                            {
                                "name": "性能优化",
                                "topics": ["缓存策略", "负载均衡", "数据库优化"]
                            },
                            {
                                "name": "安全实践",
                                "topics": ["安全认证", "数据加密", "访问控制"]
                            }
                        ]
                    }
                ],
                "recommended_order": ["beginner", "intermediate", "advanced"]
            }
        
        # 示例项目资源
        @self.mcp.resource("/examples/projects")
        def get_example_projects() -> Dict[str, Any]:
            """获取示例项目列表"""
            return {
                "projects": [
                    {
                        "name": "计算器服务",
                        "description": "简单的数学计算工具集合",
                        "difficulty": "简单",
                        "tools": ["add", "subtract", "multiply", "divide", "power"],
                        "resources": ["/config/calculator-settings"],
                        "learning_points": ["基础工具创建", "类型注解", "错误处理"]
                    },
                    {
                        "name": "文本分析器",
                        "description": "文本处理和语言分析工具",
                        "difficulty": "中等",
                        "tools": ["analyze_text", "extract_keywords", "detect_language", "calculate_readability"],
                        "resources": ["/data/languages", "/templates/text-analysis"],
                        "learning_points": ["文本处理", "自然语言处理", "数据分析"]
                    },
                    {
                        "name": "图片处理器",
                        "description": "图片格式转换和处理工具",
                        "difficulty": "中等",
                        "tools": ["resize_image", "convert_image_format", "apply_image_filter", "create_thumbnail"],
                        "resources": ["/config/image-settings", "/data/image-formats"],
                        "learning_points": ["图片处理", "文件操作", "异步处理"]
                    },
                    {
                        "name": "数据转换器",
                        "description": "多种数据格式转换工具",
                        "difficulty": "困难",
                        "tools": ["csv_to_json", "json_to_csv", "data_transformation", "generate_report"],
                        "resources": ["/templates/data-formats", "/config/conversion-settings"],
                        "learning_points": ["数据转换", "格式处理", "报告生成"]
                    },
                    {
                        "name": "Web监控器",
                        "description": "网站状态监控和数据抓取工具",
                        "difficulty": "困难",
                        "tools": ["fetch_web_data", "check_website_status", "concurrent_web_scraper"],
                        "resources": ["/config/web-settings", "/data/user-agents"],
                        "learning_points": ["网络请求", "并发处理", "错误重试"]
                    }
                ],
                "total_projects": 5,
                "difficulty_levels": ["简单", "中等", "困难"]
            }
        
        logger.info("自定义资源注册完成")
    
    def _register_prompts(self):
        """注册提示模板"""
        logger.info("注册提示模板...")
        
        # 基础工具使用提示
        BASIC_TOOLS_PROMPT = """
        You are a helpful assistant with access to basic calculation and text processing tools.
        
        Available tools:
        - add(a, b): Add two numbers
        - subtract(a, b): Subtract two numbers  
        - multiply(a, b): Multiply two numbers
        - divide(a, b): Divide two numbers (b cannot be 0)
        - analyze_text(text): Analyze text and return statistics
        - count_words(text): Count words in text
        - reverse_text(text): Reverse text string
        
        When the user asks for calculations or text processing, use the appropriate tools.
        Always check the tool results and provide clear explanations.
        """
        
        # 高级功能使用提示
        ADVANCED_TOOLS_PROMPT = """
        You are an advanced assistant with access to sophisticated tools for image processing, 
        web scraping, and data analysis.
        
        Available tools:
        - resize_image(image_data, width, height): Resize images
        - convert_image_format(image_data, target_format): Convert image formats
        - fetch_web_data(url): Fetch data from web pages
        - concurrent_web_scraper(urls): Scrape multiple URLs concurrently
        - async_data_processor(data, operation): Process data asynchronously
        - generate_report(data, report_type): Generate data reports
        
        For complex tasks, break them down into steps and use the appropriate tools.
        Always validate inputs and handle errors gracefully.
        """
        
        # 学习助手提示
        LEARNING_ASSISTANT_PROMPT = """
        You are a FastMCP learning assistant. Help users understand and use FastMCP effectively.
        
        You have access to:
        - All basic and advanced tools
        - Learning resources at /learning/* paths
        - Example projects at /examples/* paths
        - System information at /system/* paths
        
        When users ask about FastMCP:
        1. First understand their current level (beginner, intermediate, advanced)
        2. Suggest appropriate learning paths from /learning/paths
        3. Recommend relevant example projects from /examples/projects
        4. Provide step-by-step guidance with code examples
        5. Use tools to demonstrate concepts when helpful
        
        Be patient, encouraging, and provide practical examples.
        """
        
        # 注册提示模板资源
        @self.mcp.resource("/prompts/basic-tools")
        def get_basic_tools_prompt() -> str:
            """获取基础工具使用提示模板"""
            return BASIC_TOOLS_PROMPT
        
        @self.mcp.resource("/prompts/advanced-tools")
        def get_advanced_tools_prompt() -> str:
            """获取高级工具使用提示模板"""
            return ADVANCED_TOOLS_PROMPT
        
        @self.mcp.resource("/prompts/learning-assistant")
        def get_learning_assistant_prompt() -> str:
            """获取学习助手提示模板"""
            return LEARNING_ASSISTANT_PROMPT
        
        @self.mcp.resource("/prompts/code-generator")
        def get_code_generator_prompt() -> str:
            """获取代码生成器提示模板"""
            return """
            You are a FastMCP code generator. Create clean, well-documented FastMCP code based on user requirements.
            
            Guidelines:
            1. Use proper type annotations
            2. Include comprehensive docstrings
            3. Handle errors gracefully
            4. Follow FastMCP best practices
            5. Provide usage examples
            6. Use meaningful function and parameter names
            
            Structure your code:
            - Imports at the top
            - Clear function definitions with @mcp.tool() or @mcp.resource()
            - Proper error handling
            - Return appropriate data types
            - Include examples in docstrings
            
            Always test the code mentally and consider edge cases.
            """
        
        logger.info("提示模板注册完成")
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, 
            transport: str = "sse", debug: bool = False):
        """
        运行服务器
        
        Args:
            host: 主机地址
            port: 端口号
            transport: 传输方式 ("sse" 或 "stdio")
            debug: 是否启用调试模式
        """
        logger.info(f"启动FastMCP学习演示服务器...")
        logger.info(f"主机: {host}:{port}")
        logger.info(f"传输方式: {transport}")
        logger.info(f"调试模式: {debug}")
        
        try:
            self.mcp.run(
                host=host,
                port=port,
                transport=transport,
                debug=debug
            )
        except KeyboardInterrupt:
            logger.info("服务器被用户中断")
        except Exception as e:
            logger.error(f"服务器运行错误: {e}")
            raise


def create_server() -> FastMCPLearningServer:
    """创建服务器实例"""
    return FastMCPLearningServer()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="FastMCP学习演示服务器")
    parser.add_argument("--host", default="0.0.0.0", help="主机地址")
    parser.add_argument("--port", type=int, default=8000, help="端口号")
    parser.add_argument("--transport", default="sse", choices=["sse", "stdio"], help="传输方式")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    server = create_server()
    server.run(
        host=args.host,
        port=args.port,
        transport=args.transport,
        debug=args.debug
    )


if __name__ == "__main__":
    main()