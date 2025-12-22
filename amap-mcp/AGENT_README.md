# 高德地图智能Agent

基于百炼平台Qwen2.5模型和LangChain框架构建的智能地图助手，集成高德地图MCP服务。

## 功能特性

- 🤖 **智能对话**：使用百炼平台Qwen2.5模型进行自然语言理解
- 🗺️ **地图服务**：集成高德地图MCP客户端，提供完整的地图功能
- 🔧 **工具集成**：将MCP工具无缝集成到LangChain Agent中
- 💬 **交互式对话**：支持多轮对话和上下文理解

## 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖包括：
- `langchain` - LangChain框架
- `langchain-tongyi` - 百炼平台（通义千问）集成
- `dashscope` - 百炼平台SDK
- `mcp` - Model Context Protocol
- `aiohttp` - 异步HTTP客户端
- `nest-asyncio` - 异步事件循环支持

## 配置

### 1. 设置百炼平台API密钥

```bash
export DASHSCOPE_API_KEY="你的百炼平台API密钥"
```

或在代码中设置：
```python
import os
os.environ["DASHSCOPE_API_KEY"] = "你的API密钥"
```

### 2. 确保MCP服务器可用

确保 `server.py` 可以正常运行，Agent会自动连接MCP服务器。

## 使用方法

### 基本使用

```python
import asyncio
from agent import AmapAgent

async def main():
    # 创建Agent
    agent = AmapAgent(
        api_key="你的DASHSCOPE_API_KEY",
        model_name="qwen-turbo"  # 或 "qwen-plus", "qwen-max" 等
    )
    
    # 初始化（连接MCP服务器）
    await agent.initialize()
    
    # 运行查询
    response = await agent.run("北京今天天气怎么样？")
    print(response)
    
    # 清理资源
    await agent.cleanup()

asyncio.run(main())
```

### 交互式使用

直接运行 `agent.py`：

```bash
python agent.py
```

然后可以输入问题，例如：
- "北京今天天气怎么样？"
- "帮我查一下北京市朝阳区阜通东大街6号的坐标"
- "从天安门到故宫怎么走？"
- "天安门附近有什么餐馆？"

### 同步使用

```python
from agent import AmapAgent

# 创建Agent
agent = AmapAgent(api_key="你的API密钥")
await agent.initialize()

# 同步运行
response = agent.run_sync("查询北京的天气")
print(response)

await agent.cleanup()
```

## 可用工具

Agent集成了以下高德地图工具：

1. **geocode** - 地理编码（地址转坐标）
2. **regeo_code** - 逆地理编码（坐标转地址）
3. **driving_route** - 驾车路径规划
4. **walking_route** - 步行路径规划
5. **transit_route** - 公交路径规划
6. **weather** - 天气查询
7. **ip_location** - IP定位
8. **district_search** - 行政区域查询
9. **around_place** - 周边搜索

## 示例对话

```
你: 北京今天天气怎么样？
助手: 正在查询北京天气...
      [调用weather工具]
      北京今天天气：霾，温度3°C，南风≤3级，湿度63%

你: 帮我查一下天安门的坐标
助手: 正在查询天安门坐标...
      [调用geocode工具]
      天安门坐标：116.397428,39.90923

你: 从天安门到故宫怎么走？
助手: 正在规划路径...
      [调用geocode工具获取起点坐标]
      [调用geocode工具获取终点坐标]
      [调用walking_route工具]
      从天安门到故宫的步行路线：...
```

## 模型配置

支持百炼平台的以下模型：
- `qwen-turbo` - 快速响应（默认）
- `qwen-plus` - 平衡性能
- `qwen-max` - 最强性能

可以在创建Agent时指定：

```python
agent = AmapAgent(
    api_key="你的API密钥",
    model_name="qwen-plus",
    temperature=0.7,  # 创造性，0-1之间
    max_tokens=2000   # 最大输出长度
)
```

## 注意事项

1. **API密钥**：需要同时配置百炼平台API密钥和高德地图API密钥
2. **MCP服务器**：Agent会自动启动MCP服务器，确保server.py可正常运行
3. **异步处理**：工具调用会自动处理异步/同步转换
4. **错误处理**：Agent包含完善的错误处理机制

## 故障排除

### 1. 导入错误

如果遇到 `langchain_tongyi` 导入错误：
```bash
pip install langchain-tongyi dashscope
```

### 2. MCP连接失败

确保：
- `server.py` 文件存在且可执行
- 高德地图API密钥已配置
- Python环境中有所有必需的依赖

### 3. 模型调用失败

检查：
- `DASHSCOPE_API_KEY` 环境变量是否正确设置
- API密钥是否有效
- 网络连接是否正常

## 架构说明

```
用户查询
    ↓
LangChain Agent (Qwen2.5)
    ↓
工具选择与调用
    ↓
MCP Tool Wrapper
    ↓
MCP Client
    ↓
MCP Server (stdio)
    ↓
高德地图API
    ↓
返回结果
```

## 开发扩展

### 添加新工具

1. 在 `MCPToolWrapper` 类中添加新的工具方法
2. 在 `create_tools()` 方法中注册新工具
3. Agent会自动识别并使用新工具

### 自定义提示词

修改 `AmapAgent._create_agent()` 方法中的 `system_prompt` 来自定义Agent的行为。

## 许可证

MIT License

