#!/usr/bin/env python3
"""
FastMCP学习演示项目 - 运行脚本

这个脚本提供了多种运行方式，方便开发者快速启动和测试FastMCP服务器。
"""

import argparse
import sys
import os
from pathlib import Path

# 将src目录添加到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.server import create_server


def run_basic_server():
    """运行基础服务器"""
    print("🚀 启动FastMCP基础服务器...")
    server = create_server()
    server.run(port=8000, transport="sse")


def run_advanced_server():
    """运行高级功能服务器"""
    print("🚀 启动FastMCP高级功能服务器...")
    server = create_server()
    server.run(port=8001, transport="sse", debug=True)


def run_production_server():
    """运行生产环境服务器"""
    print("🚀 启动FastMCP生产环境服务器...")
    server = create_server()
    server.run(host="0.0.0.0", port=8000, transport="sse")


def run_development_server():
    """运行开发环境服务器"""
    print("🔧 启动FastMCP开发环境服务器...")
    server = create_server()
    server.run(port=8000, transport="sse", debug=True)


def run_stdio_server():
    """运行stdio模式服务器"""
    print("📡 启动FastMCP stdio模式服务器...")
    server = create_server()
    server.run(transport="stdio")


def test_server():
    """测试服务器功能"""
    print("🧪 测试FastMCP服务器功能...")
    
    # 这里可以添加基本的连接测试
    import requests
    import json
    
    try:
        # 测试系统状态
        response = requests.get("http://localhost:8000/resources/system/status")
        if response.status_code == 200:
            print("✅ 系统状态接口正常")
            print(f"系统信息: {response.json()}")
        else:
            print(f"❌ 系统状态接口异常: {response.status_code}")
            
        # 测试基础工具
        tool_response = requests.post(
            "http://localhost:8000/tools/add",
            json={"a": 5, "b": 3},
            headers={"Content-Type": "application/json"}
        )
        if tool_response.status_code == 200:
            print("✅ 基础工具接口正常")
            print(f"计算结果: 5 + 3 = {tool_response.json()}")
        else:
            print(f"❌ 基础工具接口异常: {tool_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器正在运行")
        print("请使用 'python run.py dev' 启动开发服务器")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")


def show_examples():
    """显示使用示例"""
    print("📖 FastMCP学习演示项目 - 使用示例")
    print("=" * 50)
    
    examples = [
        {
            "name": "基础数学计算",
            "description": "使用加法工具",
            "command": "curl -X POST http://localhost:8000/tools/add -H 'Content-Type: application/json' -d '{\"a\": 10, \"b\": 20}'",
            "expected": "30"
        },
        {
            "name": "文本分析",
            "description": "分析文本内容",
            "command": "curl -X POST http://localhost:8000/tools/analyze_text -H 'Content-Type: application/json' -d '{\"text\": \"Hello world! This is a test.\"}'",
            "expected": "包含字符数、单词数、句子数等统计信息"
        },
        {
            "name": "获取系统状态",
            "description": "查看服务器状态",
            "command": "curl http://localhost:8000/resources/system/status",
            "expected": "服务器运行状态、版本信息、模块加载情况等"
        },
        {
            "name": "获取可用工具列表",
            "description": "查看所有可用工具",
            "command": "curl http://localhost:8000/resources/tools/list",
            "expected": "工具列表、分类、描述等信息"
        },
        {
            "name": "获取学习路径",
            "description": "查看推荐的学习路径",
            "command": "curl http://localhost:8000/resources/learning/paths",
            "expected": "初学者、进阶、专家等不同级别的学习路径"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['name']}")
        print(f"   描述: {example['description']}")
        print(f"   命令: {example['command']}")
        print(f"   预期结果: {example['expected']}")
    
    print("\n" + "=" * 50)
    print("💡 提示: 确保服务器正在运行后再执行这些命令")
    print("💡 可以使用 'python run.py dev' 启动开发服务器")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="FastMCP学习演示项目运行脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python run.py basic          # 运行基础服务器
    python run.py dev            # 运行开发服务器
    python run.py advanced       # 运行高级功能服务器
    python run.py production     # 运行生产环境服务器
    python run.py stdio          # 运行stdio模式服务器
    python run.py test           # 测试服务器功能
    python run.py examples       # 显示使用示例
        """
    )
    
    parser.add_argument(
        "mode",
        choices=["basic", "dev", "advanced", "production", "stdio", "test", "examples"],
        help="运行模式"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="服务器端口（默认: 8000）"
    )
    
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="服务器主机（默认: 127.0.0.1）"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式"
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == "basic":
            run_basic_server()
        elif args.mode == "dev":
            run_development_server()
        elif args.mode == "advanced":
            run_advanced_server()
        elif args.mode == "production":
            run_production_server()
        elif args.mode == "stdio":
            run_stdio_server()
        elif args.mode == "test":
            test_server()
        elif args.mode == "examples":
            show_examples()
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n👋 用户中断，正在关闭服务器...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()