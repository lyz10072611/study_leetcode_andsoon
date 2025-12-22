#!/usr/bin/env python3
"""
基于百炼平台Qwen2.5模型和LangChain的Agent
集成高德地图MCP客户端
"""

import asyncio
import os
import sys
from typing import List, Optional, Dict, Any
from pathlib import Path

# LangChain核心组件
from langchain_core.tools import Tool, StructuredTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.language_models import BaseChatModel

# 百炼平台（通义千问）集成
try:
    from langchain_tongyi import ChatTongyi
except ImportError:
    # 如果langchain_tongyi不可用，尝试使用dashscope
    try:
        from langchain_community.chat_models import ChatTongyi
    except ImportError:
        ChatTongyi = None
        print("警告: 未安装langchain_tongyi或dashscope，请使用: pip install langchain-tongyi")

# LangChain Agent
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.agents.format_scratchpad import format_to_openai_tool_messages
from langchain.agents.output_parsers import OpenAIToolsAgentOutputParser

# MCP客户端
from client import AmapMCPClient

# 配置日志
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("amap-agent")

# 设置Windows控制台编码
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')  # type: ignore
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')  # type: ignore
    except:
        pass


def _run_async(coro):
    """运行异步函数的辅助函数"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果事件循环正在运行，需要创建新任务
            import nest_asyncio
            try:
                nest_asyncio.apply()
            except:
                pass
            return asyncio.run(coro)
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        # 没有事件循环，创建新的
        return asyncio.run(coro)


class MCPToolWrapper:
    """MCP客户端工具包装器，将MCP客户端方法转换为LangChain工具"""
    
    def __init__(self, mcp_client: AmapMCPClient):
        self.client = mcp_client
        self._ensure_connected()
    
    def _ensure_connected(self):
        """确保MCP客户端已连接"""
        if not self.client._connected:
            try:
                _run_async(self.client.connect())
            except Exception as e:
                logger.warning(f"MCP客户端连接失败: {e}")
    
    def create_tools(self) -> List[Tool]:
        """创建所有MCP工具"""
        tools = []
        
        # 地理编码工具
        tools.append(StructuredTool.from_function(
            func=self._geocode,
            name="geocode",
            description="地理编码：将地址转换为经纬度坐标。输入：地址字符串（可选城市参数）。返回：坐标信息。示例：geocode('北京市朝阳区阜通东大街6号')"
        ))
        
        # 逆地理编码工具
        tools.append(StructuredTool.from_function(
            func=self._regeo_code,
            name="regeo_code",
            description="逆地理编码：将经纬度坐标转换为结构化地址。输入：坐标（格式：经度,纬度）。返回：地址信息。"
        ))
        
        # 驾车路径规划工具
        tools.append(StructuredTool.from_function(
            func=self._driving_route,
            name="driving_route",
            description="驾车路径规划：计算两点之间的驾车路线。输入：起点坐标和终点坐标（格式：经度,纬度）。返回：路径规划结果。"
        ))
        
        # 步行路径规划工具
        tools.append(StructuredTool.from_function(
            func=self._walking_route,
            name="walking_route",
            description="步行路径规划：计算两点之间的步行路线。输入：起点坐标和终点坐标（格式：经度,纬度）。返回：路径规划结果。"
        ))
        
        # 公交路径规划工具
        tools.append(StructuredTool.from_function(
            func=self._transit_route,
            name="transit_route",
            description="公交路径规划：计算两点之间的公共交通路线。输入：起点坐标、终点坐标和城市名称。返回：公交路线规划结果。"
        ))
        
        # 天气查询工具
        tools.append(StructuredTool.from_function(
            func=self._weather,
            name="weather",
            description="天气查询：获取指定城市的天气信息。输入：城市名称或编码。返回：天气信息。"
        ))
        
        # IP定位工具
        tools.append(StructuredTool.from_function(
            func=self._ip_location,
            name="ip_location",
            description="IP定位：根据IP地址获取地理位置信息。输入：IP地址（可选）。返回：地理位置信息。"
        ))
        
        # 行政区域查询工具
        tools.append(StructuredTool.from_function(
            func=self._district_search,
            name="district_search",
            description="行政区域查询：查询行政区划信息。输入：查询关键字（如：北京、朝阳区）。返回：行政区划信息。"
        ))
        
        # 周边搜索工具
        tools.append(StructuredTool.from_function(
            func=self._around_place,
            name="around_place",
            description="周边搜索：搜索指定位置周边的POI点（如餐馆、酒店等）。输入：中心点坐标和关键词。返回：周边地点列表。"
        ))
        
        return tools
    
    def _geocode(self, address: str, city: Optional[str] = None) -> str:
        """地理编码工具"""
        try:
            result = _run_async(self.client.geocode(address, city))
            if result.get("success"):
                return result.get("content", "未找到结果")
            else:
                return f"错误: {result.get('content', '未知错误')}"
        except Exception as e:
            return f"执行失败: {str(e)}"
    
    def _regeo_code(self, location: str, radius: int = 1000) -> str:
        """逆地理编码工具"""
        try:
            result = _run_async(self.client.regeo_code(location, radius))
            if result.get("success"):
                return result.get("content", "未找到结果")
            else:
                return f"错误: {result.get('content', '未知错误')}"
        except Exception as e:
            return f"执行失败: {str(e)}"
    
    def _driving_route(self, origin: str, destination: str, strategy: int = 0) -> str:
        """驾车路径规划工具"""
        try:
            result = _run_async(self.client.driving_route(origin, destination, strategy))
            if result.get("success"):
                return result.get("content", "未找到路径")
            else:
                return f"错误: {result.get('content', '未知错误')}"
        except Exception as e:
            return f"执行失败: {str(e)}"
    
    def _walking_route(self, origin: str, destination: str) -> str:
        """步行路径规划工具"""
        try:
            result = _run_async(self.client.walking_route(origin, destination))
            if result.get("success"):
                return result.get("content", "未找到路径")
            else:
                return f"错误: {result.get('content', '未知错误')}"
        except Exception as e:
            return f"执行失败: {str(e)}"
    
    def _transit_route(self, origin: str, destination: str, city: str, cityd: Optional[str] = None) -> str:
        """公交路径规划工具"""
        try:
            result = _run_async(self.client.transit_route(origin, destination, city, cityd))
            if result.get("success"):
                return result.get("content", "未找到路径")
            else:
                return f"错误: {result.get('content', '未知错误')}"
        except Exception as e:
            return f"执行失败: {str(e)}"
    
    def _weather(self, city: str, extensions: str = "base") -> str:
        """天气查询工具"""
        try:
            result = _run_async(self.client.weather(city, extensions))
            if result.get("success"):
                return result.get("content", "未找到天气信息")
            else:
                return f"错误: {result.get('content', '未知错误')}"
        except Exception as e:
            return f"执行失败: {str(e)}"
    
    def _ip_location(self, ip: Optional[str] = None) -> str:
        """IP定位工具"""
        try:
            result = _run_async(self.client.ip_location(ip))
            if result.get("success"):
                return result.get("content", "未找到位置信息")
            else:
                return f"错误: {result.get('content', '未知错误')}"
        except Exception as e:
            return f"执行失败: {str(e)}"
    
    def _district_search(self, keywords: str, subdistrict: int = 1, page: int = 1, offset: int = 20) -> str:
        """行政区域查询工具"""
        try:
            result = _run_async(self.client.district_search(keywords, subdistrict, page, offset))
            if result.get("success"):
                return result.get("content", "未找到行政区划信息")
            else:
                return f"错误: {result.get('content', '未知错误')}"
        except Exception as e:
            return f"执行失败: {str(e)}"
    
    def _around_place(self, location: str, keywords: Optional[str] = None, types: Optional[str] = None,
                     radius: int = 3000, page: int = 1, offset: int = 20) -> str:
        """周边搜索工具"""
        try:
            result = _run_async(self.client.around_place(location, keywords, types, radius, page, offset))
            if result.get("success"):
                return result.get("content", "未找到周边地点")
            else:
                return f"错误: {result.get('content', '未知错误')}"
        except Exception as e:
            return f"执行失败: {str(e)}"


class AmapAgent:
    """高德地图Agent，集成MCP客户端和LangChain"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "qwen-turbo",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        初始化Agent
        
        Args:
            api_key: 百炼平台API密钥（DASHSCOPE_API_KEY）
            model_name: 模型名称，默认qwen-turbo
            temperature: 温度参数
            max_tokens: 最大token数
        """
        # 获取API密钥
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("请设置DASHSCOPE_API_KEY环境变量或传入api_key参数")
        
        # 初始化MCP客户端
        self.mcp_client = AmapMCPClient()
        self._mcp_connected = False
        
        # 初始化LLM（百炼平台Qwen2.5）
        if ChatTongyi is None:
            raise ImportError("请安装langchain-tongyi: pip install langchain-tongyi")
        
        self.llm = ChatTongyi(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            dashscope_api_key=self.api_key
        )
        
        # 工具和Agent将在initialize()中创建（需要先连接MCP）
        self.tool_wrapper = None
        self.tools = []
        self.agent = None
        
        logger.info(f"Agent初始化完成，模型: {model_name}")
    
    def _create_agent(self) -> AgentExecutor:
        """创建LangChain Agent"""
        # 系统提示词
        system_prompt = """你是一个智能地图助手，可以帮助用户进行以下操作：
1. 地址查询和坐标转换（地理编码/逆地理编码）
2. 路径规划（驾车、步行、公交）
3. 天气查询
4. 周边地点搜索
5. 行政区划查询
6. IP定位

请根据用户的问题，选择合适的工具来帮助用户。如果用户提供的是地址，可以使用地理编码工具转换为坐标；如果需要路径规划，可以使用路径规划工具；如果需要查询天气，可以使用天气查询工具。

回答要清晰、准确，并提供有用的信息。"""
        
        # 创建提示词模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # 创建Agent
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # 创建Agent执行器
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10
        )
        
        return agent_executor
    
    async def initialize(self):
        """初始化MCP客户端连接"""
        await self.mcp_client.connect()
        self._mcp_connected = True
        
        # 创建工具
        self.tool_wrapper = MCPToolWrapper(self.mcp_client)
        self.tools = self.tool_wrapper.create_tools()
        
        # 创建Agent
        self.agent = self._create_agent()
        
        logger.info(f"MCP客户端连接成功，工具数量: {len(self.tools)}")
    
    async def cleanup(self):
        """清理资源"""
        await self.mcp_client.disconnect()
        logger.info("MCP客户端已断开")
    
    async def run(self, query: str) -> str:
        """
        运行Agent处理查询
        
        Args:
            query: 用户查询
            
        Returns:
            Agent的回复
        """
        if not self.agent:
            return "Agent未初始化，请先调用initialize()方法"
        
        try:
            # 运行Agent（在事件循环中运行同步代码）
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.agent.invoke,
                {"input": query}
            )
            
            return result.get("output", "抱歉，我无法处理您的请求。")
        
        except Exception as e:
            logger.error(f"Agent执行失败: {e}", exc_info=True)
            return f"处理请求时发生错误: {str(e)}"
    
    def run_sync(self, query: str) -> str:
        """
        同步运行Agent处理查询
        
        Args:
            query: 用户查询
            
        Returns:
            Agent的回复
        """
        try:
            result = self.agent.invoke({"input": query})
            return result.get("output", "抱歉，我无法处理您的请求。")
        except Exception as e:
            logger.error(f"Agent执行失败: {e}", exc_info=True)
            return f"处理请求时发生错误: {str(e)}"


async def main():
    """主函数：交互式Agent"""
    print("=" * 60)
    print("高德地图智能助手 (基于百炼平台Qwen2.5 + LangChain)")
    print("=" * 60)
    print()
    
    # 检查API密钥
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("错误: 未设置DASHSCOPE_API_KEY环境变量")
        print("请设置环境变量: export DASHSCOPE_API_KEY='你的百炼平台API密钥'")
        return
    
    # 创建Agent
    try:
        agent = AmapAgent(api_key=api_key, model_name="qwen-turbo")
        await agent.initialize()
    except Exception as e:
        print(f"初始化Agent失败: {e}")
        return
    
    print("Agent已就绪，可以开始提问了！")
    print("输入 'exit' 或 'quit' 退出")
    print("=" * 60)
    print()
    
    try:
        while True:
            try:
                query = input("\n你: ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ["exit", "quit", "退出"]:
                    break
                
                print("\n助手: ", end="", flush=True)
                response = await agent.run(query)
                print(response)
                
            except KeyboardInterrupt:
                print("\n\n退出程序...")
                break
            except Exception as e:
                print(f"\n错误: {e}")
    
    finally:
        await agent.cleanup()
        print("\n再见！")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        logger.error(f"程序运行错误: {e}", exc_info=True)
        sys.exit(1)

