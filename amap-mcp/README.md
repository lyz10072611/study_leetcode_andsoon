# 高德地图 MCP 服务器

基于高德地图API的Model Context Protocol (MCP) 服务器实现，提供地理编码、路径规划、天气查询等功能。

## 功能特性

- 📍 **地理编码**：地址转坐标
- 🗺️ **逆地理编码**：坐标转地址
- 🚗 **路径规划**：驾车、步行、公交路径规划
- 🌤️ **天气查询**：实时天气和天气预报
- 📍 **周边搜索**：搜索指定位置周边的POI点
- 🏙️ **行政区域查询**：查询行政区划信息
- 🌐 **IP定位**：根据IP地址获取地理位置
- 📍 **地理围栏**：查询坐标点与地理围栏的关系
- 🖼️ **静态地图**：生成指定位置的静态地图

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 运行服务器

```bash
cd amap-mcp
python server.py
```

服务器将以stdio模式运行，等待MCP客户端连接。

### 2. 使用客户端

#### 演示模式

```bash
python client.py --mode demo
```

#### 交互式模式

```bash
python client.py --mode interactive
```

在交互式模式下，可以使用以下命令：

- `help` - 显示帮助信息
- `list` - 列出所有可用工具
- `geocode <地址>` - 地理编码（地址转坐标）
- `regeo <坐标>` - 逆地理编码（坐标转地址，格式：经度,纬度）
- `weather <城市>` - 查询天气
- `route <起点> <终点>` - 驾车路径规划（格式：经度,纬度）
- `exit` - 退出

### 3. 在代码中使用客户端

```python
import asyncio
from client import AmapMCPClient

async def main():
    client = AmapMCPClient()
    
    # 连接服务器
    await client.connect()
    
    # 地理编码
    result = await client.geocode("北京市朝阳区阜通东大街6号")
    print(result["content"])
    
    # 天气查询
    result = await client.weather("北京")
    print(result["content"])
    
    # 断开连接
    await client.disconnect()

asyncio.run(main())
```

## 可用工具

### geocode
地理编码：将地址转换为经纬度坐标

**参数**：
- `address` (必需): 地址描述
- `city` (可选): 地址所在城市

**示例**：
```python
result = await client.geocode("北京市朝阳区阜通东大街6号")
```

### regeo_code
逆地理编码：将经纬度坐标转换为结构化地址

**参数**：
- `location` (必需): 经纬度坐标，格式：经度,纬度
- `radius` (可选): 搜索半径，单位：米，默认1000

**示例**：
```python
result = await client.regeo_code("116.397428,39.90923")
```

### driving_route
驾车路径规划：计算两点之间的驾车路线

**参数**：
- `origin` (必需): 起点坐标，格式：经度,纬度
- `destination` (必需): 终点坐标，格式：经度,纬度
- `strategy` (可选): 策略（0-速度优先，1-费用优先，2-距离优先，3-不走高速，4-躲避拥堵，5-多策略），默认0

**示例**：
```python
result = await client.driving_route(
    origin="116.397428,39.90923",
    destination="116.407428,39.91923"
)
```

### walking_route
步行路径规划：计算两点之间的步行路线

**参数**：
- `origin` (必需): 起点坐标，格式：经度,纬度
- `destination` (必需): 终点坐标，格式：经度,纬度

### transit_route
公交路径规划：计算两点之间的公共交通路线

**参数**：
- `origin` (必需): 起点坐标，格式：经度,纬度
- `destination` (必需): 终点坐标，格式：经度,纬度
- `city` (必需): 城市代码/城市名称
- `cityd` (可选): 目的地城市代码

### weather
天气查询：获取指定城市的天气信息

**参数**：
- `city` (必需): 城市编码或名称
- `extensions` (可选): 气象类型（base-实况天气，all-预报天气），默认base

**示例**：
```python
result = await client.weather("北京", extensions="all")
```

### ip_location
IP定位：根据IP地址获取地理位置信息

**参数**：
- `ip` (可选): IP地址，为空时使用请求IP

### district_search
行政区域查询：查询行政区划信息

**参数**：
- `keywords` (必需): 查询关键字
- `subdistrict` (可选): 子级行政区（0-不返回，1-返回下一级，2-返回下两级），默认1
- `page` (可选): 页数，默认1
- `offset` (可选): 每页记录数，默认20

### around_place
周边搜索：搜索指定位置周边的POI点

**参数**：
- `location` (必需): 中心点坐标，格式：经度,纬度
- `keywords` (可选): 关键词
- `types` (可选): POI类型代码
- `radius` (可选): 搜索半径，单位：米，默认3000
- `page` (可选): 页数，默认1
- `offset` (可选): 每页记录数，默认20

### geofence_status
地理围栏状态查询：查询坐标点与地理围栏的关系

**参数**：
- `locations` (必需): 经纬度坐标，多个用'|'分隔
- `diu` (可选): 设备唯一标识

### static_map
静态地图：生成指定位置的静态地图

**参数**：
- `location` (必需): 中心点坐标，格式：经度,纬度
- `zoom` (可选): 缩放级别（1-17），默认10
- `size` (可选): 图片尺寸，格式：宽*高，默认400 * 300
- `markers` (可选): 标记点
- `paths` (可选): 路径
- `labels` (可选): 标签

## 配置

### API密钥

在 `server.py` 中配置高德地图API密钥：

```python
AMAP_API_KEY = "你的高德API密钥"
```

或者使用环境变量：

```bash
export AMAP_API_KEY="你的高德API密钥"
```

## 文件结构

```
amap-mcp/
├── server.py          # MCP服务器实现
├── client.py          # MCP客户端实现
├── requirements.txt   # 依赖列表
└── README.md          # 使用说明
```

## 注意事项

1. 需要高德地图API密钥才能使用
2. 服务器以stdio模式运行，需要通过MCP客户端连接
3. 某些功能可能需要特定的API权限

## 许可证

MIT License

