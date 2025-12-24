# 快速启动指南

## 1. 安装依赖

```bash
cd langchain_demo
pip install -r requirements.txt
```

## 2. 配置API密钥

编辑 `config.py` 文件，修改以下配置：

```python
# 百炼平台配置（必需）
BAILIAN_API_KEY = "sk-your-actual-api-key"  # 替换为你的实际API密钥

# ASR和TTS配置（可选，如果使用真实服务）
ASR_API_URL = "https://your-asr-service.com/api"
ASR_API_KEY = "your-asr-key"

TTS_API_URL = "https://your-tts-service.com/api"
TTS_API_KEY = "your-tts-key"
```

## 3. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8000` 启动。

## 4. 测试服务

### 方式一：使用测试客户端

```bash
python test_client.py
```

### 方式二：使用curl

```bash
# 健康检查
curl http://localhost:8000/health

# 文本聊天
curl -X POST "http://localhost:8000/api/chat/text" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=你好&user_id=test_user"

# 测试工具调用
curl -X POST "http://localhost:8000/api/chat/text" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=请帮我测试一下工具&user_id=test_user"

# 计算器工具
curl -X POST "http://localhost:8000/api/chat/text" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=帮我计算25乘以36&user_id=test_user"
```

### 方式三：访问API文档

打开浏览器访问：`http://localhost:8000/docs`

这里可以看到完整的API文档和交互式测试界面。

## 5. 使用语音接口

### 语音聊天（返回文本）

```bash
curl -X POST "http://localhost:8000/api/chat/voice-text" \
  -F "audio=@your_audio_file.wav" \
  -F "user_id=test_user"
```

### 语音聊天（返回音频）

```bash
curl -X POST "http://localhost:8000/api/chat/voice" \
  -F "audio=@your_audio_file.wav" \
  -F "user_id=test_user" \
  --output response.wav
```

## 注意事项

1. **ASR/TTS服务**: 当前默认使用模拟服务（MockASRService 和 MockTTSService）。如需使用真实服务，请在 `main.py` 中修改：

```python
# 改为真实服务
asr_service = ASRService()
tts_service = TTSService()
```

2. **API密钥**: 确保 `config.py` 中的 `BAILIAN_API_KEY` 已设置为有效的百炼平台API密钥。

3. **模型选择**: 默认使用 `qwen2.5-72b-instruct`，可以根据需要修改为其他模型（如 `qwen-plus`、`qwen-turbo` 等）。

## 常见问题

### Q: 服务启动失败，提示导入错误？
A: 确保在 `langchain_demo` 目录下运行，或使用 `python -m langchain_demo.main`。

### Q: API调用返回错误？
A: 检查API密钥是否正确，网络连接是否正常，以及百炼平台服务是否可用。

### Q: 语音识别/合成不工作？
A: 当前使用模拟服务，返回固定内容。如需真实功能，请配置真实的ASR/TTS服务。

