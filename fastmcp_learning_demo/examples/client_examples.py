"""
FastMCP客户端调用示例

这个模块展示了如何使用Python客户端调用FastMCP服务器的工具和资源，
包括同步和异步调用、错误处理、批量操作等高级用法。
"""

import asyncio
import aiohttp
import requests
import json
from typing import Dict, Any, List, Optional
from pathlib import Path


class FastMCPClient:
    """FastMCP客户端类，提供简单易用的API调用接口"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化客户端
        
        Args:
            base_url: 服务器基础URL
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        
    def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用工具
        
        Args:
            tool_name: 工具名称
            parameters: 工具参数
            
        Returns:
            工具执行结果
            
        Example:
            >>> client = FastMCPClient()
            >>> result = client.call_tool("add", {"a": 5, "b": 3})
            >>> print(result)  # {"result": 8}
        """
        url = f"{self.base_url}/tools/{tool_name}"
        
        try:
            response = self.session.post(url, json=parameters)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"请求失败: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"error": f"JSON解析失败: {str(e)}"}
    
    def get_resource(self, resource_path: str) -> Dict[str, Any]:
        """
        获取资源
        
        Args:
            resource_path: 资源路径
            
        Returns:
            资源数据
            
        Example:
            >>> client = FastMCPClient()
            >>> result = client.get_resource("/system/status")
            >>> print(result)  # 系统状态信息
        """
        url = f"{self.base_url}/resources{resource_path}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"请求失败: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"error": f"JSON解析失败: {str(e)}"}
    
    def batch_call_tools(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量调用工具
        
        Args:
            tool_calls: 工具调用列表，每个元素包含tool_name和parameters
            
        Returns:
            批量执行结果
            
        Example:
            >>> client = FastMCPClient()
            >>> calls = [
            ...     {"tool_name": "add", "parameters": {"a": 1, "b": 2}},
            ...     {"tool_name": "multiply", "parameters": {"a": 3, "b": 4}}
            ... ]
            >>> results = client.batch_call_tools(calls)
        """
        results = []
        for call in tool_calls:
            result = self.call_tool(call["tool_name"], call["parameters"])
            results.append({
                "tool_name": call["tool_name"],
                "parameters": call["parameters"],
                "result": result
            })
        return results
    
    def get_available_tools(self) -> List[str]:
        """
        获取可用工具列表
        
        Returns:
            工具名称列表
        """
        resource_data = self.get_resource("/tools/list")
        if "error" in resource_data:
            return []
        
        tools = resource_data.get("tools", [])
        return [tool.get("name", "") for tool in tools if tool.get("name")]
    
    def get_available_resources(self) -> List[str]:
        """
        获取可用资源列表
        
        Returns:
            资源路径列表
        """
        resource_data = self.get_resource("/resources/list")
        if "error" in resource_data:
            return []
        
        resources = resource_data.get("resources", [])
        return [resource.get("path", "") for resource in resources if resource.get("path")]
    
    def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            服务器是否健康
        """
        try:
            response = self.session.get(f"{self.base_url}/resources/system/status")
            return response.status_code == 200
        except:
            return False


class AsyncFastMCPClient:
    """异步FastMCP客户端类"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化异步客户端
        
        Args:
            base_url: 服务器基础URL
        """
        self.base_url = base_url.rstrip("/")
        self.session = None
    
    async def __aenter__(self):
        """异步上下文管理器进入"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        if self.session:
            await self.session.close()
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        异步调用工具
        
        Args:
            tool_name: 工具名称
            parameters: 工具参数
            
        Returns:
            工具执行结果
        """
        url = f"{self.base_url}/tools/{tool_name}"
        
        try:
            async with self.session.post(url, json=parameters) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            return {"error": f"请求失败: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"error": f"JSON解析失败: {str(e)}"}
    
    async def get_resource(self, resource_path: str) -> Dict[str, Any]:
        """
        异步获取资源
        
        Args:
            resource_path: 资源路径
            
        Returns:
            资源数据
        """
        url = f"{self.base_url}/resources{resource_path}"
        
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            return {"error": f"请求失败: {str(e)}"}
        except json.JSONDecodeError as e:
            return {"error": f"JSON解析失败: {str(e)}"}
    
    async def batch_call_tools(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        异步批量调用工具
        
        Args:
            tool_calls: 工具调用列表
            
        Returns:
            批量执行结果
        """
        tasks = []
        for call in tool_calls:
            task = self.call_tool(call["tool_name"], call["parameters"])
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        return [
            {
                "tool_name": call["tool_name"],
                "parameters": call["parameters"],
                "result": result
            }
            for call, result in zip(tool_calls, results)
        ]


def demonstrate_basic_tools():
    """演示基础工具的使用"""
    print("🔧 基础工具演示")
    print("=" * 40)
    
    client = FastMCPClient()
    
    # 数学计算工具
    print("\n📊 数学计算工具:")
    
    # 加法
    result = client.call_tool("add", {"a": 15, "b": 27})
    print(f"15 + 27 = {result}")
    
    # 乘法
    result = client.call_tool("multiply", {"a": 8, "b": 7})
    print(f"8 × 7 = {result}")
    
    # 统计计算
    numbers = [23, 45, 67, 89, 12, 34, 56, 78, 90, 11]
    result = client.call_tool("calculate_statistics", {"numbers": numbers})
    print(f"数字 {numbers} 的统计信息: {result}")
    
    # 字符串处理工具
    print("\n📝 字符串处理工具:")
    
    text = "Hello World! This is a test message for FastMCP demonstration."
    
    # 文本分析
    result = client.call_tool("analyze_text", {"text": text})
    print(f"文本分析结果: {result}")
    
    # 单词统计
    result = client.call_tool("count_words", {"text": text})
    print(f"单词数量: {result}")
    
    # 文本反转
    result = client.call_tool("reverse_text", {"text": "FastMCP"})
    print(f"'FastMCP' 反转后: {result}")


def demonstrate_text_tools():
    """演示文本处理工具的使用"""
    print("\n📝 高级文本处理工具演示")
    print("=" * 40)
    
    client = FastMCPClient()
    
    sample_text = """
    FastMCP is an amazing framework for building MCP servers. 
    It provides excellent tools and resources for developers.
    The learning curve is gentle and the documentation is comprehensive.
    I love using FastMCP for my AI projects!
    """
    
    # 关键词提取
    result = client.call_tool("extract_keywords", {"text": sample_text, "max_keywords": 5})
    print(f"关键词提取: {result}")
    
    # 情感分析
    result = client.call_tool("analyze_sentiment", {"text": sample_text})
    print(f"情感分析: {result}")
    
    # 可读性分析
    result = client.call_tool("calculate_readability", {"text": sample_text})
    print(f"可读性分析: {result}")
    
    # 语言检测
    result = client.call_tool("detect_language", {"text": "Hello world!"})
    print(f"语言检测: {result}")


def demonstrate_advanced_tools():
    """演示高级工具的使用"""
    print("\n🚀 高级工具演示")
    print("=" * 40)
    
    client = FastMCPClient()
    
    # 异步数据处理
    print("\n⚡ 异步数据处理:")
    data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
    result = client.call_tool("async_data_processor", {"data": data, "operation": "sort"})
    print(f"数据排序结果: {result}")
    
    # JSON验证
    print("\n🔍 JSON验证工具:")
    valid_json = '{"name": "FastMCP", "version": "0.1.0", "features": ["tools", "resources", "prompts"]}'
    result = client.call_tool("json_validator", {"json_string": valid_json})
    print(f"JSON验证结果: {result}")
    
    # 数据转换
    print("\n🔄 数据转换工具:")
    csv_data = "name,age,city\nAlice,30,New York\nBob,25,London\nCarol,35,Tokyo"
    result = client.call_tool("csv_to_json", {"csv_content": csv_data})
    print(f"CSV转JSON结果: {result}")


def demonstrate_batch_operations():
    """演示批量操作"""
    print("\n📦 批量操作演示")
    print("=" * 40)
    
    client = FastMCPClient()
    
    # 批量工具调用
    tool_calls = [
        {"tool_name": "add", "parameters": {"a": 10, "b": 5}},
        {"tool_name": "multiply", "parameters": {"a": 3, "b": 7}},
        {"tool_name": "power", "parameters": {"base": 2, "exponent": 8}},
        {"tool_name": "sqrt", "parameters": {"number": 144}},
        {"tool_name": "count_words", "parameters": {"text": "FastMCP is awesome for building AI tools"}}
    ]
    
    results = client.batch_call_tools(tool_calls)
    
    print("批量工具调用结果:")
    for i, result in enumerate(results, 1):
        tool_name = result["tool_name"]
        params = result["parameters"]
        output = result["result"]
        print(f"{i}. {tool_name}({params}) = {output}")


def demonstrate_resources():
    """演示资源访问"""
    print("\n📚 资源访问演示")
    print("=" * 40)
    
    client = FastMCPClient()
    
    # 系统状态
    print("\n🔧 系统状态:")
    result = client.get_resource("/system/status")
    print(f"系统信息: {result}")
    
    # 可用工具列表
    print("\n🛠️ 可用工具:")
    tools = client.get_available_tools()
    print(f"工具数量: {len(tools)}")
    print(f"前10个工具: {tools[:10]}")
    
    # 配置信息
    print("\n⚙️ 配置信息:")
    result = client.get_resource("/config/app-settings")
    print(f"应用设置: {result}")
    
    # 静态数据
    print("\n🌍 静态数据:")
    result = client.get_resource("/data/countries")
    print(f"国家数据（前3个）: {result[:3] if isinstance(result, list) else result}")
    
    result = client.get_resource("/data/currencies")
    print(f"货币数据（前3个）: {result[:3] if isinstance(result, list) else result}")


def demonstrate_error_handling():
    """演示错误处理"""
    print("\n❌ 错误处理演示")
    print("=" * 40)
    
    client = FastMCPClient()
    
    # 除零错误
    print("1. 除零错误:")
    result = client.call_tool("divide", {"a": 10, "b": 0})
    print(f"结果: {result}")
    
    # 负数平方根
    print("\n2. 负数平方根:")
    result = client.call_tool("sqrt", {"number": -25})
    print(f"结果: {result}")
    
    # 不存在的工具
    print("\n3. 不存在的工具:")
    result = client.call_tool("non_existent_tool", {"param": "value"})
    print(f"结果: {result}")
    
    # 不存在的资源
    print("\n4. 不存在的资源:")
    result = client.get_resource("/non/existent/resource")
    print(f"结果: {result}")


async def demonstrate_async_operations():
    """演示异步操作"""
    print("\n⚡ 异步操作演示")
    print("=" * 40)
    
    async with AsyncFastMCPClient() as client:
        # 并发工具调用
        print("\n1. 并发工具调用:")
        tasks = [
            client.call_tool("add", {"a": i, "b": i*2})
            for i in range(1, 6)
        ]
        
        results = await asyncio.gather(*tasks)
        for i, result in enumerate(results, 1):
            print(f"任务{i}: {result}")
        
        # 批量异步操作
        print("\n2. 批量异步操作:")
        tool_calls = [
            {"tool_name": "calculate_statistics", "parameters": {"numbers": list(range(1, 11))}},
            {"tool_name": "count_words", "parameters": {"text": "FastMCP async operations are efficient"}},
            {"tool_name": "reverse_text", "parameters": {"text": "Asynchronous"}},
            {"tool_name": "analyze_text", "parameters": {"text": "FastMCP provides excellent async support"}}
        ]
        
        results = await client.batch_call_tools(tool_calls)
        for i, result in enumerate(results, 1):
            print(f"批量任务{i}: {result}")


def demonstrate_learning_path():
    """演示学习路径"""
    print("\n📚 学习路径演示")
    print("=" * 40)
    
    client = FastMCPClient()
    
    # 获取学习路径
    print("\n1. 获取学习路径:")
    result = client.get_resource("/learning/paths")
    print(f"学习路径信息: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    # 获取示例项目
    print("\n2. 获取示例项目:")
    result = client.get_resource("/examples/projects")
    print(f"示例项目信息: {json.dumps(result, indent=2, ensure_ascii=False)}")


def main():
    """主函数 - 运行所有演示"""
    print("🎯 FastMCP客户端调用示例")
    print("=" * 60)
    print("这个演示展示了如何使用Python客户端调用FastMCP服务器的各种功能。\n")
    
    # 检查服务器是否运行
    client = FastMCPClient()
    if not client.health_check():
        print("❌ 服务器未运行，请先启动服务器:")
        print("   python run.py dev")
        print("   或使用: python -m src.server")
        return
    
    print("✅ 服务器连接正常，开始演示...\n")
    
    try:
        # 基础工具演示
        demonstrate_basic_tools()
        
        # 文本处理工具演示
        demonstrate_text_tools()
        
        # 高级工具演示
        demonstrate_advanced_tools()
        
        # 批量操作演示
        demonstrate_batch_operations()
        
        # 资源访问演示
        demonstrate_resources()
        
        # 错误处理演示
        demonstrate_error_handling()
        
        # 异步操作演示
        print("\n🔄 运行异步操作演示...")
        asyncio.run(demonstrate_async_operations())
        
        # 学习路径演示
        demonstrate_learning_path()
        
    except KeyboardInterrupt:
        print("\n👋 用户中断演示")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
    
    print("\n🎉 演示完成！")
    print("\n💡 提示:")
    print("   - 可以修改这些示例代码来测试不同的功能")
    print("   - 查看服务器日志了解详细的请求处理过程")
    print("   - 参考README.md获取更多使用信息")


if __name__ == "__main__":
    main()