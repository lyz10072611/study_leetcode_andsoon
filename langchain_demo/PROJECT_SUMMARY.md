# LangChain 语音聊天机器人项目总结

## 项目概述

基于 LangChain 1.0.0+ 架构的语音聊天机器人，支持语音输入和语音输出。

## 核心特性

✅ **LangChain 1.0.0+ 兼容**: 使用最新版 LangChain SDK，确保版本 >= 1.0.0  
✅ **ASR 工具封装**: 将语音转文本功能封装为 LangChain tool，可在 agent 中调用  
✅ **TTS 工具封装**: 将文本转语音功能封装为 LangChain tool，可在 agent 中调用  
✅ **百炼平台集成**: 使用百炼平台的 qwen2.5 作为 LLM，ASR 和 TTS 服务  
✅ **FastAPI 服务**: 提供完整的 HTTP API 接口  

## 项目结构

```
langchain_demo/
├── config.py          # 配置文件（包含硬编码的 API key）
├── asr_tts.py         # ASR 和 TTS 服务封装
├── tools.py           # LangChain 工具定义（ASR、TTS、测试工具、计算器）
├── agent.py           # LangChain Agent（使用最新版 API）
├── main.py            # FastAPI 服务主文件
├── requirements.txt   # 依赖包（LangChain >= 1.0.0）
├── INSTALL.md         # 安装说明
└── PROJECT_SUMMARY.md # 项目总结（本文件）
```

## 关键实现

### 1. ASR 和 TTS 工具封装

在 `tools.py` 中，使用 `@tool` 装饰器将 ASR 和 TTS 封装为 LangChain 工具：

```python
@tool
async def asr_tool(audio_data_base64: str, audio_format: str = "wav") -> str:
    """语音转文本工具"""
    # ... 实现代码

@tool
async def tts_tool(text: str, voice: Optional[str] = None) -> str:
    """文本转语音工具"""
    # ... 实现代码
```

这些工具可以在 agent 中被自动调用。

### 2. LangChain 1.0.0+ 兼容性

在 `agent.py` 中实现了多层次的导入兼容性：

```python
# 优先尝试标准导入
try:
    from langchain.agents import create_openai_tools_agent, AgentExecutor
except ImportError:
    # 备用导入方案
    ...
```

### 3. 百炼平台集成

- **LLM**: 使用 `ChatOpenAI` 兼容接口，配置百炼平台的 base_url
- **ASR**: 使用百炼平台的语音识别 API
- **TTS**: 使用百炼平台的语音合成 API

## 配置说明

在 `config.py` 中硬编码了 API key：

```python
BAILIAN_API_KEY = "sk-your-api-key-here"  # 请替换为您的实际 API Key
```

## 使用方法

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

编辑 `config.py`，将 `BAILIAN_API_KEY` 替换为您的实际 API Key。

### 3. 启动服务

```bash
python main.py
```

或使用 uvicorn：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. API 接口

- **文本聊天**: `POST /api/chat/text`
- **语音聊天**: `POST /api/chat/voice`
- **语音转文本**: `POST /api/chat/voice-text`
- **对话历史**: `GET /api/history`
- **清空历史**: `DELETE /api/history`

## 版本要求

- **Python**: >= 3.8
- **LangChain**: >= 1.0.0
- **langchain-core**: >= 1.0.0
- **langchain-openai**: >= 1.0.0
- **langchain-community**: >= 1.0.0
- **langchain-agents**: >= 1.0.0 (如果可用)

## 注意事项

1. **版本兼容性**: 确保所有 LangChain 相关包版本 >= 1.0.0，避免版本冲突
2. **API Key**: 需要在 `config.py` 中配置百炼平台的 API Key
3. **工具调用**: ASR 和 TTS 工具可以在 agent 中自动调用，无需手动处理
4. **异步支持**: 所有工具都支持异步调用

## 测试工具

项目中包含两个测试工具：
- **test_tool**: 用于测试 agent 的工具调用功能
- **calculator**: 用于执行数学计算

这些工具可以帮助验证 agent 的工具调用机制是否正常工作。

