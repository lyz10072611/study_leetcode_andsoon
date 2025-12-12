#!/usr/bin/env python3
"""
FastMCP 资源服务器示例
展示了各种资源管理功能
"""

from fastmcp import FastMCP
from typing import Dict, List, Any
import json
import time

# 创建资源 MCP 服务器
mcp = FastMCP("资源学习服务器")

# 静态资源示例
@mcp.resource("books://all")
def get_all_books() -> List[Dict[str, Any]]:
    """获取所有图书"""
    return [
        {"id": 1, "title": "Python编程入门", "author": "张三", "year": 2023},
        {"id": 2, "title": "FastMCP实战指南", "author": "李四", "year": 2024},
        {"id": 3, "title": "机器学习基础", "author": "王五", "year": 2023},
        {"id": 4, "title": "深度学习进阶", "author": "赵六", "year": 2024}
    ]

@mcp.resource("books://{book_id}")
def get_book_by_id(book_id: str) -> Dict[str, Any]:
    """根据ID获取具体图书"""
    books = {
        "1": {"id": 1, "title": "Python编程入门", "author": "张三", "year": 2023, "pages": 350, "genre": "编程"},
        "2": {"id": 2, "title": "FastMCP实战指南", "author": "李四", "year": 2024, "pages": 280, "genre": "技术"},
        "3": {"id": 3, "title": "机器学习基础", "author": "王五", "year": 2023, "pages": 420, "genre": "AI"},
        "4": {"id": 4, "title": "深度学习进阶", "author": "赵六", "year": 2024, "pages": 380, "genre": "AI"}
    }
    
    book = books.get(book_id)
    if book:
        return book
    else:
        return {"error": "图书未找到", "book_id": book_id}

@mcp.resource("weather://{city}")
def get_weather_data(city: str) -> Dict[str, Any]:
    """获取城市天气数据（模拟）"""
    weather_data = {
        "beijing": {"city": "北京", "temperature": 25, "condition": "晴", "humidity": 45, "wind_speed": 10},
        "shanghai": {"city": "上海", "temperature": 28, "condition": "多云", "humidity": 60, "wind_speed": 15},
        "guangzhou": {"city": "广州", "temperature": 32, "condition": "雨", "humidity": 80, "wind_speed": 8},
        "shenzhen": {"city": "深圳", "temperature": 30, "condition": "阴", "humidity": 70, "wind_speed": 12}
    }
    
    city_lower = city.lower()
    if city_lower in weather_data:
        data = weather_data[city_lower].copy()
        data["timestamp"] = time.ctime()
        data["unit"] = "摄氏度"
        return data
    else:
        return {"error": "城市数据未找到", "city": city}

@mcp.resource("users://profile/{user_id}")
def get_user_profile(user_id: str) -> Dict[str, Any]:
    """获取用户档案"""
    profiles = {
        "1001": {"id": 1001, "name": "张三", "email": "zhangsan@example.com", "role": "开发者", "level": "高级"},
        "1002": {"id": 1002, "name": "李四", "email": "lisi@example.com", "role": "设计师", "level": "中级"},
        "1003": {"id": 1003, "name": "王五", "email": "wangwu@example.com", "role": "产品经理", "level": "高级"}
    }
    
    return profiles.get(user_id, {"error": "用户不存在", "user_id": user_id})

# 动态资源 - 时间相关
@mcp.resource("time://current")
def get_current_time() -> Dict[str, str]:
    """获取当前时间"""
    return {
        "current_time": time.ctime(),
        "timestamp": str(int(time.time())),
        "timezone": "UTC+8"
    }

@mcp.resource("time://formatted/{format}")
def get_formatted_time(format: str) -> Dict[str, str]:
    """获取格式化时间"""
    current_time = time.localtime()
    
    if format == "iso":
        formatted = time.strftime("%Y-%m-%dT%H:%M:%S", current_time)
    elif format == "date":
        formatted = time.strftime("%Y年%m月%d日", current_time)
    elif format == "time":
        formatted = time.strftime("%H:%M:%S", current_time)
    elif format == "full":
        formatted = time.strftime("%Y年%m月%d日 %H:%M:%S", current_time)
    else:
        formatted = time.ctime()
    
    return {
        "format": format,
        "formatted_time": formatted,
        "raw_time": str(int(time.time()))
    }

# 配置资源
@mcp.resource("config://app")
def get_app_config() -> Dict[str, Any]:
    """应用配置"""
    return {
        "app_name": "资源学习服务器",
        "version": "1.0.0",
        "author": "FastMCP学习者",
        "features": {
            "books": True,
            "weather": True,
            "users": True,
            "time": True
        },
        "limits": {
            "max_books_per_request": 10,
            "weather_update_interval": 300,  # 5分钟
            "user_cache_duration": 3600     # 1小时
        }
    }

@mcp.resource("config://endpoints")
def get_available_endpoints() -> Dict[str, Any]:
    """可用端点列表"""
    return {
        "books": {
            "all": "books://all - 获取所有图书",
            "single": "books://{book_id} - 获取具体图书"
        },
        "weather": {
            "city": "weather://{city} - 获取城市天气"
        },
        "users": {
            "profile": "users://profile/{user_id} - 获取用户档案"
        },
        "time": {
            "current": "time://current - 获取当前时间",
            "formatted": "time://formatted/{format} - 获取格式化时间"
        },
        "config": {
            "app": "config://app - 应用配置",
            "endpoints": "config://endpoints - 可用端点"
        }
    }

# 统计资源
@mcp.resource("stats://server")
def get_server_stats() -> Dict[str, Any]:
    """服务器统计信息"""
    return {
        "total_resources": 8,
        "resource_types": ["books", "weather", "users", "time", "config", "stats"],
        "dynamic_resources": 5,
        "static_resources": 3,
        "server_start_time": time.ctime(time.time() - 3600),  # 假设运行了1小时
        "total_requests": 1247,  # 模拟数据
        "average_response_time": "45ms"
    }

# 工具功能 - 用于资源管理
@mcp.tool()
def search_books(keyword: str) -> List[Dict[str, Any]]:
    """搜索图书"""
    all_books = get_all_books()
    keyword_lower = keyword.lower()
    
    results = []
    for book in all_books:
        if (keyword_lower in book["title"].lower() or 
            keyword_lower in book["author"].lower()):
            results.append(book)
    
    return results

@mcp.tool()
def get_weather_summary(cities: List[str]) -> Dict[str, Any]:
    """获取多个城市天气摘要"""
    summary = {}
    for city in cities:
        weather = get_weather_data(city)
        if "error" not in weather:
            summary[city] = {
                "temperature": weather["temperature"],
                "condition": weather["condition"]
            }
        else:
            summary[city] = {"error": weather["error"]}
    
    return {
        "summary": summary,
        "cities_count": len(cities),
        "successful_cities": len([c for c in summary.values() if "error" not in c])
    }

# 提示模板
@mcp.prompt()
def librarian_prompt() -> str:
    """图书管理员提示模板"""
    return """
    你是一个专业的图书管理员，负责管理图书资源和帮助用户查找信息。
    
    你的职责包括：
    1. 管理图书资源（books://all, books://{book_id}）
    2. 帮助用户搜索图书
    3. 提供图书推荐和建议
    4. 维护图书信息系统
    
    请：
    - 友好地回答用户关于图书的问题
    - 帮助用户找到他们需要的图书
    - 提供准确的图书信息
    - 推荐相关的图书资源
    
    记住要保持耐心和乐于助人！
    """

@mcp.prompt()
def weather_forecaster_prompt() -> str:
    """天气预报员提示模板"""
    return """
    你是一个专业的天气预报员，负责提供准确的天气信息和预报。
    
    你的能力包括：
    1. 获取城市天气数据（weather://{city}）
    2. 提供多个城市天气摘要
    3. 分析天气趋势
    4. 给出天气相关建议
    
    请：
    - 准确报告当前天气状况
    - 提供有用的天气建议
    - 解释天气数据的含义
    - 帮助用户理解天气变化
    
    确保信息的准确性和实用性！
    """

if __name__ == "__main__":
    print("📚 启动 FastMCP 资源服务器...")
    print("\n可用资源：")
    print("📖 图书资源：books://all, books://{book_id}")
    print("🌤️  天气资源：weather://{city}")
    print("👤 用户资源：users://profile/{user_id}")
    print("⏰ 时间资源：time://current, time://formatted/{format}")
    print("⚙️  配置资源：config://app, config://endpoints")
    print("📊 统计资源：stats://server")
    print("\n可用工具：")
    print("🔍 图书搜索：search_books")
    print("🌦️  天气摘要：get_weather_summary")
    print("\n服务器正在运行，按 Ctrl+C 停止...")
    
    mcp.run()