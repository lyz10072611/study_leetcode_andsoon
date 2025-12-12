# FastMCP 学习 Demo 项目

这个项目是一个完整的 FastMCP 学习教程，包含了从基础到高级的各种示例，帮助你快速掌握 FastMCP 技术。

## 项目结构

```
fastmcp_learning_demo/
├── README.md                 # 项目说明
├── requirements.txt          # 依赖包
├── basic_server.py          # 基础服务器示例
├── advanced_server.py       # 高级功能示例
├── calculator_server.py     # 计算器工具示例
├── resource_server.py       # 资源管理示例
├── client_demo.py          # 客户端调用示例
├── image_server.py         # 图片处理示例
├── test_client.py          # 测试客户端
└── run_all.py              # 一键运行所有示例
```

## 安装依赖

```bash
pip install fastmcp
# 或者使用 uv
uv pip install fastmcp
```

## 快速开始

### 1. 运行基础服务器
```bash
python basic_server.py
```

### 2. 运行高级服务器
```bash
python advanced_server.py
```

### 3. 运行客户端测试
```bash
python test_client.py
```

## 学习路径

1. **基础入门** - 从 `basic_server.py` 开始，了解 FastMCP 的基本概念
2. **工具开发** - 学习 `calculator_server.py` 中的各种工具定义
3. **资源管理** - 掌握 `resource_server.py` 中的资源暴露方法
4. **高级功能** - 探索 `advanced_server.py` 的异步处理和复杂功能
5. **客户端调用** - 通过 `client_demo.py` 学习如何调用 MCP 服务
6. **实际应用** - 参考 `image_server.py` 了解图片处理等实际应用

## 核心概念

### Tools（工具）
- LLM 可以执行的操作
- 类似 API 的 POST 端点
- 用于执行代码或产生副作用

### Resources（资源）
- 提供给 LLM 的数据
- 类似 API 的 GET 端点
- 用于加载信息到 LLM 上下文中

### Prompts（提示）
- 可复用的交互模板
- 指导 LLM 更高效地使用工具

## 更多资源

- [FastMCP 官方文档](https://fastmcp.wiki/zh/getting-started/welcome)
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)

## 注意事项

- 确保 Python 版本 >= 3.8
- 某些示例可能需要额外的依赖包
- 运行前请检查端口是否被占用
