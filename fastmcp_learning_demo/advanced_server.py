#!/usr/bin/env python3
"""
FastMCP 高级服务器示例
展示了异步处理、文件操作、图片处理等高级功能
"""

from fastmcp import FastMCP
import asyncio
import aiohttp
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import time

# 创建高级 MCP 服务器
mcp = FastMCP("高级学习服务器")

# 异步工具示例
@mcp.tool()
async def fetch_data(url: str) -> Dict[str, Any]:
    """异步获取网络数据"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return {"success": True, "data": data}
                else:
                    return {"success": False, "error": f"HTTP {response.status}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
async def slow_calculation(number: int) -> Dict[str, Any]:
    """模拟耗时计算"""
    print(f"开始计算 {number} 的平方...")
    await asyncio.sleep(2)  # 模拟耗时操作
    result = number ** 2
    print(f"计算完成: {number}² = {result}")
    return {"number": number, "square": result, "calculation_time": "2秒"}

# 文件操作工具
@mcp.tool()
def read_file_info(file_path: str) -> Dict[str, Any]:
    """读取文件信息"""
    try:
        path = Path(file_path)
        if path.exists():
            stat = path.stat()
            return {
                "exists": True,
                "size": stat.st_size,
                "modified": time.ctime(stat.st_mtime),
                "is_file": path.is_file(),
                "is_directory": path.is_dir()
            }
        else:
            return {"exists": False, "error": "文件不存在"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def list_directory(path: str = ".") -> Dict[str, Any]:
    """列出目录内容"""
    try:
        dir_path = Path(path)
        if dir_path.exists() and dir_path.is_dir():
            items = []
            for item in dir_path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "file" if item.is_file() else "directory",
                    "size": item.stat().st_size if item.is_file() else 0
                })
            return {"success": True, "items": items, "path": str(dir_path.absolute())}
        else:
            return {"success": False, "error": "目录不存在"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# 数据处理工具
@mcp.tool()
def process_json_data(json_string: str) -> Dict[str, Any]:
    """处理 JSON 数据"""
    try:
        data = json.loads(json_string)
        
        # 基本统计信息
        stats = {
            "type": type(data).__name__,
            "length": len(data) if hasattr(data, '__len__') else None
        }
        
        if isinstance(data, dict):
            stats["keys"] = list(data.keys())
            stats["nested_objects"] = sum(1 for v in data.values() if isinstance(v, dict))
            stats["arrays"] = sum(1 for v in data.values() if isinstance(v, list))
        elif isinstance(data, list):
            stats["item_types"] = list(set(type(item).__name__ for item in data))
            stats["total_items"] = len(data)
        
        return {
            "success": True,
            "original_data": data,
            "statistics": stats
        }
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"JSON 解析错误: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def generate_report(data: Dict[str, Any], report_type: str = "summary") -> str:
    """生成数据报告"""
    try:
        if report_type == "summary":
            report = f"数据摘要报告\n"
            report += f"=" * 30 + "\n"
            report += f"数据类型: {type(data).__name__}\n"
            report += f"数据大小: {len(str(data))} 字符\n"
            
            if isinstance(data, dict):
                report += f"键值对数量: {len(data)}\n"
                report += f"键列表: {', '.join(data.keys())}\n"
            elif isinstance(data, list):
                report += f"列表长度: {len(data)}\n"
                
            return report
        elif report_type == "detailed":
            return f"详细分析报告:\n{json.dumps(data, indent=2, ensure_ascii=False)}"
        else:
            return f"不支持的报告类型: {report_type}"
    except Exception as e:
        return f"报告生成失败: {e}"

# 高级资源
@mcp.resource("system://info")
def get_system_info() -> Dict[str, Any]:
    """系统信息"""
    return {
        "platform": os.name,
        "current_directory": os.getcwd(),
        "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        "environment_variables": dict(os.environ),
        "timestamp": time.ctime()
    }

@mcp.resource("logs://recent/{count}")
def get_recent_logs(count: int = 10) -> List[Dict[str, Any]]:
    """最近的日志条目"""
    # 模拟日志数据
    logs = []
    for i in range(min(count, 50)):  # 限制最大数量
        logs.append({
            "id": i + 1,
            "timestamp": time.ctime(time.time() - i * 60),  # 每分钟一条
            "level": "INFO" if i % 3 == 0 else "DEBUG" if i % 3 == 1 else "WARNING",
            "message": f"这是第 {i+1} 条日志消息",
            "source": "advanced_server.py"
        })
    return logs

@mcp.resource("config://advanced")
def get_advanced_config() -> Dict[str, Any]:
    """高级配置"""
    return {
        "server_name": "高级学习服务器",
        "version": "2.0.0",
        "features": {
            "async_support": True,
            "file_operations": True,
            "data_processing": True,
            "logging": True,
            "error_handling": True
        },
        "limits": {
            "max_file_size": "10MB",
            "max_concurrent_requests": 100,
            "timeout_seconds": 30
        },
        "settings": {
            "debug_mode": True,
            "log_level": "INFO",
            "cache_enabled": True
        }
    }

# 高级提示模板
@mcp.prompt()
def data_analyst_prompt() -> str:
    """数据分析师提示模板"""
    return """
    你是一个专业的数据分析师，擅长处理各种数据格式和生成报告。
    
    你的能力包括：
    1. 解析和处理 JSON 数据
    2. 生成各种类型的数据报告
    3. 提供数据统计和分析
    4. 文件和数据管理
    
    请：
    - 仔细分析用户提供的数据
    - 生成清晰、有用的报告
    - 指出数据中的关键信息
    - 提供数据处理的建议
    
    记住要保持专业和准确！
    """

@mcp.prompt()
def system_admin_prompt() -> str:
    """系统管理员提示模板"""
    return """
    你是一个经验丰富的系统管理员，负责监控系统状态和管理文件。
    
    你的职责包括：
    1. 监控系统信息和性能
    2. 管理文件和目录
    3. 查看系统日志
    4. 配置系统参数
    
    请：
    - 及时响应系统问题
    - 提供详细的系统信息
    - 安全地执行文件操作
    - 监控日志和错误信息
    
    确保系统稳定运行！
    """

if __name__ == "__main__":
    print("⚡ 启动 FastMCP 高级服务器...")
    print("\n可用高级工具：")
    print("🌐 异步工具：fetch_data, slow_calculation")
    print("📁 文件操作：read_file_info, list_directory")
    print("📊 数据处理：process_json_data, generate_report")
    print("\n可用高级资源：")
    print("💻 系统信息：system://info")
    print("📋 日志查看：logs://recent/{count}")
    print("⚙️  高级配置：config://advanced")
    print("\n服务器正在运行，按 Ctrl+C 停止...")
    
    mcp.run()