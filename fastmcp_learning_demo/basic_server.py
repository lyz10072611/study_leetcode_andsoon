#!/usr/bin/env python3
"""
FastMCP 基础服务器示例
这是最简单的 FastMCP 服务器实现，展示了核心概念
"""

from fastmcp import FastMCP

# 创建 MCP 服务器实例
mcp = FastMCP("基础学习服务器")

# 基础工具示例：加法
@mcp.tool()
def add(a: int, b: int) -> int:
    """两个数字相加"""
    return a + b

# 基础工具示例：字符串处理
@mcp.tool()
def reverse_string(text: str) -> str:
    """反转字符串"""
    return text[::-1]

# 基础资源示例：静态数据
@mcp.resource("config://app")
def get_app_config() -> dict:
    """获取应用配置"""
    return {
        "name": "FastMCP学习应用",
        "version": "1.0.0",
        "author": "学习者"
    }

# 基础资源示例：动态数据
@mcp.resource("user://profile/{user_id}")
def get_user_profile(user_id: str) -> dict:
    """获取用户档案"""
    # 模拟数据库查询
    users = {
        "123": {"name": "张三", "age": 25, "city": "北京"},
        "456": {"name": "李四", "age": 30, "city": "上海"}
    }
    return users.get(user_id, {"error": "用户不存在"})

# 基础提示模板示例
@mcp.prompt()
def math_helper() -> str:
    """数学助手提示模板"""
    return """
    你是一个数学助手，可以帮助用户进行各种数学计算。
    你可以使用以下工具：
    - add: 进行加法运算
    - reverse_string: 反转字符串
    
    请友好地回答用户的问题，并在需要时使用工具。
    """

if __name__ == "__main__":
    # 运行服务器
    print("🚀 启动基础 FastMCP 服务器...")
    print("可用工具：")
    print("- add: 两个数字相加")
    print("- reverse_string: 反转字符串")
    print("可用资源：")
    print("- config://app: 应用配置")
    print("- user://profile/{user_id}: 用户档案")
    print("\n服务器正在运行，按 Ctrl+C 停止...")
    
    mcp.run()