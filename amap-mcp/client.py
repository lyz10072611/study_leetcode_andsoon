#!/usr/bin/env python3
"""
高德API MCP客户端
用于连接和测试高德地图MCP服务器
"""

import asyncio
import json
import sys
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("amap-mcp-client")


class AmapMCPClient:
    """高德地图MCP客户端"""
    
    def __init__(self, server_script: Optional[str] = None):
        """
        初始化客户端
        
        Args:
            server_script: 服务器脚本路径，默认为当前目录下的server.py
        """
        if server_script is None:
            # 默认使用当前目录下的server.py
            current_dir = Path(__file__).parent
            server_script = str(current_dir / "server.py")
        
        self.server_script = server_script
        self.server_params = StdioServerParameters(
            command="python",
            args=[server_script],
            env=None
        )
        self.stdio_transport = None
        self.session: Optional[ClientSession] = None
        self._connected = False
    
    async def __aenter__(self):
        """异步上下文管理器进入"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.disconnect()
    
    async def connect(self):
        """连接到MCP服务器"""
        if self._connected:
            return True
        
        try:
            # 创建stdio客户端连接（使用async with）
            self.stdio_transport = stdio_client(self.server_params)
            # stdio_client返回的是async context manager，需要进入上下文
            read_stream, write_stream = await self.stdio_transport.__aenter__()
            
            # 创建客户端会话（也使用async context manager）
            self.session = ClientSession(read_stream, write_stream)
            await self.session.__aenter__()
            await self.session.initialize()
            
            self._connected = True
            logger.info("已连接到MCP服务器")
            return True
        except Exception as e:
            logger.error(f"连接服务器失败: {e}", exc_info=True)
            self._cleanup()
            return False
    
    async def disconnect(self):
        """断开连接"""
        if not self._connected:
            return
        
        try:
            # 先关闭session
            if self.session:
                try:
                    # 尝试正常关闭session
                    await self.session.__aexit__(None, None, None)
                except Exception as e:
                    logger.debug(f"关闭session时出错: {e}")
                self.session = None
            
            # 然后关闭stdio传输
            if self.stdio_transport:
                try:
                    # 尝试正常关闭stdio传输
                    await self.stdio_transport.__aexit__(None, None, None)
                except (RuntimeError, Exception) as e:
                    # 忽略"不同任务退出"的错误，这是MCP库的已知问题
                    if "different task" not in str(e).lower():
                        logger.debug(f"关闭stdio传输时出错: {e}")
                self.stdio_transport = None
        except Exception as e:
            logger.debug(f"断开连接时出错: {e}")
        finally:
            self._cleanup()
            logger.info("已断开连接")
    
    def _cleanup(self):
        """清理资源（同步部分）"""
        self._connected = False
        self.session = None
        self.stdio_transport = None
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        列出所有可用工具
        
        Returns:
            工具列表
        """
        if not self.session:
            raise RuntimeError("未连接到服务器，请先调用connect()")
        
        try:
            result = await self.session.list_tools()
            return [tool.model_dump() for tool in result.tools]
        except Exception as e:
            logger.error(f"获取工具列表失败: {e}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用工具
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        if not self.session:
            raise RuntimeError("未连接到服务器，请先调用connect()")
        
        try:
            result = await self.session.call_tool(tool_name, arguments)
            
            # 提取文本内容
            content_texts = []
            for content in result.content:
                if isinstance(content, str):
                    content_texts.append(content)
                elif hasattr(content, 'text'):
                    text_attr = getattr(content, 'text', None)
                    if isinstance(text_attr, str):
                        content_texts.append(text_attr)
            
            return {
                "success": not result.isError,
                "content": "\n".join(content_texts),
                "isError": result.isError
            }
        except Exception as e:
            logger.error(f"调用工具失败: {e}")
            return {
                "success": False,
                "content": f"错误: {str(e)}",
                "isError": True
            }
    
    async def geocode(self, address: str, city: Optional[str] = None) -> Dict[str, Any]:
        """
        地理编码：地址转坐标
        
        Args:
            address: 地址
            city: 城市（可选）
            
        Returns:
            地理编码结果
        """
        arguments = {"address": address}
        if city:
            arguments["city"] = city
        return await self.call_tool("geocode", arguments)
    
    async def regeo_code(self, location: str, radius: int = 1000) -> Dict[str, Any]:
        """
        逆地理编码：坐标转地址
        
        Args:
            location: 坐标（格式：经度,纬度）
            radius: 搜索半径（米）
            
        Returns:
            逆地理编码结果
        """
        return await self.call_tool("regeo_code", {
            "location": location,
            "radius": radius
        })
    
    async def driving_route(self, origin: str, destination: str, strategy: int = 0) -> Dict[str, Any]:
        """
        驾车路径规划
        
        Args:
            origin: 起点坐标（格式：经度,纬度）
            destination: 终点坐标（格式：经度,纬度）
            strategy: 策略（0-速度优先，1-费用优先，2-距离优先，3-不走高速，4-躲避拥堵，5-多策略）
            
        Returns:
            路径规划结果
        """
        return await self.call_tool("driving_route", {
            "origin": origin,
            "destination": destination,
            "strategy": strategy
        })
    
    async def walking_route(self, origin: str, destination: str) -> Dict[str, Any]:
        """
        步行路径规划
        
        Args:
            origin: 起点坐标（格式：经度,纬度）
            destination: 终点坐标（格式：经度,纬度）
            
        Returns:
            路径规划结果
        """
        return await self.call_tool("walking_route", {
            "origin": origin,
            "destination": destination
        })
    
    async def transit_route(self, origin: str, destination: str, city: str, 
                           cityd: Optional[str] = None) -> Dict[str, Any]:
        """
        公交路径规划
        
        Args:
            origin: 起点坐标（格式：经度,纬度）
            destination: 终点坐标（格式：经度,纬度）
            city: 城市代码/城市名称
            cityd: 目的地城市代码（可选）
            
        Returns:
            路径规划结果
        """
        arguments = {
            "origin": origin,
            "destination": destination,
            "city": city
        }
        if cityd:
            arguments["cityd"] = cityd
        return await self.call_tool("transit_route", arguments)
    
    async def weather(self, city: str, extensions: str = "base") -> Dict[str, Any]:
        """
        天气查询
        
        Args:
            city: 城市编码或名称
            extensions: 气象类型（base-实况天气，all-预报天气）
            
        Returns:
            天气信息
        """
        return await self.call_tool("weather", {
            "city": city,
            "extensions": extensions
        })
    
    async def ip_location(self, ip: Optional[str] = None) -> Dict[str, Any]:
        """
        IP定位
        
        Args:
            ip: IP地址（可选，为空时使用请求IP）
            
        Returns:
            IP定位结果
        """
        arguments = {}
        if ip:
            arguments["ip"] = ip
        return await self.call_tool("ip_location", arguments)
    
    async def district_search(self, keywords: str, subdistrict: int = 1, 
                              page: int = 1, offset: int = 20) -> Dict[str, Any]:
        """
        行政区域查询
        
        Args:
            keywords: 查询关键字
            subdistrict: 子级行政区（0-不返回，1-返回下一级，2-返回下两级）
            page: 页数
            offset: 每页记录数
            
        Returns:
            行政区划信息
        """
        return await self.call_tool("district_search", {
            "keywords": keywords,
            "subdistrict": subdistrict,
            "page": page,
            "offset": offset
        })
    
    async def around_place(self, location: str, keywords: Optional[str] = None,
                          types: Optional[str] = None, radius: int = 3000,
                          page: int = 1, offset: int = 20) -> Dict[str, Any]:
        """
        周边搜索
        
        Args:
            location: 中心点坐标（格式：经度,纬度）
            keywords: 关键词（可选）
            types: POI类型（可选）
            radius: 搜索半径（米）
            page: 页数
            offset: 每页记录数
            
        Returns:
            周边搜索结果
        """
        arguments = {
            "location": location,
            "radius": radius,
            "page": page,
            "offset": offset
        }
        if keywords:
            arguments["keywords"] = keywords
        if types:
            arguments["types"] = types
        return await self.call_tool("around_place", arguments)
    
    async def geofence_status(self, locations: str, diu: Optional[str] = None) -> Dict[str, Any]:
        """
        地理围栏状态查询
        
        Args:
            locations: 经纬度坐标，多个用'|'分隔
            diu: 设备唯一标识（可选）
            
        Returns:
            地理围栏状态
        """
        arguments = {"locations": locations}
        if diu:
            arguments["diu"] = diu
        return await self.call_tool("geofence_status", arguments)
    
    async def static_map(self, location: str, zoom: int = 10, size: str = "400 * 300",
                        markers: Optional[str] = None, paths: Optional[str] = None,
                        labels: Optional[str] = None) -> Dict[str, Any]:
        """
        静态地图
        
        Args:
            location: 中心点坐标（格式：经度,纬度）
            zoom: 缩放级别（1-17）
            size: 图片尺寸（格式：宽*高）
            markers: 标记点（可选）
            paths: 路径（可选）
            labels: 标签（可选）
            
        Returns:
            静态地图URL
        """
        arguments = {
            "location": location,
            "zoom": zoom,
            "size": size
        }
        if markers:
            arguments["markers"] = markers
        if paths:
            arguments["paths"] = paths
        if labels:
            arguments["labels"] = labels
        return await self.call_tool("static_map", arguments)


async def demo():
    """演示客户端使用"""
    # 设置Windows控制台编码为UTF-8
    import sys
    if sys.platform == "win32":
        try:
            # Python 3.7+支持reconfigure
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')  # type: ignore
            if hasattr(sys.stderr, 'reconfigure'):
                sys.stderr.reconfigure(encoding='utf-8')  # type: ignore
        except:
            pass
    
    print("高德地图MCP客户端演示")
    print("=" * 60)
    
    client = AmapMCPClient()
    
    try:
        # 连接服务器
        print("\n1. 连接服务器...")
        if not await client.connect():
            print("连接失败，请确保服务器正在运行")
            return
        
        # 列出所有工具
        print("\n2. 获取可用工具列表...")
        tools = await client.list_tools()
        print(f"找到 {len(tools)} 个工具:")
        for i, tool in enumerate(tools[:5], 1):  # 只显示前5个
            print(f"   {i}. {tool.get('name', 'Unknown')}: {tool.get('description', '')[:50]}...")
        
        # 测试地理编码
        print("\n3. 测试地理编码...")
        result = await client.geocode("北京市朝阳区阜通东大街6号")
        if result.get("success"):
            print("地理编码成功:")
            print(result.get("content", ""))
        else:
            print("地理编码失败:")
            print(result.get("content", ""))
        
        # 测试逆地理编码
        print("\n4. 测试逆地理编码...")
        result = await client.regeo_code("116.397428,39.90923")
        if result.get("success"):
            print("逆地理编码成功:")
            print(result.get("content", ""))
        else:
            print("逆地理编码失败:")
            print(result.get("content", ""))
        
        # 测试天气查询
        print("\n5. 测试天气查询...")
        result = await client.weather("北京")
        if result.get("success"):
            print("天气查询成功:")
            print(result.get("content", ""))
        else:
            print("天气查询失败:")
            print(result.get("content", ""))
        
        # 测试路径规划
        print("\n6. 测试驾车路径规划...")
        result = await client.driving_route(
            origin="116.397428,39.90923",
            destination="116.397428,39.91923"
        )
        if result.get("success"):
            print("路径规划成功:")
            print(result.get("content", "")[:200] + "...")  # 只显示前200字符
        else:
            print("路径规划失败:")
            print(result.get("content", ""))
    
    finally:
        # 断开连接
        print("\n7. 断开连接...")
        await client.disconnect()
        print("演示完成！")


async def interactive_mode():
    """交互式模式"""
    # 设置Windows控制台编码为UTF-8
    import sys
    if sys.platform == "win32":
        try:
            # Python 3.7+支持reconfigure
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')  # type: ignore
            if hasattr(sys.stderr, 'reconfigure'):
                sys.stderr.reconfigure(encoding='utf-8')  # type: ignore
        except:
            pass
    
    print("高德地图MCP客户端 - 交互式模式")
    print("=" * 60)
    print("输入 'help' 查看帮助，输入 'exit' 退出")
    print()
    
    # 使用客户端连接
    client = AmapMCPClient()
    try:
        # 连接服务器
        if not await client.connect():
            print("连接失败，请确保服务器正在运行")
            return
        
        while True:
            try:
                command = input("\n> ").strip()
                
                if not command:
                    continue
                
                if command == "exit":
                    break
                
                if command == "help":
                    print("\n可用命令:")
                    print("  help              - 显示帮助")
                    print("  list              - 列出所有工具")
                    print("  geocode <地址>    - 地理编码")
                    print("  regeo <坐标>      - 逆地理编码（格式：经度,纬度）")
                    print("  weather <城市>    - 查询天气")
                    print("  route <起点> <终点> - 驾车路径规划（格式：经度,纬度）")
                    print("  exit              - 退出")
                    continue
                
                if command == "list":
                    tools = await client.list_tools()
                    print(f"\n找到 {len(tools)} 个工具:")
                    for i, tool in enumerate(tools, 1):
                        print(f"   {i}. {tool.get('name', 'Unknown')}: {tool.get('description', '')}")
                    continue
                
                parts = command.split(maxsplit=1)
                if len(parts) < 2:
                    print("参数不足，输入 'help' 查看帮助")
                    continue
                
                cmd = parts[0]
                args = parts[1]
                
                if cmd == "geocode":
                    result = await client.geocode(args)
                    print("\n" + result.get("content", ""))
                
                elif cmd == "regeo":
                    result = await client.regeo_code(args)
                    print("\n" + result.get("content", ""))
                
                elif cmd == "weather":
                    result = await client.weather(args)
                    print("\n" + result.get("content", ""))
                
                elif cmd == "route":
                    route_parts = args.split(maxsplit=1)
                    if len(route_parts) < 2:
                        print("需要起点和终点坐标")
                        continue
                    result = await client.driving_route(route_parts[0], route_parts[1])
                    print("\n" + result.get("content", ""))
                
                else:
                    print(f"未知命令: {cmd}，输入 'help' 查看帮助")
            
            except KeyboardInterrupt:
                print("\n\n退出交互式模式")
                break
            except Exception as e:
                print(f"错误: {e}")
    
    finally:
        # 断开连接
        await client.disconnect()


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="高德地图MCP客户端")
    parser.add_argument(
        "--mode",
        choices=["demo", "interactive"],
        default="interactive",
        help="运行模式：demo（演示）或 interactive（交互式）"
    )
    
    args = parser.parse_args()
    
    if args.mode == "demo":
        await demo()
    elif args.mode == "interactive":
        await interactive_mode()


if __name__ == "__main__":
    # 设置Windows控制台编码为UTF-8
    if sys.platform == "win32":
        try:
            # Python 3.7+支持reconfigure
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')  # type: ignore
            if hasattr(sys.stderr, 'reconfigure'):
                sys.stderr.reconfigure(encoding='utf-8')  # type: ignore
        except:
            pass
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        logger.error(f"程序运行错误: {e}", exc_info=True)
        sys.exit(1)

