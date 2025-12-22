#!/usr/bin/env python3
"""
高德API的MCP服务器实现
使用原始MCP协议封装高德地图服务
"""

import asyncio
import os
import json
import logging
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

import aiohttp
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    ListToolsResult,
    CallToolResult,
    ContentBlock
)
from pydantic import BaseModel, Field
from urllib.parse import quote

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("amap-mcp")

# 环境变量配置
AMAP_API_KEY = "51911a6d335665ca01092dc140310a00"
AMAP_BASE_URL = "https://restapi.amap.com/v3"

if not AMAP_API_KEY:
    logger.warning("AMAP_API_KEY 未设置，请通过环境变量配置")


# 数据模型
class Coordinate(BaseModel):
    """坐标点"""
    longitude: float = Field(description="经度")
    latitude: float = Field(description="纬度")


class GeoCodeRequest(BaseModel):
    """地理编码请求"""
    address: str = Field(description="地址描述")
    city: Optional[str] = Field(None, description="地址所在城市")


class RegeoCodeRequest(BaseModel):
    """逆地理编码请求"""
    location: str = Field(description="经纬度坐标，格式：经度,纬度")
    radius: Optional[int] = Field(1000, description="搜索半径，单位：米")


class DrivingRouteRequest(BaseModel):
    """驾车路径规划请求"""
    origin: str = Field(description="起点坐标，格式：经度,纬度")
    destination: str = Field(description="终点坐标，格式：经度,纬度")
    strategy: Optional[int] = Field(0,
                                    description="策略：0-速度优先，1-费用优先，2-距离优先，3-不走高速，4-躲避拥堵，5-多策略")


class WalkingRouteRequest(BaseModel):
    """步行路径规划请求"""
    origin: str = Field(description="起点坐标，格式：经度,纬度")
    destination: str = Field(description="终点坐标，格式：经度,纬度")


class TransitRouteRequest(BaseModel):
    """公交路径规划请求"""
    origin: str = Field(description="起点坐标，格式：经度,纬度")
    destination: str = Field(description="终点坐标，格式：经度,纬度")
    city: str = Field(description="城市代码/城市名称")
    cityd: Optional[str] = Field(None, description="目的地城市代码")


class IPLocationRequest(BaseModel):
    """IP定位请求"""
    ip: Optional[str] = Field(None, description="IP地址，为空时使用请求IP")
    sig: Optional[str] = Field(None, description="数字签名")


class WeatherRequest(BaseModel):
    """天气查询请求"""
    city: str = Field(description="城市编码或名称")
    extensions: Optional[str] = Field("base", description="气象类型：base-实况天气，all-预报天气")


class DistrictSearchRequest(BaseModel):
    """行政区域查询请求"""
    keywords: str = Field(description="查询关键字")
    subdistrict: Optional[int] = Field(1, description="子级行政区：0-不返回，1-返回下一级，2-返回下两级")
    page: Optional[int] = Field(1, description="页数")
    offset: Optional[int] = Field(20, description="每页记录数")


class AroundPlaceRequest(BaseModel):
    """周边搜索请求"""
    location: str = Field(description="中心点坐标，格式：经度,纬度")
    keywords: Optional[str] = Field(None, description="关键词")
    types: Optional[str] = Field(None, description="POI类型")
    radius: Optional[int] = Field(3000, description="搜索半径，单位：米")
    page: Optional[int] = Field(1, description="页数")
    offset: Optional[int] = Field(20, description="每页记录数")


class GeoFenceRequest(BaseModel):
    """地理围栏查询请求"""
    locations: str = Field(description="经纬度坐标，多个用'|'分隔")
    diu: Optional[str] = Field(None, description="设备唯一标识")


class StaticMapRequest(BaseModel):
    """静态地图请求"""
    location: str = Field(description="中心点坐标，格式：经度,纬度")
    zoom: Optional[int] = Field(10, description="缩放级别：1-17")
    size: Optional[str] = Field("400 * 300", description="图片尺寸，格式：宽*高")
    markers: Optional[str] = Field(None, description="标记点")
    paths: Optional[str] = Field(None, description="路径")
    labels: Optional[str] = Field(None, description="标签")


class AmapMCPClient:
    """高德MCP客户端"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or AMAP_API_KEY
        if not self.api_key:
            raise ValueError("AMAP_API_KEY 未配置")

        self.base_url = AMAP_BASE_URL
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _make_request(self, endpoint: str, params: Dict) -> Dict:
        """发起HTTP请求"""
        if not self.session:
            self.session = aiohttp.ClientSession()

        params["key"] = self.api_key
        params["output"] = "JSON"

        url = f"{self.base_url}/{endpoint}"

        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with self.session.get(url, params=params, timeout=timeout) as response:
                response.raise_for_status()
                data = await response.json()
                status = data.get("status", "0")

                if status == "1" or status == 1:
                    return data
                else:
                    error_msg = data.get("info", "未知错误")
                    logger.error(f"高德API错误: {error_msg}")
                    return {"status": "0", "info": error_msg, "data": None}
        except aiohttp.ClientError as e:
            logger.error(f"网络请求错误: {e}")
            return {"status": "0", "info": f"网络请求失败: {str(e)}", "data": None}
        except asyncio.TimeoutError:
            logger.error("请求超时")
            return {"status": "0", "info": "请求超时", "data": None}
        except Exception as e:
            logger.error(f"未知错误: {e}")
            return {"status": "0", "info": f"系统错误: {str(e)}", "data": None}

    async def geocode(self, address: str, city: Optional[str] = None) -> Dict:
        """地理编码：地址转坐标"""
        params = {"address": address}
        if city:
            params["city"] = city
        return await self._make_request("geocode/geo", params)

    async def regeo_code(self, location: str, radius: int = 1000) -> Dict:
        """逆地理编码：坐标转地址"""
        params = {
            "location": location,
            "radius": radius,
            "extensions": "all"
        }
        return await self._make_request("geocode/regeo", params)

    async def driving_route(self, origin: str, destination: str, strategy: int = 0) -> Dict:
        """驾车路径规划"""
        params = {
            "origin": origin,
            "destination": destination,
            "strategy": strategy
        }
        return await self._make_request("direction/driving", params)

    async def walking_route(self, origin: str, destination: str) -> Dict:
        """步行路径规划"""
        params = {
            "origin": origin,
            "destination": destination
        }
        return await self._make_request("direction/walking", params)

    async def transit_route(self, origin: str, destination: str, city: str, cityd: Optional[str] = None) -> Dict:
        """公交路径规划"""
        params = {
            "origin": origin,
            "destination": destination,
            "city": city
        }
        if cityd:
            params["cityd"] = cityd
        return await self._make_request("direction/transit/integrated", params)

    async def ip_location(self, ip: Optional[str] = None) -> Dict:
        """IP定位"""
        params = {}
        if ip:
            params["ip"] = ip
        return await self._make_request("ip", params)

    async def weather(self, city: str, extensions: str = "base") -> Dict:
        """天气查询"""
        params = {
            "city": city,
            "extensions": extensions
        }
        return await self._make_request("weather/weatherInfo", params)

    async def district_search(self, keywords: str, subdistrict: int = 1, page: int = 1, offset: int = 20) -> Dict:
        """行政区域查询"""
        params = {
            "keywords": keywords,
            "subdistrict": subdistrict,
            "page": page,
            "offset": offset
        }
        return await self._make_request("config/district", params)

    async def around_place(self, location: str, keywords: Optional[str] = None, types: Optional[str] = None,
                           radius: int = 3000, page: int = 1, offset: int = 20) -> Dict:
        """周边搜索"""
        params = {
            "location": location,
            "radius": radius,
            "page": page,
            "offset": offset
        }
        if keywords:
            params["keywords"] = keywords
        if types:
            params["types"] = types
        return await self._make_request("place/around", params)

    async def static_map(self, location: str, zoom: int = 10, size: str = "400 * 300",
                         markers: Optional[str] = None, paths: Optional[str] = None, labels: Optional[str] = None) -> Dict:
        """静态地图"""
        params = {
            "location": location,
            "zoom": zoom,
            "size": size
        }
        if markers:
            params["markers"] = markers
        if paths:
            params["paths"] = paths
        if labels:
            params["labels"] = labels
        return await self._make_request("staticmap", params)

    async def geofence_status(self, locations: str, diu: Optional[str] = None) -> Dict:
        """地理围栏状态查询"""
        params = {"locations": locations}
        if diu:
            params["diu"] = diu
        return await self._make_request("v4/geofence/status", params)


class AmapMCPServer:
    """高德MCP服务器"""

    def __init__(self):
        self.client = None
        self.tools = self._initialize_tools()

    def _initialize_tools(self) -> List[Tool]:
        """初始化所有工具"""
        return [
            Tool(
                name="geocode",
                description="地理编码：将地址转换为经纬度坐标",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "address": {
                            "type": "string",
                            "description": "地址描述，如：北京市朝阳区阜通东大街6号"
                        },
                        "city": {
                            "type": "string",
                            "description": "地址所在城市，可选"
                        }
                    },
                    "required": ["address"]
                }
            ),
            Tool(
                name="regeo_code",
                description="逆地理编码：将经纬度坐标转换为结构化地址",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "经纬度坐标，格式：经度,纬度，如：116.397428,39.90923"
                        },
                        "radius": {
                            "type": "integer",
                            "description": "搜索半径，单位：米，默认1000"
                        }
                    },
                    "required": ["location"]
                }
            ),
            Tool(
                name="driving_route",
                description="驾车路径规划：计算两点之间的驾车路线",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "origin": {
                            "type": "string",
                            "description": "起点坐标，格式：经度,纬度"
                        },
                        "destination": {
                            "type": "string",
                            "description": "终点坐标，格式：经度,纬度"
                        },
                        "strategy": {
                            "type": "integer",
                            "description": "策略：0-速度优先，1-费用优先，2-距离优先，3-不走高速，4-躲避拥堵，5-多策略，默认0"
                        }
                    },
                    "required": ["origin", "destination"]
                }
            ),
            Tool(
                name="walking_route",
                description="步行路径规划：计算两点之间的步行路线",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "origin": {
                            "type": "string",
                            "description": "起点坐标，格式：经度,纬度"
                        },
                        "destination": {
                            "type": "string",
                            "description": "终点坐标，格式：经度,纬度"
                        }
                    },
                    "required": ["origin", "destination"]
                }
            ),
            Tool(
                name="transit_route",
                description="公交路径规划：计算两点之间的公共交通路线",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "origin": {
                            "type": "string",
                            "description": "起点坐标，格式：经度,纬度"
                        },
                        "destination": {
                            "type": "string",
                            "description": "终点坐标，格式：经度,纬度"
                        },
                        "city": {
                            "type": "string",
                            "description": "城市代码/城市名称"
                        },
                        "cityd": {
                            "type": "string",
                            "description": "目的地城市代码，可选"
                        }
                    },
                    "required": ["origin", "destination", "city"]
                }
            ),
            Tool(
                name="weather",
                description="天气查询：获取指定城市的天气信息",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "城市编码或名称，如：110000 或 北京"
                        },
                        "extensions": {
                            "type": "string",
                            "description": "气象类型：base-实况天气，all-预报天气，默认base"
                        }
                    },
                    "required": ["city"]
                }
            ),
            Tool(
                name="ip_location",
                description="IP定位：根据IP地址获取地理位置信息",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ip": {
                            "type": "string",
                            "description": "IP地址，为空时使用请求IP"
                        }
                    }
                }
            ),
            Tool(
                name="district_search",
                description="行政区域查询：查询行政区划信息",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "keywords": {
                            "type": "string",
                            "description": "查询关键字，如：北京、朝阳区"
                        },
                        "subdistrict": {
                            "type": "integer",
                            "description": "子级行政区：0-不返回，1-返回下一级，2-返回下两级，默认1"
                        },
                        "page": {
                            "type": "integer",
                            "description": "页数，默认1"
                        },
                        "offset": {
                            "type": "integer",
                            "description": "每页记录数，默认20"
                        }
                    },
                    "required": ["keywords"]
                }
            ),
            Tool(
                name="around_place",
                description="周边搜索：搜索指定位置周边的POI点",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "中心点坐标，格式：经度,纬度"
                        },
                        "keywords": {
                            "type": "string",
                            "description": "关键词，如：餐馆、酒店"
                        },
                        "types": {
                            "type": "string",
                            "description": "POI类型代码，可选"
                        },
                        "radius": {
                            "type": "integer",
                            "description": "搜索半径，单位：米，默认3000"
                        },
                        "page": {
                            "type": "integer",
                            "description": "页数，默认1"
                        },
                        "offset": {
                            "type": "integer",
                            "description": "每页记录数，默认20"
                        }
                    },
                    "required": ["location"]
                }
            ),
            Tool(
                name="geofence_status",
                description="地理围栏状态查询：查询坐标点与地理围栏的关系",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "locations": {
                            "type": "string",
                            "description": "经纬度坐标，多个用'|'分隔，如：116.310003,39.991957|116.320003,39.981957"
                        },
                        "diu": {
                            "type": "string",
                            "description": "设备唯一标识，可选"
                        }
                    },
                    "required": ["locations"]
                }
            ),
            Tool(
                name="static_map",
                description="静态地图：生成指定位置的静态地图",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "中心点坐标，格式：经度,纬度"
                        },
                        "zoom": {
                            "type": "integer",
                            "description": "缩放级别：1-17，默认10"
                        },
                        "size": {
                            "type": "string",
                            "description": "图片尺寸，格式：宽*高，默认400 * 300"
                        },
                        "markers": {
                            "type": "string",
                            "description": "标记点，可选"
                        },
                        "paths": {
                            "type": "string",
                            "description": "路径，可选"
                        },
                        "labels": {
                            "type": "string",
                            "description": "标签，可选"
                        }
                    },
                    "required": ["location"]
                }
            )
        ]

    def format_response(self, data: Dict, tool_name: str) -> List[TextContent]:
        """格式化响应数据为MCP格式"""
        status = data.get("status", "0")

        if status == "0" or status == 0:
            error_info = data.get("info", "未知错误")
            return [TextContent(
                type="text",
                text=f"❌ 请求失败: {error_info}"
            )]

        # 根据不同工具格式化输出
        if tool_name == "geocode":
            geocodes = data.get("geocodes", [])
            if not geocodes:
                return [TextContent(type="text", text="未找到相关地址信息")]

            result = ["📍 地理编码结果："]
            for i, geocode in enumerate(geocodes[:5], 1):  # 只显示前5个结果
                formatted_address = geocode.get("formatted_address", "")
                province = geocode.get("province", "")
                city = geocode.get("city", "")
                district = geocode.get("district", "")
                location = geocode.get("location", "")
                result.append(f"{i}. {formatted_address}")
                result.append(f"   地区: {province} {city} {district}")
                result.append(f"   坐标: {location}")
                result.append("")

            return [TextContent(type="text", text="\n".join(result))]

        elif tool_name == "regeo_code":
            regeocode = data.get("regeocode", {})
            if not regeocode:
                return [TextContent(type="text", text="未找到坐标对应的地址信息")]

            formatted_address = regeocode.get("formatted_address", "")
            address_component = regeocode.get("addressComponent", {})

            province = address_component.get("province", "")
            city = address_component.get("city", "")
            district = address_component.get("district", "")
            township = address_component.get("township", "")

            result = [
                "🗺️ 逆地理编码结果：",
                f"格式化地址: {formatted_address}",
                f"行政区划: {province} {city} {district} {township}",
                ""
            ]

            # 添加POI点
            pois = regeocode.get("pois", [])
            if pois:
                result.append("附近POI点:")
                for i, poi in enumerate(pois[:5], 1):
                    name = poi.get("name", "")
                    address = poi.get("address", "")
                    distance = poi.get("distance", "")
                    result.append(f"{i}. {name} - {address} ({distance}米)")

            return [TextContent(type="text", text="\n".join(result))]

        elif tool_name in ["driving_route", "walking_route", "transit_route"]:
            route = data.get("route", {})
            if not route:
                return [TextContent(type="text", text="未找到路径规划结果")]

            paths = route.get("paths", [])
            if not paths:
                return [TextContent(type="text", text="未找到路径")]

            result = [f"🗺️ 路径规划结果 ({tool_name.replace('_', ' ')}):"]

            for i, path in enumerate(paths[:3], 1):  # 最多显示3条路径
                distance = int(path.get("distance", 0))
                duration = int(path.get("duration", 0))

                # 转换时间为可读格式
                hours = duration // 3600
                minutes = (duration % 3600) // 60

                result.append(f"\n路径 {i}:")
                result.append(f"  距离: {distance} 米 ({distance / 1000:.1f} 公里)")
                result.append(f"  预计时间: {hours}小时{minutes}分钟")

                # 显示步骤
                steps = path.get("steps", [])
                if steps:
                    result.append("  路线指引:")
                    for j, step in enumerate(steps[:5], 1):  # 只显示前5步
                        instruction = step.get("instruction", "").replace("<b>", "").replace("</b>", "")
                        result.append(f"    {j}. {instruction}")

            return [TextContent(type="text", text="\n".join(result))]

        elif tool_name == "weather":
            lives = data.get("lives", [])
            forecasts = data.get("forecasts", [])

            if lives:
                weather = lives[0]
                result = [
                    "🌤️ 实时天气:",
                    f"地区: {weather.get('province')} {weather.get('city')}",
                    f"天气: {weather.get('weather')}",
                    f"温度: {weather.get('temperature')}°C",
                    f"风向: {weather.get('winddirection')}风 {weather.get('windpower')}级",
                    f"湿度: {weather.get('humidity')}%",
                    f"发布时间: {weather.get('reporttime')}"
                ]
                return [TextContent(type="text", text="\n".join(result))]

            elif forecasts:
                forecast = forecasts[0]
                casts = forecast.get("casts", [])
                result = [
                    f"📅 天气预报 - {forecast.get('city')}:"
                ]

                for cast in casts[:3]:  # 显示3天预报
                    date = cast.get("date", "")
                    dayweather = cast.get("dayweather", "")
                    nightweather = cast.get("nightweather", "")
                    daytemp = cast.get("daytemp", "")
                    nighttemp = cast.get("nighttemp", "")
                    result.append(f"\n{date}:")
                    result.append(f"  白天: {dayweather} {daytemp}°C")
                    result.append(f"  夜间: {nightweather} {nighttemp}°C")

                return [TextContent(type="text", text="\n".join(result))]

            else:
                return [TextContent(type="text", text="未找到天气信息")]

        elif tool_name == "district_search":
            districts = data.get("districts", [])
            if not districts:
                return [TextContent(type="text", text="未找到行政区划信息")]

            result = ["🏙️ 行政区划查询结果："]

            def format_district(district, level=0):
                indent = "  " * level
                result = []
                result.append(f"{indent}📌 {district.get('name')} ({district.get('citycode', '')})")

                # 显示中心点
                center = district.get("center", "")
                if center:
                    result.append(f"{indent}  中心点: {center}")

                # 显示下级区域
                sub_districts = district.get("districts", [])
                for sub in sub_districts:
                    result.extend(format_district(sub, level + 1))

                return result

            for district in districts:
                result.extend(format_district(district))

            return [TextContent(type="text", text="\n".join(result))]

        elif tool_name == "around_place":
            pois = data.get("pois", [])
            if not pois:
                return [TextContent(type="text", text="未找到周边地点")]

            result = ["📍 周边搜索结果："]
            for i, poi in enumerate(pois[:10], 1):  # 显示前10个结果
                name = poi.get("name", "")
                address = poi.get("address", "")
                distance = poi.get("distance", "")
                typecode = poi.get("typecode", "")

                result.append(f"{i}. {name}")
                if address:
                    result.append(f"   地址: {address}")
                if distance:
                    result.append(f"   距离: {distance}米")
                if typecode:
                    result.append(f"   类型: {typecode}")
                result.append("")

            return [TextContent(type="text", text="\n".join(result))]

        elif tool_name == "ip_location":
            ip_info = data
            if ip_info.get("status") == "1":
                result = [
                    "🌐 IP定位结果：",
                    f"IP地址: {ip_info.get('ip', '')}",
                    f"国家: {ip_info.get('country', '')}",
                    f"省份: {ip_info.get('province', '')}",
                    f"城市: {ip_info.get('city', '')}",
                    f"区县: {ip_info.get('district', '')}",
                    f"运营商: {ip_info.get('isp', '')}",
                    f"地理位置: {ip_info.get('location', '')}"
                ]
                return [TextContent(type="text", text="\n".join(result))]
            else:
                return [TextContent(type="text", text="IP定位失败")]

        elif tool_name == "geofence_status":
            fence_info = data
            if fence_info.get("status") == "1":
                data_list = fence_info.get("data", [])
                result = ["📍 地理围栏状态："]

                for i, item in enumerate(data_list, 1):
                    fence_name = item.get("fence_name", "")
                    triggered = item.get("triggered", False)
                    point = item.get("point", "")

                    result.append(f"\n围栏 {i}: {fence_name}")
                    result.append(f"   状态: {'在围栏内' if triggered else '在围栏外'}")
                    result.append(f"   坐标: {point}")

                return [TextContent(type="text", text="\n".join(result))]
            else:
                return [TextContent(type="text", text="地理围栏查询失败")]

        elif tool_name == "static_map":
            # 静态地图返回的是图片URL
            # 从环境变量获取API密钥
            api_key = AMAP_API_KEY or ""
            image_url = f"https://restapi.amap.com/v3/staticmap?location={data.get('location', '')}&zoom={data.get('zoom', 10)}&size={data.get('size', '400 * 300')}&key={api_key}"

            # 添加标记点
            if data.get("markers"):
                image_url += f"&markers={data.get('markers')}"

            return [
                TextContent(type="text", text="🖼️ 静态地图生成成功"),
                TextContent(type="text", text=f"图片URL: {image_url}")
            ]

        # 默认返回JSON格式
        return [TextContent(
            type="text",
            text=f"✅ 操作成功:\n{json.dumps(data, ensure_ascii=False, indent=2)}"
        )]

    async def handle_tool_call(self, tool_name: str, arguments: Dict) -> CallToolResult:
        """处理工具调用"""
        try:
            if not self.client:
                self.client = AmapMCPClient()

            async with self.client as client:
                if tool_name == "geocode":
                    result = await client.geocode(
                        address=arguments["address"],
                        city=arguments.get("city")
                    )

                elif tool_name == "regeo_code":
                    result = await client.regeo_code(
                        location=arguments["location"],
                        radius=arguments.get("radius", 1000)
                    )

                elif tool_name == "driving_route":
                    result = await client.driving_route(
                        origin=arguments["origin"],
                        destination=arguments["destination"],
                        strategy=arguments.get("strategy", 0)
                    )

                elif tool_name == "walking_route":
                    result = await client.walking_route(
                        origin=arguments["origin"],
                        destination=arguments["destination"]
                    )

                elif tool_name == "transit_route":
                    result = await client.transit_route(
                        origin=arguments["origin"],
                        destination=arguments["destination"],
                        city=arguments["city"],
                        cityd=arguments.get("cityd")
                    )

                elif tool_name == "weather":
                    result = await client.weather(
                        city=arguments["city"],
                        extensions=arguments.get("extensions", "base")
                    )

                elif tool_name == "ip_location":
                    result = await client.ip_location(
                        ip=arguments.get("ip")
                    )

                elif tool_name == "district_search":
                    result = await client.district_search(
                        keywords=arguments["keywords"],
                        subdistrict=arguments.get("subdistrict", 1),
                        page=arguments.get("page", 1),
                        offset=arguments.get("offset", 20)
                    )

                elif tool_name == "around_place":
                    result = await client.around_place(
                        location=arguments["location"],
                        keywords=arguments.get("keywords"),
                        types=arguments.get("types"),
                        radius=arguments.get("radius", 3000),
                        page=arguments.get("page", 1),
                        offset=arguments.get("offset", 20)
                    )

                elif tool_name == "geofence_status":
                    result = await client.geofence_status(
                        locations=arguments["locations"],
                        diu=arguments.get("diu")
                    )

                elif tool_name == "static_map":
                    result = await client.static_map(
                        location=arguments["location"],
                        zoom=arguments.get("zoom", 10),
                        size=arguments.get("size", "400 * 300"),
                        markers=arguments.get("markers"),
                        paths=arguments.get("paths"),
                        labels=arguments.get("labels")
                    )

                else:
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"未知工具: {tool_name}"
                        )],
                        isError=True
                    )

                # 格式化响应
                formatted_content = self.format_response(result, tool_name)

                # TextContent已经是ContentBlock的子类型，可以直接使用
                return CallToolResult(
                    content=formatted_content,  # type: ignore
                    isError=False
                )

        except Exception as e:
            logger.error(f"工具调用失败: {e}", exc_info=True)
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"工具调用失败: {str(e)}"
                )],
                isError=True
            )

    async def list_tools(self) -> ListToolsResult:
        """列出所有可用工具"""
        return ListToolsResult(tools=self.tools)


async def main():
    """主函数：启动MCP服务器"""
    # 创建MCP服务器实例
    app = Server("amap-mcp-server")
    server = AmapMCPServer()

    # 注册工具列表处理器
    @app.list_tools()
    async def list_tools() -> List[Tool]:
        """列出所有可用工具"""
        return server.tools

    # 注册工具调用处理器
    @app.call_tool()
    async def call_tool(name: str, arguments: Dict) -> List[TextContent]:
        """处理工具调用"""
        result = await server.handle_tool_call(name, arguments)
        # 将ContentBlock列表转换为TextContent列表
        text_contents: List[TextContent] = []
        for item in result.content:
            if isinstance(item, TextContent):
                text_contents.append(item)
            elif hasattr(item, 'text'):
                # 只处理有text属性的TextContent类型
                text_attr = getattr(item, 'text', None)
                if isinstance(text_attr, str):
                    text_contents.append(TextContent(type="text", text=text_attr))
        return text_contents

    # 使用stdio传输运行服务器
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
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
    
    # 检查API密钥
    if not AMAP_API_KEY:
        print("警告: AMAP_API_KEY 环境变量未设置")
        print("请设置环境变量: export AMAP_API_KEY='你的高德API密钥'")
        print("或创建.env文件并添加: AMAP_API_KEY=你的高德API密钥")

    print("启动高德地图MCP服务器...")
    print(f"API密钥: {'已设置' if AMAP_API_KEY else '未设置'}")
    print("服务已启动，等待连接...")

    asyncio.run(main())