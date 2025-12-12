#!/usr/bin/env python3
"""
FastMCP 客户端调用示例
展示了如何使用 FastMCP 客户端调用 MCP 服务器
"""

import asyncio
from fastmcp import Client

async def test_basic_server():
    """测试基础服务器"""
    print("🚀 测试基础服务器...")
    
    async with Client("http://localhost:8000") as client:
        # 测试加法工具
        result = await client.call_tool("add", {"a": 5, "b": 3})
        print(f"加法结果: {result}")
        
        # 测试字符串反转
        result = await client.call_tool("reverse_string", {"text": "Hello FastMCP!"})
        print(f"字符串反转结果: {result}")
        
        # 测试资源访问
        config = await client.read_resource("config://app")
        print(f"应用配置: {config}")
        
        user_profile = await client.read_resource("user://profile/123")
        print(f"用户档案: {user_profile}")

async def test_calculator_server():
    """测试计算器服务器"""
    print("\n🧮 测试计算器服务器...")
    
    async with Client("http://localhost:8001") as client:
        # 测试基础运算
        result = await client.call_tool("add", {"a": 10.5, "b": 20.3})
        print(f"加法: {result}")
        
        result = await client.call_tool("multiply", {"a": 4, "b": 7})
        print(f"乘法: {result}")
        
        # 测试高级运算
        result = await client.call_tool("power", {"base": 2, "exponent": 8})
        print(f"幂运算: {result}")
        
        result = await client.call_tool("sqrt", {"number": 16})
        print(f"平方根: {result}")
        
        # 测试统计分析
        result = await client.call_tool("calculate_average", {"numbers": [85, 92, 78, 95, 88]})
        print(f"平均值: {result}")
        
        # 测试方程求解
        result = await client.call_tool("solve_quadratic", {"a": 1, "b": -5, "c": 6})
        print(f"一元二次方程: {result}")
        
        # 测试资源访问
        constants = await client.read_resource("math://constants")
        print(f"数学常数: {constants}")

async def test_resource_server():
    """测试资源服务器"""
    print("\n📚 测试资源服务器...")
    
    async with Client("http://localhost:8002") as client:
        # 测试静态资源
        books = await client.read_resource("books://all")
        print(f"图书列表: {books}")
        
        # 测试动态资源
        book = await client.read_resource("books://1")
        print(f"具体图书: {book}")
        
        # 测试天气数据
        weather = await client.read_resource("weather://beijing")
        print(f"北京天气: {weather}")

async def test_advanced_server():
    """测试高级服务器"""
    print("\n⚡ 测试高级服务器...")
    
    async with Client("http://localhost:8003") as client:
        # 测试异步工具
        result = await client.call_tool("fetch_data", {"url": "https://httpbin.org/json"})
        print(f"异步数据获取: {result}")
        
        # 测试图片处理
        # 注意：这需要实际的图片文件
        # result = await client.call_tool("resize_image", {"image_path": "test.jpg", "width": 200, "height": 200})
        # print(f"图片处理: {result}")
        
        # 测试文件操作
        result = await client.call_tool("read_file_info", {"file_path": "README.md"})
        print(f"文件信息: {result}")

async def main():
    """主函数：运行所有测试"""
    print("🧪 FastMCP 客户端测试开始...")
    print("=" * 50)
    
    try:
        # 测试基础服务器
        await test_basic_server()
    except Exception as e:
        print(f"基础服务器测试失败: {e}")
    
    try:
        # 测试计算器服务器
        await test_calculator_server()
    except Exception as e:
        print(f"计算器服务器测试失败: {e}")
    
    try:
        # 测试资源服务器
        await test_resource_server()
    except Exception as e:
        print(f"资源服务器测试失败: {e}")
    
    try:
        # 测试高级服务器
        await test_advanced_server()
    except Exception as e:
        print(f"高级服务器测试失败: {e}")
    
    print("\n" + "=" * 50)
    print("✅ 测试完成！")

if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())