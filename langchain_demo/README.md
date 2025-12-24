# 语音聊天机器人

基于 LangChain 架构的语音聊天机器人，支持语音输入和语音输出。

## 功能特性

- 🎤 **语音识别 (ASR)**: 使用在线 ASR 模型将语音转换为文本
- 🤖 **智能对话**: 基于 LangChain Agent 和百炼平台 Qwen2.5 模型的智能对话
- 🛠️ **工具调用**: 支持工具调用，包括测试工具和计算器工具
- 🔊 **语音合成 (TTS)**: 使用在线 TTS 模型将文本转换为语音
- 🚀 **FastAPI 服务**: 提供 RESTful API 接口

## 项目结构

```
langchai[travel-agent](../travel-agent)n_demo/
├── config.py          # 配置文件（API密钥、服务地址等）
├── asr_tts.py         # ASR和TTS服务封装
├── tools.py           # LangChain工具定义
├── agent.py           # 语音聊天机器人Agent
├── main.py            # FastAPI服务主文件
├── requirements.txt   # 依赖包列表
└── README.md          # 项目说明文档
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

编辑 `config.py` 文件，配置以下参数：

1. **百炼平台配置**:
   - `BAILIAN_API_KEY`: 百炼平台API密钥（已硬编码，可修改）
   - `BAILIAN_BASE_URL`: API基础URL
   - `QWEN_MODEL`: 使用的模型名称（默认：qwen2.5-72b-instruct）

2. **ASR服务配置**:
   - `ASR_API_URL`: ASR服务API地址
   - `ASR_API_KEY`: ASR服务API密钥

3. **TTS服务配置**:
   - `TTS_API_URL`: TTS服务API地址
   - `TTS_API_KEY`: TTS服务API密钥

## 运行服务

```bash
python main.py
```

服务将在 `http://0.0.0.0:8000` 启动。

## API接口

### 1. 健康检查

```bash
GET /health
```

### 2. 文本聊天

```bash
POST /api/chat/text
Content-Type: application/x-www-form-urlencoded

text=你好&user_id=user123
```

### 3. 语音聊天（返回音频）

```bash
POST /api/chat/voice
Content-Type: multipart/form-data

audio: [音频文件]
user_id: user123 (可选)
```

### 4. 语音聊天（返回文本）

```bash
POST /api/chat/voice-text
Content-Type: multipart/form-data

audio: [音频文件]
user_id: user123 (可选)
```

### 5. 获取对话历史

```bash
GET /api/history?user_id=user123
```

### 6. 清空对话历史

```bash
DELETE /api/history
```

## 工具说明

### 测试工具 (test_tool)

用于测试 agent 的工具调用功能。当用户询问测试相关问题时，agent 会调用此工具。

### 计算器工具 (calculator)

执行基本的数学计算，支持加法、减法、乘法、除法等运算。

## 使用示例

### Python 客户端示例

```python
import httpx
import asyncio

async def test_text_chat():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/chat/text",
            data={"text": "你好，请帮我测试一下工具", "user_id": "test_user"}
        )
        print(response.json())

async def test_voice_chat():
    async with httpx.AsyncClient() as client:
        with open("test_audio.wav", "rb") as f:
            files = {"audio": ("test_audio.wav", f, "audio/wav")}
            data = {"user_id": "test_user"}
            response = await client.post(
                "http://localhost:8000/api/chat/voice-text",
                files=files,
                data=data
            )
            print(response.json())

asyncio.run(test_text_chat())
```

### cURL 示例

```bash
# 文本聊天
curl -X POST "http://localhost:8000/api/chat/text" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=你好&user_id=user123"

# 语音聊天（返回文本）
curl -X POST "http://localhost:8000/api/chat/voice-text" \
  -F "audio=@test_audio.wav" \
  -F "user_id=user123"
```

## 注意事项

1. **ASR/TTS服务**: 当前使用模拟服务（MockASRService 和 MockTTSService），如需使用真实服务，请在 `main.py` 中切换为 `ASRService()` 和 `TTSService()`，并配置相应的API地址和密钥。

2. **API密钥**: `config.py` 中的 API 密钥是硬编码的示例，请根据实际情况修改。

3. **音频格式**: 支持的音频格式取决于ASR服务的支持情况，常见格式包括 wav、mp3、m4a 等。

4. **模型配置**: 默认使用 qwen2.5-72b-instruct 模型，可以根据需要修改为其他模型。

## 开发说明

### 添加新工具

在 `tools.py` 中定义新工具：

```python
class MyToolInput(BaseModel):
    param: str = Field(description="参数说明")

class MyTool(BaseTool):
    name: str = "my_tool"
    description: str = "工具描述"
    args_schema: Type[BaseModel] = MyToolInput
    
    def _run(self, param: str) -> str:
        # 实现工具逻辑
        return "结果"
    
    async def _arun(self, param: str) -> str:
        return self._run(param)
```

然后在 `get_all_tools()` 函数中添加新工具。

## 许可证

MIT License

